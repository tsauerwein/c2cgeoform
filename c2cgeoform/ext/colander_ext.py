
from colander import (null, Invalid)

from geoalchemy2 import WKBElement
from geoalchemy2.shape import to_shape, from_shape
from shapely.geometry import mapping, shape
from shapely.ops import transform
from functools import partial
import pyproj
import json


class Geometry(object):
    """
    """
    def __init__(self, geometry_type='GEOMETRY', srid=-1, map_srid=-1):
        self.geometry_type = geometry_type.upper()
        self.srid = int(srid)
        self.map_srid = int(map_srid)
        if self.map_srid == -1:
            self.map_srid = self.srid

        if self.srid != self.map_srid:
            self.project_db_to_map = partial(
                pyproj.transform,
                pyproj.Proj(init='epsg:' + str(self.srid)),
                pyproj.Proj(init='epsg:' + str(self.map_srid)))
            self.project_map_to_db = partial(
                pyproj.transform,
                pyproj.Proj(init='epsg:' + str(self.map_srid)),
                pyproj.Proj(init='epsg:' + str(self.srid)))

    def serialize(self, node, appstruct):
        """
        In Colander speak: Converts a Python data structure (an appstruct) into
        a serialization (a cstruct).
        Or: Converts a `WKBElement` into a GeoJSON string.
        """
        if appstruct is null:
            return null
        if isinstance(appstruct, WKBElement):
            geometry = to_shape(appstruct)
            if self.srid != self.map_srid and appstruct.srid != self.map_srid:
                geometry = transform(self.project_db_to_map, geometry)

            return json.dumps(mapping(geometry))
        raise Invalid(node, 'Unexpected value: %r' % appstruct)

    def deserialize(self, node, cstruct):
        """
        In Colander speak: Converts a serialized value (a cstruct) into a
        Python data structure (a appstruct).
        Or: Converts a GeoJSON string into a `WKBElement`.
        """
        if cstruct is null or cstruct == '':
            return null
        try:
            # TODO Shapely does not support loading GeometryCollections from
            # GeoJSON, see https://github.com/Toblerity/Shapely/issues/115
            geometry = shape(json.loads(cstruct))
        except Exception:
            raise Invalid(node, 'Invalid geometry: %r' % cstruct)

        if self.srid != self.map_srid:
            geometry = transform(self.project_map_to_db, geometry)

        return from_shape(geometry, srid=self.srid)

    def cstruct_children(self, node, cstruct):
        return []
