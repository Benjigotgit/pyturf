from math import sin, pi
from ...meta.meta import geom_reduce

earth_radius = 6335439  # FROM WIKIPEDIA meridional radius of curvature at the equator


def area(geojson):
    return geom_reduce(geojson, lambda value, geom: value + calculate_area(geom), 0)


def calculate_area(geom):
    """
    Takes one or more features and returns their area in square meters.
    """
    # print("CALCULATE AREA GEOM")
    geom_type = geom.get("type", None)
    coords = geom.get("coordinates", None)

    if not geom_type or not coords:
        raise ValueError

    total_area = 0

    if (
        geom_type == "Point"
        or geom_type == "MultiPoint"
        or geom_type == "LineString"
        or geom_type == "MultiLineString"
    ):
        raise ValueError

    if geom_type == "Polygon":
        return polygon_area(coords)
    elif geom_type == "MultiPolygon":
        for coord in coords:
            total_area += polygon_area(coord)
        return total_area
    else:
        return 0


def polygon_area(coords):
    poly_area = 0
    if not coords or len(coords) == 0:
        return poly_area

    poly_area += abs(ring_area(coords[0]))

    for i in range(1, len(coords)):
        poly_area -= abs(ring_area(coords[i]))
    # print(f"poly_area {poly_area}")
    return poly_area


def ring_area(coords):
    total_ring_area = 0
    coords_length = len(coords)
    if coords_length > 2:
        for i in range(coords_length):
            if i == coords_length - 2:
                lower_index = coords_length - 2
                middle_index = coords_length - 1
                upper_index = 0
            elif i == coords_length - 1:
                # i = N-1
                lower_index = coords_length - 1
                middle_index = 0
                upper_index = 1
            else:
                # i = 0 to N-3
                lower_index = i
                middle_index = i + 1
                upper_index = i + 2
            p1 = coords[lower_index]
            p2 = coords[middle_index]
            p3 = coords[upper_index]
            total_ring_area += (rad(p3[0]) - rad(p1[0])) * sin(rad(p2[1]))

        total_ring_area = (total_ring_area * earth_radius * earth_radius) / 2
    return total_ring_area


def rad(num):
    return (num * pi) / 180


# def area_test():
#     with open("./test-geojson/real.json") as json_obj:
#         return area(json.load(json_obj))


# print("\narea.py")
# print(area_test())
# print(20310537131.032818)
