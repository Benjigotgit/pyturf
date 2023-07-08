def geom_reduce(geojson, callback, initial_value=None):
    previous_value = initial_value

    def reduce_func(current_geometry, feature_index, properties, bbox, id):
        nonlocal previous_value
        if feature_index == 0 and initial_value is None:
            previous_value = current_geometry
        else:
            previous_value = callback(previous_value, current_geometry)

    geom_each(geojson, reduce_func)
    return previous_value


def geom_each(geojson, callback):
    """
    applies callback to all geometries in a FeatureCollection
    (including geometries in Geometry collections)
    """
    is_feature_collection = geojson["type"] == "FeatureCollection"
    is_feature = geojson["type"] == "Feature"
    feature_loop_count = 1 if is_feature else len(geojson["features"])

    # This logic may look a little weird. The reason why it is that way
    # is because it's trying to be fast. GeoJSON supports multiple kinds
    # of objects at its root: FeatureCollection, Features, Geometries.
    # This function has the responsibility of handling all of them, and that
    # means that some of the `for` loops you see below actually just don't apply
    # to certain inputs. For instance, if you give this just a
    # Point geometry, then both loops are short-circuited and all we do
    # is gradually rename the input until it's called 'geometry'.
    #
    # This also aims to allocate as few resources as possible: just a
    # few numbers and booleans, rather than any temporary arrays as would
    # be required with the normalization approach.

    for feat_idx in range(feature_loop_count):
        if is_feature_collection:
            geometry = geojson["features"][feat_idx]["geometry"]
            properties = geojson["features"][feat_idx].get("properties", {})
            bbox = geojson["features"][feat_idx].get("bbox", None)
            id = geojson["features"][feat_idx].get("id", None)
        elif is_feature:
            geometry = geojson["geometry"]
            properties = geojson.get("properties", {})
            bbox = geojson.get("bbox", None)
            id = geojson.get("id", None)

        is_geom_collection = geometry["type"] == "GeometryCollection"
        geometry_loop_count = (
            1 if not is_geom_collection else len(geometry["geometries"])
        )

        for geom_idx in range(geometry_loop_count):
            feature_geom = (
                geometry if not is_geom_collection else geometry["geometries"][geom_idx]
            )

            if not feature_geom:
                if callback(None, feat_idx, properties, bbox, id) == False:
                    return False
                continue

            if feature_geom["type"] in [
                "Point",
                "LineString",
                "MultiPoint",
                "Polygon",
                "MultiLineString",
                "MultiPolygon",
            ]:
                if callback(geometry, feat_idx, properties, bbox, id) == False:
                    return False
                break

            elif feature_geom["type"] == "GeometryCollection":
                for geom_col_idx in range(len(geometry["geometries"])):
                    if (
                        not callback(
                            geometry["geometries"][geom_col_idx],
                            feat_idx,
                            properties,
                            bbox,
                            id,
                        )
                        == False
                    ):
                        return False
                    break
            else:
                raise ValueError("Unknown Geometry Type")


def coord_each(geojson, callback, exclude_wrap_coord=False):
    if geojson is None:
        raise ValueError("Coord Each Geojson is None")

    is_feature_collection = geojson["type"] == "FeatureCollection"
    is_feature = geojson["type"] == "Feature"
    feature_loop_count = 1 if is_feature else len(geojson["features"])
    coord_index = 0

    for feat_idx in range(feature_loop_count):
        if is_feature_collection:
            geometry = geojson["features"][feat_idx]["geometry"]
        elif is_feature:
            geometry = geojson["geometry"]

        is_geom_collection = geometry["type"] == "GeometryCollection"
        geometry_loop_count = (
            1 if not is_geom_collection else len(geometry["geometries"])
        )

        for geom_idx in range(geometry_loop_count):
            multifeat_idx = geom_idx = 0
            if is_geom_collection:
                feature_geom = geometry["geometries"][geom_idx]
            else:
                feature_geom = geometry

            if feature_geom is None:
                raise ValueError("Coord Each Geojson is None")

            coords = feature_geom["coordinates"]
            geom_type = feature_geom["type"]

            wrap_shrink = (
                1
                if exclude_wrap_coord and geom_type in ["Polygon", "MultiPolygon"]
                else 0
            )

            if geom_type == "Point":
                cb = callback(coords, coord_index, feat_idx, multifeat_idx, geom_idx)
                if cb == False:
                    return False
                coord_index += 1
                multifeat_idx += 1

            elif geom_type == "LineString" or geom_type == "MultiPoint":
                for i in range(len(coords)):
                    cb = callback(
                        coords[i], coord_index, feat_idx, multifeat_idx, geom_idx
                    )
                    if cb == False:
                        return False
                    coord_index += 1
                    if geom_type == "MultiPoint":
                        multifeat_idx += 1
                if geom_type == "LineString":
                    multifeat_idx += 1
                break

            elif geom_type == "Polygon" or geom_type == "MultiLineString":
                for i in range(len(coords)):
                    for j in range(coords[i] - wrap_shrink):
                        cb = callback(
                            coords[i][j], coord_index, feat_idx, multifeat_idx, geom_idx
                        )
                        if cb == False:
                            return False
                        coord_index += 1

                    if geom_type == "MultiLineString":
                        multifeat_idx += 1
                    if geom_type == "Polygon":
                        geom_idx += 1

                if geom_type == "Polygon":
                    multifeat_idx += 1
                break

            elif geom_type == "MultiPolygon":
                for i in range(len(coords)):
                    for j in range(coords[i]):
                        for k in range(coords[i][j] - wrap_shrink):
                            cb = callback(
                                coords[i][j][k],
                                coord_index,
                                feat_idx,
                                multifeat_idx,
                                geom_idx,
                            )
                            if cb == False:
                                return False
                            coord_index += 1
                        geom_idx += 1
                    multifeat_idx += 1
                break

            elif geom_type == "MultiPolygon":
                for i in range(len(feature_geom["geometries"])):
                    ce = coord_each(
                        feature_geom["geometries"][i], callback, exclude_wrap_coord
                    )
                    if ce == False:
                        return False
                break
            else:
                raise ValueError("Unknown geometry type")
