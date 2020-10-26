import vizApps.services.DataConnectorSevice as connector

from  shapely.geometry  import GeometryCollection, Point, Polygon, LineString, LinearRing, MultiPoint, MultiPolygon, MultiLineString
import  numpy as np

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
import spatialpandas as spd
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

    def getLabelGeom(self, dataframe):
        eval = [el for el in list(dataframe) if el.casefold() in GEOMLABEL]
        if len(eval) > 0:
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

    def createEmptyGeomShapelyFromWktType(self, typeViz):

        switcher = {
            'POINT': Point(),
            'MULTIPOINT': MultiPoint(),
            'LINESTRING' : LineString(),
            'POLYGON': Polygon(),
            'MULTIPOLYGON': MultiPolygon(),
            'MULTILINESTRING': MultiLineString(),
            'GEOMETRYCOLLECTION' : GeometryCollection()
        }
        return switcher.get(typeViz, None)

    def switchGeom(self, geomType):
        geomType
        return self.switchGeom(geomType)

    def transformGdfToDf(self, dataframe):
        dataframe =  pd.DataFrame(dataframe.drop(columns=self.labelGeom))
        return dataframe