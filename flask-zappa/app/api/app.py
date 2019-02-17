from flask import Flask, Response, abort

from api.wfsserver import WFSServer
from api.geo_serverless import Geo_Serverless
from api.utils import get_request_arg_casei

app = Flask(__name__)


@app.route("/")
def wfs():
    r = get_request_arg_casei("REQUEST")
    COGJ_URL = get_request_arg_casei("COGJ_URL")
    if COGJ_URL is None:
        return Response()

    wfs_server = WFSServer({
        "SERVICE_TITLE": "COGJ Web Feature Service",
        "COGJ_URL": COGJ_URL
    })
    geo_serverless = Geo_Serverless(COGJ_URL)

    if r.upper() == "GETCAPABILITIES":
        return get_capabilities(wfs_server, geo_serverless)
    elif r.upper() == "DESCRIBEFEATURETYPE":
        return describe_feature_type(wfs_server, geo_serverless)
    elif r.upper() == "GETFEATURE":
        return get_feature(wfs_server, geo_serverless)

    abort(404)


def get_capabilities(wfs_server, geo_serverless):
    return Response(wfs_server.get_capabilities(geo_serverless.get_metadata(), geo_serverless.get_bbox()), mimetype="text/xml")


def describe_feature_type(wfs_server, geo_serverless):
    return Response(wfs_server.describe_feature_type(get_request_arg_casei("TYPENAME"), geo_serverless), mimetype="text/xml")


def get_feature(wfs_server, geo_serverless):
    bbox = get_request_arg_casei("BBOX")
    feature_collections = geo_serverless.read_feature_collections(geo_serverless.get_collections_for_bbox(bbox))

    gml_path = wfs_server.get_feature(get_request_arg_casei("TYPENAME"), feature_collections, bbox)
    with open(gml_path) as f:
        return Response(f.read(), mimetype="text/xml; subtype=gml/3.1.1")
