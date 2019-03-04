from flask import Flask, Response, abort

from api.wfsserver import WFSServer
from api.geo_serverless import Geo_Serverless
from api.utils import get_request_arg_casei, get_env

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
    def __get_bbox(bbox_param, srsname):
        if bbox_param is None:
            return None

        bbox = [float(i) for i in bbox_param.split(",")[:4]]

        if (srsname is not None and srsname.startswith("urn:")) or "urn:" in bbox_param:
            bbox = [bbox[1], bbox[0], bbox[3], bbox[2]]

        return bbox

    bbox = get_request_arg_casei("BBOX")
    srs_name = get_request_arg_casei("SRSNAME")
    start_index = get_request_arg_casei("STARTINDEX")
    count = get_request_arg_casei("COUNT")
    type_name = get_request_arg_casei("TYPENAMES")
    result_type = get_request_arg_casei("RESULTTYPE")
    result_type_hits = True if result_type is not None and result_type.lower() == "hits" else False

    start_feature = int(start_index) if start_index is not None else 0
    feature_count = int(count) if count is not None else int(get_env("MAX_FEATURES_PER_PAGE"))
    fc = geo_serverless.get_collections_for_bbox(__get_bbox(bbox, srs_name))
    total_features = geo_serverless.get_total_features(fc)

    geojson = geo_serverless.read_feature_collections(fc, start_feature, feature_count)
    print(">>> start_feature", start_feature)
    print(">>> feature_count", feature_count)
    print(">>> total_features", total_features)
    print(">>> # of features", len(geojson["features"]))

    gml = wfs_server.get_feature(type_name, geojson, bbox, start_feature, feature_count, total_features, result_type_hits)
    return Response(gml, mimetype="application/gml+xml; version=3.2")
