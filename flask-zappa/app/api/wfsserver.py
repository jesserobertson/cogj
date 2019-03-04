from flask import request
from bs4 import BeautifulSoup

from api.exceptions import GeoServerlessException
from api.gml import GeoJSON2GML
from api.utils import make_dict_keys_uppercase, get_env

from urllib import parse
from copy import deepcopy


class WFSServer:
    def __init__(self, service_info=None):
        self.url_root = request.url_root
        self.service_info = service_info
        self.max_features_per_page = int(get_env("MAX_FEATURES_PER_PAGE"))

    def make_wfs_safe_layername(self, filename):
        # https://lists.osgeo.org/pipermail/mapserver-dev/2015-July/014506.html
        # Name must start with either a letter or underscore (_) and may contain only letters, digits, underscores (_), hyphens (-), and periods (.).
        # FIXME Implement a regex to check that the name is valid and either fix it (best) or reject it (easiest) if it fails these strict checks.
        return filename.lower()

    def get_capabilities(self, metadata, bbox):
        with open("api/templates/getcapabilities_2.0.0.xml") as f:
            soup = BeautifulSoup(f.read(), features="lxml-xml")
            feature_type_list = soup.find("FeatureTypeList")

            with open("api/templates/featuretype_2.0.0.xml") as f:
                feature_type_soup = BeautifulSoup(f.read(), features="lxml-xml")

                feature_type_soup.find("Name").string = self.make_wfs_safe_layername(metadata["name"])
                feature_type_soup.find("Title").string = metadata["title"]
                feature_type_soup.find("Abstract").string = metadata["abstract"]
                feature_type_soup.find("LowerCorner").string = "{} {}".format(bbox[1], bbox[0])
                feature_type_soup.find("UpperCorner").string = "{} {}".format(bbox[3], bbox[2])

                feature_type_list.append(feature_type_soup)

            title = soup.find("ServiceIdentification").find("Title")
            title.string = self.service_info["SERVICE_TITLE"]

            default_value = soup.find("Constraint", {"name": "CountDefault"}).find("DefaultValue")
            default_value.string = str(self.max_features_per_page)

            operations_metadata = soup.find("OperationsMetadata")
            for op in operations_metadata.findAll("Operation"):
                get = op.find("Get")
                get["xlink:href"] = "{}?COGJ_URL={}".format(self.url_root, parse.quote(self.service_info["COGJ_URL"]))

            return str(soup)

    def describe_feature_type(self, type_name, gs):
        feature_collection = gs.read_feature_collections([gs.find_smallest_collection()])
        first_feature = feature_collection["features"][0]

        with open("api/templates/describefeaturetype_2.0.0.xml") as f:
            soup = BeautifulSoup(f.read(), features="lxml-xml")
            sequence = soup.find("xsd:sequence")

            with open("api/templates/element_2.0.0.xml") as f:
                element_xml_template = f.read()

                for prop, val in first_feature["properties"].items():
                    element_xml = BeautifulSoup(element_xml_template, features="lxml-xml").find("xsd:element")
                    element_xml["name"] = prop
                    sequence.append(element_xml)

            return str(soup)

    def get_feature(self, type_name, geojson_feature_collection, bbox, start_feature, feature_count, total_features, result_type_hits):
        def __write_envelope_gml(bbox, soup):
            minx, miny = bbox[0]
            maxx, maxy = bbox[1]

            lower_corner = soup.find("gml:lowerCorner")
            lower_corner.string = "{} {}".format(miny, minx)

            upper_corner = soup.find("gml:upperCorner")
            upper_corner.string = "{} {}".format(maxy, maxx)

        def __has_next_page(start_feature, features_in_response, total_features):
            return (start_feature + features_in_response) < total_features

        def __get_next_page_url(start_feature, features_in_response):
            scheme, netloc, path, query_string, fragment = parse.urlsplit(request.url)
            query_params = make_dict_keys_uppercase(parse.parse_qs(query_string))

            query_params["STARTINDEX"] = start_feature + features_in_response
            if "COUNT" not in query_params:
                query_params["COUNT"] = self.max_features_per_page

            new_query_string = parse.urlencode(query_params)
            return parse.urlunsplit((scheme, netloc, path, new_query_string, fragment))

        def __has_previous_page(start_feature):
            return start_feature > 0

        def __get_previous_page_url(start_feature, feature_count):
            scheme, netloc, path, query_string, fragment = parse.urlsplit(request.url)
            query_params = make_dict_keys_uppercase(parse.parse_qs(query_string))

            query_params["STARTINDEX"] = start_feature - feature_count
            if "COUNT" not in query_params:
                query_params["COUNT"] = self.max_features_per_page

            new_query_string = parse.urlencode(query_params, doseq=True)
            return parse.urlunsplit((scheme, netloc, path, new_query_string, fragment))

        with open("api/templates/getfeature_2.0.0.xml") as f:
            soup = BeautifulSoup(f.read(), features="lxml-xml")

        geojson2GML = GeoJSON2GML(type_name, geojson_feature_collection)

        # Convert features and write to in memory GML collection
        if result_type_hits is False:
            featureMembers = soup.find("gml:featureMembers")
            for xml in geojson2GML.convert():
                featureMembers.append(xml)
            print(">>> # of featureMembers", len(featureMembers))

            # Write the bounding box containing all features into GML
            bbox = geojson2GML.get_features_bbox()
            __write_envelope_gml(bbox, soup)

        # Support paging features and returning resultType=hits
        featureCollection = soup.find("wfs:FeatureCollection")

        if result_type_hits is False:
            featureCollection["numberMatched"] = total_features
            featureCollection["numberReturned"] = len(featureMembers)

            if __has_next_page(start_feature, len(featureMembers), total_features) is True:
                featureCollection["next"] = __get_next_page_url(start_feature, len(geojson_feature_collection["features"]))

            if __has_previous_page(start_feature):
                featureCollection["previous"] = __get_previous_page_url(start_feature, feature_count)

        else:
            featureCollection["numberMatched"] = total_features
            featureCollection["numberReturned"] = 0
            soup.find("gml:boundedBy").decompose()
            soup.find("gml:featureMembers").decompose()

        return str(soup.find("wfs:FeatureCollection"))
