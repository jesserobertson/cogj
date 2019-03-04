from bs4 import BeautifulSoup

from api.exceptions import GeoServerlessException


class GeoJSON2GML:
    def __init__(self, feature_type_name, geojson_feature_collection):
        # FIXME
        self.namespace = "test"
        self.feature_type_name = feature_type_name
        self.geojson_feature_collection = geojson_feature_collection
        # self.feature_id_incrementer = 1
        self.features_bbox = None

    def convert(self, limit=None):
        xml_elements = []
        all_bounding_box_coordinate_pairs = []
        # feature_xml_template = self.__get_feature_xml_template()

        for f in self.geojson_feature_collection["features"][:limit]:
            geometry = self.__get_geometry(f)

            # if geometry.is_supported() is False:
            #     # FIXME We don't support all types of geometry yet (e.g. donut polygons)
            #     print(">>> Skipping", f["geometry"]["type"])
            #     continue

            # coordinate_pairs = geometry.flatten_to_coordinate_pairs()
            # box = self.__bounding_box_from_coordinates(coordinate_pairs)
            # all_bounding_box_coordinate_pairs += box

            # soup = BeautifulSoup(feature_xml_template, features="lxml-xml")
            soup = geometry.create_feature_element()
            # self.__write_feature_envelope_gml(box, soup)
            # self.__write_feature_the_geom_gml(geometry, coordinate_pairs, soup)
            self.__write_feature_id_gml(soup, f)
            self.__write_feature_attributes(f, soup)
            xml_elements.append(soup.find(self.__get_feature_type_name()))

            all_bounding_box_coordinate_pairs += geometry.get_bounding_box()

        self.features_bbox = self.__bounding_box_from_coordinates(all_bounding_box_coordinate_pairs)
        return xml_elements

    def get_features_bbox(self):
        if self.features_bbox is not None:
            return self.features_bbox
        raise GeoServerlessException("Features bounding box hasn't been calculated yet.")

    def __get_feature_type_name(self):
        return "{}:{}".format(self.namespace, self.feature_type_name.lower())

    def __get_geometry(self, feature):
        if feature["geometry"]["type"] == "Polygon":
            return Polygon(feature, self.feature_type_name)
        elif feature["geometry"]["type"] == "MultiPolygon":
            return MultiPolygon(feature, self.feature_type_name)
        raise GeoServerlessException("Unable to determine geometry for feature: {}".format(str(feature)[:100]))

    # def __get_feature_xml_template(self):
    #     with open("api/templates/feature_polygon_2.0.0.xml") as f:
    #         return f.read()

    def __bounding_box_from_coordinates(self, points):
        x_coordinates, y_coordinates = zip(*points)
        return [(min(x_coordinates), min(y_coordinates)), (max(x_coordinates), max(y_coordinates))]

    def __get_feature_id(self, feature):
        possible_gid_names = ["fid", "gid", "oid", "objectid", "id"]
        for prop, value in feature["properties"].items():
            if prop.lower() in possible_gid_names:
                return value
        raise GeoServerlessException("Unable to find a unique feature id in the dataset. May be one of: {}".format(", ".join(possible_gid_names)))

    def __write_feature_id_gml(self, soup, feature):
        feature_type_name = self.__get_feature_type_name()
        feature_xml = soup.find("featureTypeName")
        feature_xml.name = feature_type_name
        feature_xml["gml:id"] = "{}.{}".format(feature_type_name, self.__get_feature_id(feature))

        # object_id = feature["properties"]["OBJECTID"]
        # feature_xml["gml:id"] = "{}.{}".format(feature_type_name, object_id)

    # def __write_feature_envelope_gml(self, bbox, soup):
    #     minx, miny = bbox[0]
    #     maxx, maxy = bbox[1]

    #     lower_corner = soup.find("gml:lowerCorner")
    #     lower_corner.string = "{} {}".format(minx, miny)

    #     upper_corner = soup.find("gml:upperCorner")
    #     upper_corner.string = "{} {}".format(maxx, maxy)

    # def __write_feature_the_geom_gml(self, geometry, coordinate_pairs, soup):
    #     pos_list = soup.find("gml:posList")
    #     coordinates = geometry.flatten_coordinate_pairs(coordinate_pairs)
    #     pos_list.string = " ".join(coordinates)

    def __write_feature_attributes(self, feature, soup):
        feature_xml = soup.find(self.__get_feature_type_name())

        for prop, val in feature["properties"].items():
            # if prop == "OBJECTID" and str(val) == "42595":
            #     print(">>> FOUND 42595!")

            new_tag = soup.new_tag("{}:{}".format(self.namespace, prop))
            new_tag.string = str(val) if val is not None else ""
            feature_xml.append(new_tag)


import itertools

def grouper(n, iterable, fillvalue=None):
    "grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return itertools.zip_longest(fillvalue=fillvalue, *args)
    
