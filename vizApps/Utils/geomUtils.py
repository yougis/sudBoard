
GEOMLABEL = [
    'geom',
    'geometry',
    'geometrie',
    'geometries'
]

from cartopy import crs as ccrs
from shapely import wkt
import geopandas as gpd
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
        for g in GEOMLABEL:
            if g.casefold() in set(dataframe):
                return True

    def getLabelGeom(self, dataframe):
        for g in GEOMLABEL:
            if g.casefold() in set(dataframe):
                return g

    def isDataFrameHasGeom(self, df):
        if ("geom" in set(df)):
            return "geom"
        elif ("geometry" in set(df)):
            return "geometry"
        elif ("geometrie" in set(df)):
            return "geometrie"
        elif ("geometries" in set(df)):
            return "geometries"
        else:
            return False

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

        labelGeom = GeomUtil.getLabelGeom(self,dataframe=dataframe)
        # on recupère l'EPSG

        metaGeom = GeomUtil.getMetaGeomFromDataFrame(self,serie=dataframe[labelGeom])
        # epsg = "epsg:" + metaGeom[0][1]
        # on clean la geom pour avoir un WKT
        data = GeomUtil.cleanGeomWKT(self,df=dataframe, meta=metaGeom, labelGeom=labelGeom)
        labelGeom = "geometry"  # maintenant c'est geometry pour etre compatible avec la classe GeomDictInterface
        data[labelGeom] = data[labelGeom].apply(wkt.loads)
        crs_proj4 = crsRgnc.proj4_init
        data = gpd.GeoDataFrame(data, geometry=labelGeom, crs=crs_proj4)

        return data.to_crs(toEpsg)

    def transformGdfToDf(self, dataframe):
        dataframe =  pd.DataFrame(dataframe.drop(columns=self.labelGeom))
        return dataframe