""" file:    reproject.py (spatial)
    author:  Jess Robertson, @jesserobertson
    date:    Sunday, 27 January 2019

    description: Reprojection algorithms for shapely geometries
"""

from functools import partial

from shapely.geometry import Polygon, MultiPolygon, MultiLineString, \
    LineString, LinearRing, Point, MultiPoint
import pyproj
import numpy as np

from cogj import Feature, FeatureCollection

GEOJSON_PROJ = 'EPSG:4326'  # Default/only projection used by GeoJSON

def get_projector(from_crs, to_crs=None):
    """
    Return a function to reproject something from one
    coordinate reference system (CRS) to another.

    Coordinate references can be specified as PROJ strings
    (e.g. '+datum=WGS84 +ellps=WGS84 +no_defs +proj=longlat'
    see fiona.crs.to_string for more on this) or using EPSG
    codes (e.g. 'epsg:3857').

    Parameters:
        from_crs - the source coordinate reference system
        to_crs - the destination coordinate reference system.
            Optiona, defaults to 'epsg:4326' which is Web
            Mercator projection (to make it easy to pass to
            leaflet maps)
    """
    # Generate pyproj objects from our CRSes
    prjs = [from_crs, to_crs or GEOJSON_PROJ]
    for idx, prj in enumerate(prjs):
        if isinstance(prj, str) and prj.lower().startswith('epsg'):
            prjs[idx] = pyproj.Proj(init=prj)
        else:
            prjs[idx] = pyproj.Proj(prj)

    # Generate the function to actually carry out the transforms
    if prjs[0] == prjs[1]:
        _project = lambda *p: p
    else:
        _project = lambda *p: np.asarray(list(partial(pyproj.transform, *prjs)(*p)))
    return _project

def reproject(geom, from_crs=None, to_crs=None, projector=None):
    """
    Reproject a shapely {Multi,}Polygon or {Multi,}LineString
    using a given projector (see `get_projector`).

    Parameters:
        geom - the geometry to reproject
        from_crs - the source coordinate reference system
        to_crs - the destination coordinate reference system.
            Optional, defaults to 'epsg:4326' which is Web
            Mercator projection (to make it easy to pass to
            leaflet maps)

    Returns:
        the reprojected geometries
    """
    # Handle inputs
    from_crs = from_crs or GEOJSON_PROJ
    to_crs = to_crs or GEOJSON_PROJ
    if projector is None:
        projector = get_projector(from_crs, to_crs)

    # Handle different geometry types
    mapping = {
        'Polygon': _polygon,
        'LineString': _linestring,
        'MultiPolygon': _multipolygon,
        'LinearRing': _linearring,
        'MultiLineString': _multilinestring,
        'Point': _point,
        'MultiPoint': _multipoint,
        'Feature': _feature,
        'FeatureCollection': _featurecollection
    }
    try:
        return mapping[geom.geom_type](geom, projector=projector)
    except KeyError:
        msg = "Don't know how to reproject a {}".format(geom.geom_type)
        raise ValueError(msg)

# Reprojection helpers
def _featurecollection(geom, projector):
    return FeatureCollection([
        reproject(f, projector=projector)
        for f in geom
    ])

def _feature(geom, projector):
    return Feature(
        geometry=reproject(geom.geometry, projector=projector),
        properties=geom.properties
    )

def _point(geom, projector):
    return Point(projector(*geom.xy))

def _multipoint(geom, projector):
    return MultiPoint([_point(p, projector) for p in geom])

def _polygon(geom, projector):
    if geom.interiors:
        reproj = Polygon(
            shell=_linearring(geom.exterior, projector),
            holes=[_linearring(i, projector) for i in geom.interiors]
        )
    else:
        reproj = Polygon(reproject(geom.exterior, projector=projector))
    return reproj

def _linestring(geom, projector):
    return LineString(projector(*geom.xy).T)

def _linearring(geom, projector):
    return LinearRing(projector(*geom.coords.xy).T)

def _multipolygon(geom, projector):
    return MultiPolygon([_polygon(p, projector) for p in geom])

def _multilinestring(geom, projector):
    return MultiLineString([_linestring(p, projector) for p in geom])
