import vizApps.services.DataConnectorSevice as connector
from vizApps.Utils.dataUtils import DataUtils

from  shapely.geometry  import GeometryCollection, Point, Polygon, LineString, LinearRing, MultiPoint, MultiPolygon, MultiLineString
import  numpy as np

import geoviews as gv


POINT = ['Point','point[int64]','multipoint[int64]']
POLYGONE = ['Polygon','MultiPolygon', 'polygon[int64]','multipolygon[int64]']
MULTIPOLYGONE = 'MultiPolygon'
MULTILINESTRING = 'MultiLineString'
LINESTRING = ['LineString','MultiLineString','MultiLine','line[int64]','multiline[int64]']
GEOMETRYCOLLECTION =['GeometryCollection']

STRONG_SIMPLIFY = 500.0
SOFT_SIMPLIFY = 50.0


GEOMLABEL = [
    'geom',
    'geometry',
    'geometrie',
    'geometries',
    'geomwktcollection'
]

from cartopy import crs as ccrs
from shapely import wkt, wkb
import geopandas as gpd
#import spatialpandas as spd
import pandas as pd


crsRgnc = ccrs.LambertConformal(central_longitude=166,
                                standard_parallels=(-20.66666666666667, -22.33333333333333),
                                central_latitude=-21.5,
                                false_easting=400000,
                                false_northing=300000,
                                cutoff=0,
                                globe=ccrs.Globe(ellipse='GRS80'))



