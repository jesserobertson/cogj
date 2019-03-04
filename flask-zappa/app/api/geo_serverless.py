import os
from urllib.parse import urlparse

import requests

from api.exceptions import GeoServerlessException
from api.utils import is_dev

# https://stackoverflow.com/q/40795709


class Point:

    def __init__(self, xcoord=0, ycoord=0):
        self.x = xcoord
        self.y = ycoord


class Rectangle:
    def __init__(self, bottom_left, top_right):
        self.bottom_left = bottom_left
        self.top_right = top_right

    def intersects(self, other):
        return not (self.top_right.x < other.bottom_left.x or self.bottom_left.x > other.top_right.x or self.top_right.y < other.bottom_left.y or self.bottom_left.y > other.top_right.y)


class Geo_Serverless:
    def __init__(self, COGJ_URL):
        if COGJ_URL is None:
            raise GeoServerlessException("COGJ_URL not provided.")

        self.COGJ_URL = COGJ_URL
        self.header = None

    def get_filename_from_url(self):
        return os.path.basename(urlparse(self.COGJ_URL).path)

    def read_header(self):
        if self.COGJ_URL is None:
            raise GeoServerlessException("No S3 URL configured")

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
        raise GeoServerlessException("COGJ file header doesn't contain 'bbox'")

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
            raise GeoServerlessException(e)

    def get_collections_for_bbox(self, bbox=None):
        if self.header is None:
            self.read_header()

        if bbox is None:
            return self.header["collections"]

        filter_bbox = Rectangle(Point(bbox[0], bbox[1]), Point(bbox[2], bbox[3]))

        filtered_collections = []
        for collection in self.header["collections"]:
            collection_bbox = Rectangle(Point(collection["bbox"][0], collection["bbox"][1]), Point(collection["bbox"][2], collection["bbox"][3]))

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

    def read_feature_collections(self, feature_collections, start_feature=0, feature_count=1):
        def __get_start_fc_idx(start_feature):
            if start_feature is None:
                return 0, 0

            feature_running_total = 0
            for idx, fc in enumerate(feature_collections):
                feature_running_total += fc["features"]

                if feature_running_total >= start_feature:
                    return idx, feature_running_total - fc["features"]
            raise GeoServerlessException("Unable to find a feature collection to start from for a start_feature of {}".format(start_feature))

        # def __get_finish_fc_idx(start_idx, start_feature, feature_count):
        #     feature_running_total = 0
        #     for idx, fc in enumerate(feature_collections[start_idx:]):
        #         feature_running_total += fc["features"]

        #         if feature_running_total >= (start_feature + feature_count):
        #             return idx + 1
        #     raise GeoServerlessException("Unable to find a feature collection to start from for a start_feature of {} and feature_count of {}".format(start_feature, feature_count))

        def __filter_required_feature_collections(feature_collections):
            start_idx, feature_running_total = __get_start_fc_idx(start_feature)
            return feature_collections[start_idx:], feature_running_total

        features = []
        fcf, feature_running_total = __filter_required_feature_collections(feature_collections)
        for idx, fc in enumerate(fcf):
            if "start" not in fc or "size" not in fc:
                raise GeoServerlessException("FeatureCollection missing 'start'/'size'")

            response = requests.get(self.COGJ_URL, headers={
                "Range": "bytes={start}-{end}".format(start=fc["start"], end=fc["start"] + fc["size"])
            })
            fc = response.json()

            if idx == 0:
                start_at = start_feature - feature_running_total
                features += fc["features"][start_at:]
            else:
                features += fc["features"]

            if len(features) >= feature_count:
                features = features[:feature_count]
                break

        return {
            "type": "FeatureCollection",
            "features": features
        }

    def get_total_features(self, feature_collections):
        return sum([fc["features"] for fc in feature_collections])
