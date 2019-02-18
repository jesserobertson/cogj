import os
import subprocess
from urllib.parse import quote
import json
from random import getrandbits

from flask import request
from lxml import objectify
from lxml.etree import parse, fromstring, tostring

from api.exceptions import GeoServerlessException
from api.utils import get_env, merge_dicts


class WFSServer:
    def __init__(self, service_info=None):
        self.url_root = request.url_root
        self.service_info = service_info
        pass

    def make_wfs_safe_layername(self, filename):
        # https://lists.osgeo.org/pipermail/mapserver-dev/2015-July/014506.html
        # Name must start with either a letter or underscore (_) and may contain only letters, digits, underscores (_), hyphens (-), and periods (.).
        # FIXME Implement a regex to check that the name is valid and either fix it (best) or reject it (easiest) if it fails these strict checks.
        return filename

    def get_capabilities(self, metadata, bbox):
        with open("api/templates/getcapabilities.xml") as f:
            root = objectify.parse(f).getroot()

            with open("api/templates/featuretype.xml") as f:
                featureTypeInfo = merge_dicts(
                    metadata,
                    {
                        "minx": bbox[0],
                        "miny": bbox[1],
                        "maxx": bbox[2],
                        "maxy": bbox[3],
                    },
                    {"name": self.make_wfs_safe_layername(metadata["name"])}
                )

                featureType = tostring(parse(f).getroot()).decode("utf-8")
                featureType = featureType.format(**featureTypeInfo)
                root.FeatureTypeList.append(fromstring(featureType))

            getCaps = tostring(root).decode("utf-8")
            getCaps = getCaps.format(
                **merge_dicts(self.service_info, {
                    "URL_ROOT": self.url_root,
                    "COGJ_URL": quote(self.service_info["COGJ_URL"])
                }))

            return getCaps

    def describe_feature_type(self, type_name, gs):
        fc = gs.read_feature_collections([gs.find_smallest_collection()])
        xsd_path = self.geojson_to_gml(type_name, fc).replace(".gml", ".xsd")

        with open(xsd_path) as f:
            return f.read()

    def get_feature(self, type_name, feature_collections, bbox=None):
        return self.geojson_to_gml(type_name, feature_collections, bbox)

    def geojson_to_gml(self, type_name, feature_collections, bbox=None):
        scratch_dir = "./scratch/{dir}".format(dir=str(getrandbits(128)))
        if not os.path.exists(scratch_dir):
            os.makedirs(scratch_dir)

        geojson_path = "{scratch_dir}/{type_name}.geojson".format(scratch_dir=scratch_dir, type_name=type_name)
        gml_path = "{scratch_dir}/{type_name}.gml".format(scratch_dir=scratch_dir, type_name=type_name)

        with open(geojson_path, "w") as f:
            json.dump(feature_collections, f)

        if bbox is not None:
            command = "ogr2ogr -f GML -dsco FORMAT=GML3 -clipsrc {bbox} {gml_path} {geojson_path}".format(bbox=bbox.replace(",", " "), geojson_path=geojson_path, gml_path=gml_path)
        else:
            command = "ogr2ogr -f GML -dsco FORMAT=GML3 {gml_path} {geojson_path}".format(geojson_path=geojson_path, gml_path=gml_path)

        p = subprocess.Popen(command.split(" "), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, err = p.communicate()

        if len(err) > 0:
            raise GeoServerlessException("Got error '{err}' whilst reading data".format(err=err))
        return gml_path
