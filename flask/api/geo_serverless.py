import requests
from shapely.geometry import box
import exceptions
from utils import is_dev
from urlparse import urlparse
import os


class Geo_Serverless:
    def __init__(self, COGJ_URL):
        if COGJ_URL is None:
            raise exceptions.GeoServerlessException("COGJ_URL not provided.")

        self.COGJ_URL = COGJ_URL
        self.header = None

    def get_filename_from_url(self):
        return os.path.basename(urlparse(self.COGJ_URL).path)

    def read_header(self):
        if self.COGJ_URL is None:
            raise exceptions.GeoServerlessException("No S3 URL configured")

        response = requests.get(self.COGJ_URL, headers={
            "Range": "bytes=0-9999"
        })
        self.header = response.json()

    def get_collections(self):
        if self.header is None:
            self.read_header()
        return self.header["collections"]

    def get_bbox(self):
        if self.header is None:
            self.read_header()

        if "bbox" in self.header:
            return self.header["bbox"]
        raise exceptions.GeoServerlessException("COGJ file header doesn't contain 'bbox'")

    def get_metadata(self):
        def build_abstract():
            abstract = ""
            if "description" in self.header:
                abstract = self.header["description"]

            if "version" in self.header:
                abstract += "Verison: {}.".format(self.header["version"])

            if "published" in self.header:
                abstract += "Published on: {}.".format(self.header["published"])
            return abstract

        if self.header is None:
            self.read_header()

        try:
            return {
                "name": self.get_filename_from_url(),
                "title": self.header["name"] if "name" in self.header else "Unmamed dataset", "abstract": build_abstract()
            }
        except Exception as e:
            raise exceptions.GeoServerlessException(e)

    # def get_bbox_from_data(self):
    #     bboxes = []
    #     for collection in self.get_collections():
    #         bboxes.append(box(*collection["bbox"]))

    #     return list(cascaded_union(bboxes).bounds)

    def get_collections_for_bbox(self, bbox=None):
        if self.header is None:
            self.read_header()

        if bbox is None:
            if is_dev() is True:
                return self.header["collections"][:1]
            else:
                return self.header["collections"]

        filter_bbox = box(*[float(i) for i in bbox.split(",")])
        filtered_collections = []
        for collection in self.header["collections"]:
            collection_bbox = box(*collection["bbox"])
            if filter_bbox.intersects(collection_bbox) is True:
                filtered_collections.append(collection)
        return filtered_collections

    def find_smallest_collection(self):
        smallest = None
        for collection in self.get_collections():
            if smallest is None:
                smallest = collection
            if collection["features"] < smallest["features"]:
                smallest = collection
        return smallest

    def read_feature_collections(self, collections):
        featureCollection = {
            "type": "FeatureCollection",
            "features": []
        }

        for collection in collections:
            if "start" not in collection or "size" not in collection:
                raise exceptions.GeoServerlessException("FeatureCollection missing 'start'/'size'")

            response = requests.get(self.COGJ_URL, headers={
                "Range": "bytes={start}-{end}".format(start=collection["start"], end=collection["start"] + collection["size"])
            })
            fc = response.json()
            featureCollection["features"] += fc["features"]

        return featureCollection