class Geometry:
    def __init__(self, feature, feature_type_name):
        self.feature = feature
        self.feature_type_name = feature_type_name

    # def is_supported(self):
    #     raise NotImplementedError

    def create_feature_element(self):
        raise NotImplementedError

    def get_bounding_box(self):
        raise NotImplementedError

    def flatten_to_coordinate_pairs(self):
        raise NotImplementedError

    def flatten_coordinate_pairs_to_string(self, coordinate_pairs):
        return " ".join([str(c) for cp in coordinate_pairs for c in cp])

    def bounding_box_from_coordinates(self, points):

        # print(">>> points", points)
        points = grouper(2, points)
        # print(">>> points", points)
        x_coordinates, y_coordinates = zip(*points)
        # print(">>> x_coordinates", x_coordinates)
        # print(">>> y_coordinates", y_coordinates)
        return [(min(x_coordinates), min(y_coordinates)), (max(x_coordinates), max(y_coordinates))]


class Polygon(Geometry):
    def __init__(self, feature, feature_type_name):
        super(Polygon, self).__init__(feature, feature_type_name)

        self.coordinate_pairs = None
        self.bbox = None

    # def is_supported(self):
    #     return True

    # def __is_simple_polygon(self):
    #     # FIXME Bodge bodge
    #     return isinstance(self.feature["geometry"]["coordinates"][0][0][0], float)

    def create_feature_element(self):
        coordinate_pairs = self.get_coordinate_pairs()
        bbox = self.get_bounding_box()

        feature_xml_template = self.get_feature_xml_template()
        soup = BeautifulSoup(feature_xml_template, features="lxml-xml")
        self.write_feature_envelope_gml(bbox, soup)

        # surface_member_xml_element = self.write_feature_the_geom_gml(coordinate_pairs, soup)
        # soup.find("gml:MultiSurface").append(surface_member_xml_element)
        # return soup

        surface_member_xml_element = self.write_feature_the_geom_gml(coordinate_pairs, soup)
        polygon = surface_member_xml_element.find("gml:Polygon")
        # print(surface_member_xml_element)
        # surface_member_xml_element.find("gml:surfaceMember").decompose()

        # polygon.append(surface_member_xml_element)
        the_geom = soup.find("test:the_geom")
        soup.find("gml:MultiSurface").decompose()

        the_geom.append(polygon)
        return soup

    def get_coordinate_pairs(self):
        if self.coordinate_pairs is None:
            self.coordinate_pairs = self.flatten_to_coordinate_pairs()
            # print(self.coordinate_pairs)
        return self.coordinate_pairs

    def get_bounding_box(self):
        if self.bbox is None:
            cp = self.get_coordinate_pairs()
            # print(">>> cp", cp)
            self.bbox = self.bounding_box_from_coordinates(cp)
        # print(">>> self.bbox", self.bbox)
        return self.bbox

    # def flatten_to_coordinate_pairs(self):
    #     return [c for c in self.feature["geometry"]["coordinates"][0]]

    def flatten_to_coordinate_pairs(self, coordinates=None):
        # return " ".join([str(c) for cp in coordinate_pairs for c in cp])
        # return [c for p in mp in self.feature["geometry"]["coordinates"] for c in p in mp]

        # import itertools
        # l = list(itertools.chain.from_iterable(self.feature["geometry"]["coordinates"]))

        if coordinates is None:
            coordinates = self.feature["geometry"]["coordinates"]

        from itertools import chain

        def flatten(L):
            if not hasattr(L, "__iter__"):
                return [L]
            else:
                return chain(*map(flatten, L))
        l = list(flatten(coordinates))

        # l = [[item for subsublist in sublist for item in subsublist] for sublist in self.feature["geometry"]["coordinates"]]

        # for foo in l:
        #     print(">>> foo")
        #     print(foo)
        # print("=============================")
        return l

    def get_feature_xml_template(self):
        with open("api/templates/feature_polygon_2.0.0.xml") as f:
            return f.read()

    def get_surfacemember_xml_template(self):
        with open("api/templates/surfacemember_gml_3.2.xml") as f:
            return f.read()

    def write_feature_envelope_gml(self, bbox, soup):
        minx, miny = bbox[0]
        maxx, maxy = bbox[1]

        lower_corner = soup.find("gml:lowerCorner")
        lower_corner.string = "{} {}".format(miny, minx)

        upper_corner = soup.find("gml:upperCorner")
        upper_corner.string = "{} {}".format(maxy, maxx)

    def write_feature_the_geom_gml(self, coordinate_pairs, soup):
        surfacemember_xml_template = self.get_surfacemember_xml_template()
        soup = BeautifulSoup(surfacemember_xml_template, features="lxml-xml").find("gml:surfaceMember")

        pos_list = soup.find("gml:posList")
        # pos_list.string = self.flatten_coordinate_pairs_to_string(coordinate_pairs)
        # print(coordinate_pairs)
        coordinate_pairs = grouper(2, coordinate_pairs)
        coordinate_pairs = [list(reversed(l)) for l in coordinate_pairs]
        coordinate_pairs = self.flatten_to_coordinate_pairs(coordinate_pairs)
        pos_list.string = " ".join([str(c) for c in coordinate_pairs])
        return soup


