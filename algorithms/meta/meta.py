def geomReduce(geojson, callback, initial_value):
    previous_value = initial_value

    def reduce_func(current_geometry, feature_index, properties, bbox, id):
        if feature_index == 0 and initial_value is None:
            previous_value = current_geometry
        else:
            previous_value = callback(
                previous_value, current_geometry, feature_index, properties, bbox, id
            )

    geom_each(geojson, reduce_func)
    return previous_value


def geom_each(geojson, callback):
    """
    applies callback to all geometries in a FeatureCollection
    (including geometries in Geometry collections)
    """

    isFeatureCollection = (geojson["type"] == "FeatureCollection",)
    isFeature = (geojson["type"] == "Feature",)
    feature_loop_count = 1 if isFeature else len(geojson["features"])

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
        if isFeatureCollection:
            geometry = geojson["features"][feat_idx]["geometry"]
            properties = geojson["features"][feat_idx].get("properties", {})
            bbox = geojson["features"][feat_idx].get("bbox", None)
            id = geojson["features"][feat_idx].get("id", None)
        elif isFeature:
            geometry = geojson["geometry"]
            properties = geojson.get("properties", {})
            bbox = geojson.get("bbox", None)
            id = geojson.get("id", None)

        isGeometryCollection = geometry["type"] == "GeometryCollection"
        geometry_loop_count = 1 if isGeometryCollection else len(geometry["geometries"])

        def callback_executor(geom):
            return callback(geom, feat_idx, properties, bbox, id)

        for geom_idx in range(geometry_loop_count):
            feature_geom = (
                geometry
                if not isGeometryCollection
                else geometry["geometries"][geom_idx]
            )

            if not feature_geom:
                if not callback_executor(None):
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
                if not callback_executor(geometry):
                    return False
                break

            elif feature_geom["type"] == "GeometryCollection":
                for geom_col_idx in range(len(geometry["geometries"])):
                    if not callback_executor(geometry["geometries"][geom_col_idx]):
                        return False
                    break
            else:
                raise ValueError("Unknown Geometry Type")
