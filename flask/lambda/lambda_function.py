import os
import sys
import logging

# set up logger
logger = logging.getLogger(__file__)
logger.setLevel(logging.DEBUG)
# commented out to avoid duplicate logs in lambda
# logger.addHandler(logging.StreamHandler())

# imports used for the example code below
from osgeo import gdal, ogr

import json
import subprocess

def lambda_handler(event, context):
    """ Lambda handler """
    logger.debug(event)
    # print(event)

    # process event payload and do something like this
    # fname = event['filename']
    # fname = fname.replace('s3://', '/vsis3/')
    # # open and return metadata
    # ds = gdal.Open(fname)
    # band = ds.GetRasterBand(1)
    # stats = band.GetStatistics(0, 1)

    # geojsonFile = "./sample_data/Cadastral.firstcollection.geojson"
    geojsonFile = "./sample_data/Casatral.noformatting.geojson"
    # driver = ogr.GetDriverByName("GeoJSON")
    # dataSource = driver.Open(geojsonFile, 0)
    # layer = dataSource.GetLayer()

    # with open(geojsonFile) as f:
    #   featureCollection = json.loads(f.read())
    #   for feature in featureCollection["features"][:1]:
    #     feature = ogr.CreateGeometryFromJson(json.dumps(feature["geometry"]))

    basePath = "./"
    command = ["ogr2ogr", "--version"]
    # https://gis.stackexchange.com/a/154008
    foo = subprocess.check_call(command)
    # ogr2ogr -f "GML" -nlt "GEOMETRYCOLLECTION" ./sample_data/Cadastral.gml ./sample_data/Casatral.noformatting.geojson

    return None


if __name__ == "__main__":
    event = []
    context = []
    lambda_handler(event, context)