class  GeomUtil():
    def __init__(self):
        pass

    def getIsGeo(self, dataframe):
        if len([el for el in list(dataframe) if el.casefold() in GEOMLABEL]) > 0:
            return True

    @classmethod
    def getLabelGeom(cls,dataframe):
        eval = [el for el in list(dataframe) if el.casefold() in GEOMLABEL]
        if len(eval) > 0:
            dataframe.labelGeom = eval[0]
            return eval[0]

    def getMetaGeomFromDataFrame(self, serie):

        meta = serie.head(1).to_string(index=False)
        metaList = meta.split('(')
        epsg = metaList[0].split('@')[0].strip()
        geom = metaList[0].split('@')[1].strip()
        return [("EPSG", epsg), ("Geometry", geom)]

    def cleanGeomWKT(self, df, meta, labelGeom):
        epsg = meta[0][1]
        geomType = meta[1][1]
        stringToReplace = epsg + '@' + geomType + ' '
        newStringMeta = geomType
        df[labelGeom] = df[labelGeom].str.replace(str(stringToReplace), str(newStringMeta))


        df.rename(columns={labelGeom: 'geometry'}, inplace=True)
        return df


    def transformToGeoDf(self, dataframe, toEpsg="EPSG:3857"):

        # self is ConnectorInterface

        labelGeom = GeomUtil.getLabelGeom(self,dataframe=dataframe)
        crs_proj4 = crsRgnc.proj4_init

        if self.connectorType == connector.DATABASE:
            #dataframe[labelGeom] = dataframe[labelGeom].apply(lambda x: hex(int(x, 16)))
            dataframe[labelGeom] = dataframe[labelGeom].apply(lambda x: wkb.loads(x,True))

            # maintenant c'est geometry pour etre compatible avec la classe GeomDictInterface de shapely pour la reprojection
            dataframe.rename(columns={labelGeom: 'geometry'}, inplace=True)
            labelGeom = "geometry"

            data = gpd.GeoDataFrame(dataframe, geometry=labelGeom, crs=crs_proj4)
        else:

            # on recupère l'EPSG

            # on cherche les meta sur une geom on filtre le dataframe pour n'avoir que les data avec des geom
            geomSerie = dataframe[~dataframe[labelGeom].isnull()]

            metaGeom = GeomUtil.getMetaGeomFromDataFrame(self,serie=geomSerie[labelGeom])
            # epsg = "epsg:" + metaGeom[0][1]
            # on clean la geom pour avoir un WKT
            data = GeomUtil.cleanGeomWKT(self,df=dataframe, meta=metaGeom, labelGeom=labelGeom)
            labelGeom = "geometry"  # maintenant c'est geometry pour etre compatible avec la classe GeomDictInterface



            data[labelGeom] = data[labelGeom].apply(lambda x: wkt.loads(x) if x != None and not pd.isnull(x) else np.nan )

            data = gpd.GeoDataFrame(data, geometry=labelGeom, crs=crs_proj4)


            # on remplace les valeur vide par des geometries vides

            geomType = metaGeom[1][1]
            emptyShapelyGeom = GeomUtil.createEmptyGeomShapelyFromWktType(self, geomType)
            data[labelGeom] = data[labelGeom].apply(lambda x:  emptyShapelyGeom if not x else x )

            # on ne prend que les données dont la geom n'est pas vide
            data = data[~data.is_empty]


        # conversion en spatialPandas
        # data = spd.GeoDataFrame(data)
        return data.to_crs(toEpsg)

    def gdfToEmptyGeom(self, data):
        labelGeom = GeomUtil.getLabelGeom(self,data)
        emptyShapelyGeom = GeomUtil.createEmptyGeomShapelyFromWktType(self, data.geom_type.unique()[0])
        data[labelGeom] = data[labelGeom].apply(lambda x: emptyShapelyGeom )
        return data

    def convertGeomToCentroid(self, data):
        labelGeom = GeomUtil.getLabelGeom(self, data)
        data[labelGeom] = data[labelGeom].apply(lambda x: x.centroid)
        return data

    def createEmptyGeomShapelyFromWktType(self, geomType):

        switcher = {
            'POINT': Point(),
            'MULTIPOINT': MultiPoint(),
            'LINESTRING' : LineString(),
            'POLYGON': Polygon(),
            'MULTIPOLYGON': MultiPolygon(),
            'MULTILINESTRING': MultiLineString(),
            'GEOMETRYCOLLECTION' : GeometryCollection()
        }
        return switcher.get(geomType.upper(), None)


    def transformGdfToDf(self, dataframe):
        labelGeom = self.labelGeom
        if not labelGeom:
            labelGeom = GeomUtil.getLabelGeom(self, dataframe)
        dataframe =  pd.DataFrame(dataframe.drop(columns=labelGeom))

        dataframe = DataUtils.dataCleaner(self, dataframe)

        listColumnToIntType = dataframe.select_dtypes('int64')

        for col in listColumnToIntType:
            dataframe[col] = dataframe[col].astype(int)

        return dataframe


    def getGeoElementFromData(self, data,vdims=None):

        arrayGeomType = data.geom_type.unique()

        for geomType in arrayGeomType:

            data = data[data['geometry'].apply(lambda x: x.geom_type == geomType)]

            if geomType in POINT:
                geomNdOverlay = gv.Points(data, vdims=vdims,crs=ccrs.GOOGLE_MERCATOR,  group=POINT[0])


            elif geomType in LINESTRING:
                data['geometry'] = data.simplify(SOFT_SIMPLIFY, True)
                geomNdOverlay = gv.Path(data, vdims=vdims,crs=ccrs.GOOGLE_MERCATOR, group=LINESTRING[0])

            elif geomType in MULTILINESTRING:
                data['geometry'] = data.simplify(SOFT_SIMPLIFY, True)
                geomNdOverlay = gv.Path(data, vdims=vdims, crs=ccrs.GOOGLE_MERCATOR,
                                        group=MULTILINESTRING[0])
            elif geomType in POLYGONE:
                data['geometry'] = data.simplify(STRONG_SIMPLIFY, True)
                geomNdOverlay = gv.Polygons(data, vdims=vdims, crs=ccrs.GOOGLE_MERCATOR,  group=POLYGONE[0])

            elif geomType in MULTIPOLYGONE:
                data['geometry'] = data.simplify(STRONG_SIMPLIFY, True)
                geomNdOverlay = gv.Polygons(data, vdims=vdims, crs=ccrs.GOOGLE_MERCATOR,
                                            group=MULTIPOLYGONE[0])
            elif geomType in GEOMETRYCOLLECTION:
                data = data.explode()
                geomNdOverlay = GeomUtil.getGeoElementFromData(self,data=data)
            else:
                return None

        return geomNdOverlay.opts(tools=['hover', 'tap'])