class MultiPolygon(Polygon):
    # def is_supported(self):
    #     return True

    def get_polygon_interior_xml_template(self):
        with open("api/templates/polygon_interior_gml_3.2.xml") as f:
            return f.read()

    def create_feature_element(self):
        coordinate_pairs = self.get_coordinate_pairs()
        bbox = self.get_bounding_box()

        feature_xml_template = self.get_feature_xml_template()
        soup = BeautifulSoup(feature_xml_template, features="lxml-xml")
        self.write_feature_envelope_gml(bbox, soup)
        # surface_member_xml_element = self.write_feature_the_geom_gml(coordinate_pairs, soup)
        multi_surface = soup.find("gml:MultiSurface")

        # object_id = self.feature["properties"]["OBJECTID"]
        # multi_surface["gml:id"] = "{}.{}.geom.0".format(self.feature_type_name, object_id)

        for surface_member_xml_element in self.write_feature_the_geom_gml(coordinate_pairs, soup):
            multi_surface.append(surface_member_xml_element)
        return soup

    def write_feature_the_geom_gml(self, coordinate_pairs, soup):
        xml_elements = []
        surfacemember_xml_template = self.get_surfacemember_xml_template()
        polygon_interior_xml_template = self.get_polygon_interior_xml_template()
        # from copy import deepcopy

        for idx, foo in enumerate(self.feature["geometry"]["coordinates"]):
            # print(">>> foo", len(foo), str(foo)[:100])
            # print(">>> level 1", len(foo), str(foo)[:100])
            # for foo2 in foo:
                # print(">>> level 2", len(foo2), str(foo2)[:100])
                # if isinstance(foo2[0][0], float) is False:
                #     for foo3 in foo2:
                #         print(">>> level 3", len(foo3), str(foo3)[:100])

            soup = BeautifulSoup(surfacemember_xml_template, features="lxml-xml").find("gml:surfaceMember")

            polygon = soup.find("gml:Polygon")
            # object_id = self.feature["properties"]["OBJECTID"]
            # polygon["gml:id"] = "{}.{}.geom.0.{}".format(self.feature_type_name, object_id, idx)

            pos_list = soup.find("gml:exterior").find("gml:posList")
            # print(">>> foo[0]", foo[0])
            foo[0] = [list(reversed(l)) for l in foo[0]]
            coordinate_pairs = self.flatten_to_coordinate_pairs(foo[0])
            # print(">>> coordinate_pairs", coordinate_pairs)
            # pos_list.string = self.flatten_coordinate_pairs_to_string(coordinate_pairs)
            pos_list.string = " ".join([str(c) for c in coordinate_pairs])

            # soup.find("gml:interior").decompose()
            # xml_elements.append(soup)

            if len(foo) > 1:
                for thing in foo[1:]:
                    interior_soup = BeautifulSoup(polygon_interior_xml_template, features="lxml-xml").find("gml:interior")
                    pos_list = interior_soup.find("gml:posList")
                    # print(">>> thing", thing)
                    thing = [list(reversed(l)) for l in thing]
                    # print(">>> thing", thing)
                    coordinate_pairs = self.flatten_to_coordinate_pairs(thing)
                    # print(">>> coordinate_pairs", coordinate_pairs)
                    # pos_list.string = self.flatten_coordinate_pairs_to_string(coordinate_pairs)
                    pos_list.string = " ".join([str(c) for c in coordinate_pairs])

                    soup.find("gml:Polygon").append(interior_soup)

            xml_elements.append(soup)

            # print("")

        # print(">>> coordinate_pairs", coordinate_pairs)

        # return soup
        return xml_elements

    def flatten_to_coordinate_pairs(self, coordinates=None):
        # return " ".join([str(c) for cp in coordinate_pairs for c in cp])
        # return [c for p in mp in self.feature["geometry"]["coordinates"] for c in p in mp]

        # import itertools
        # l = list(itertools.chain.from_iterable(self.feature["geometry"]["coordinates"]))

        if coordinates is None:
            coordinates = self.feature["geometry"]["coordinates"]

        from itertools import chain

        def flatten(L):
            if not hasattr(L, "__iter__"):
                return [L]
            else:
                return chain(*map(flatten, L))
        l = list(flatten(coordinates))

        # l = [[item for subsublist in sublist for item in subsublist] for sublist in self.feature["geometry"]["coordinates"]]

        # for foo in l:
        #     print(">>> foo")
        #     print(foo)
        # print("=============================")
        return l

    def get_coordinate_pairs(self):
        if self.coordinate_pairs is None:
            self.coordinate_pairs = self.flatten_to_coordinate_pairs()
            # print(">>> self.coordinate_pairs", self.coordinate_pairs)
        return self.coordinate_pairs

    # def get_bounding_box(self):
    #     if self.bbox is None:
    #         self.bbox = self.bounding_box_from_coordinates(self.get_coordinate_pairs())
    #     return self.bbox

    # def flatten_to_coordinate_pairs(self):
    #     # FIXME
    #     return [c for c in self.feature["geometry"]["coordinates"][0][0]]
