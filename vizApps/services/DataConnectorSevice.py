from sudBoard.settings import BASE_URL
import requests
import pandas, json
import geopandas as gpd
from cartopy import crs as ccrs
from pyproj import CRS
from shapely import wkt
import pyepsg

from vizApps.services.JossoSessionService import JossoSession

LIMIT_PARAM = 100

GEOMLABEL = [
    'geom',
    'geometry',
    'geometrie',
    'geometries'
]



crsRgnc = ccrs.LambertConformal(central_longitude=166,
                                standard_parallels=(-20.66666666666667, -22.33333333333333),
                                central_latitude=-21.5,
                                false_easting=400000,
                                false_northing=300000,
                                cutoff=0,
                                globe=ccrs.Globe(ellipse='GRS80'))

#epsg3163 = pyepsg.get(3163)
#proj4jRGNC = epsg3163.as_proj4().strip()
#bound =  epsg3163.domain_of_validity()
#proj4CRS = CRS.from_proj4(proj4jRGNC)

class ConnectorInterface():
    instances = []

    def __init__(self, json):
        self.id = json["connector-id"]
        self.data = None
        ConnectorInterface.instances.append(self)
        if(json["connector"]=="RestApi"):
            self.connector = PsudRestApi(json['url'],json['extraParams'])
        elif (json["connector"] == "Database"):
            self.connector = PsudDatabase(json['db'])

    @classmethod
    def get(cls, jsonParams):
        id = jsonParams["connector-id"]
        instance = [inst for inst in cls.instances if inst.id == id]
        if len(instance) >= 1:
            return instance[0]  # on renvoit uniquement un objet
        return ConnectorInterface(jsonParams)

    def getData(self, force=False):
        if force==True:
             self.data = self.connector.getDataFromUrlPandaDataframe(self.connector.endPointUrl,
                                                                    self.connector.extraParams)

        if isinstance(self.data, pandas.DataFrame) or isinstance(self.data, gpd.GeoDataFrame) :
            if self.data.empty:
                self.data = self.connector.getDataFromUrlPandaDataframe(self.connector.endPointUrl,
                                                                        self.connector.extraParams)
            else:
                return self.data

        if self.data != None:
            return self.data
        else:
            self.data = self.connector.getDataFromUrlPandaDataframe(self.connector.endPointUrl,
                                                                self.connector.extraParams)
        return self.data


    def refreshData(self):
        return self.getData(self, force=True)


    def getIsGeo(self,data):
       return self.connector.getIsGeo(data)

    def getLabelGeom(self,data):
       return self.connector.getLabelGeom(data)


class PsudRestApi():
    baseUrl = BASE_URL.__getitem__(1)[1]
    endPointUrl =""
    extraParams=""
    jossoSession = JossoSession()

    def __init__(self, url,extraParams):
        self.jossoSession = JossoSession()
        self.endPointUrl = url
        self.extraParams = extraParams

    def getDataFromUrlPandaDataframe(self,url,extraParams):
        #on récupère les meta data à partir d'une seul entité
        extraParams.append('limit=1')
        result = requests.get(self.baseUrl + url + "?_responseMode=json&"+ '&'.join(extraParams), cookies=self.jossoSession.cookies, headers=self.jossoSession.headers)

        if result.status_code==200:
            jsonResult =json.loads(result.text)
            nbEntity = jsonResult['total']
            print(nbEntity)

        else:
            print("on a un problème Huston")
            raise Exception('PsudRestApi Error','Data')

        # on supprime le parametre limit et en fonction du nombre total de donnée on va paginer nos requetes pour pas killer le serveur.
        extraParams.pop()

        data = pandas.DataFrame()
        if (nbEntity < LIMIT_PARAM):
            data = self.makeRequest(url,extraParams)

        else:
            modulo = nbEntity%LIMIT_PARAM
            nbOfRequest = int((nbEntity-modulo)/LIMIT_PARAM)
            limitParam = 'limit=' + str(LIMIT_PARAM)

            extraParams.append(limitParam)

            nbEntity = 10

            for i in range(0,nbEntity,LIMIT_PARAM):
               extraParams.append('start='+str(i))
               df = self.makeRequest(url,extraParams)

               if (data.size==0):
                   data = df
               else:
                   data = data.append(df)
               print(data.head())

               extraParams.pop()

        if self.getIsGeo(data):
            data = self.transformToGeoDf(data)

        self.data = data
        return self.data

    def makeRequest(self,url,extraParams):
        result = requests.get(self.baseUrl + url + "?_responseMode=json&" + '&'.join(extraParams),
                                  cookies=self.jossoSession.cookies, headers=self.jossoSession.headers)
        jsonResult = json.loads(result.text)
        dataFrame = pandas.json_normalize(jsonResult['data'])
        return dataFrame

    def paginatedRequest(self,url,extraParams):
        resultPage = self.makeRequest(url,extraParams)
        return resultPage

    def getIsGeo(self,df):
        for g in GEOMLABEL:
            if g.casefold() in set(df):
                return True

    def getLabelGeom(self, df):
        for g in GEOMLABEL:
            if g.casefold() in set(df):
             return g

    def isDataFrameHasGeom(self,df):
        if("geom" in set(df)):
            return "geom"
        elif("geometry" in set(df)):
            return "geometry"
        elif("geometrie" in set(df)):
            return "geometrie"
        elif("geometries" in set(df)):
            return "geometries"
        else:
            return False

    def getMetaGeomFromDataFrame(self, serie):

        meta = serie.head(1).to_string(index=False)
        metaList = meta.split('(')
        epsg = metaList[0].split('@')[0].strip()
        geom = metaList[0].split('@')[1].strip()
        return [("EPSG",epsg),("Geometry",geom)]

    def cleanGeomWKT(self,df,meta, labelGeom):
        epsg = meta[0][1]
        geomType = meta[1][1]
        stringToReplace = epsg + '@' + geomType + ' '
        newStringMeta = geomType
        df[labelGeom] = df[labelGeom].str.replace(str(stringToReplace),str(newStringMeta))

        df.rename(columns={labelGeom:'geometry'}, inplace=True)
        return df

    def transformToGeoDf(self,data,toEpsg="EPSG:3857"):

        labelGeom = self.getLabelGeom(data)
        #on recupère l'EPSG

        metaGeom = self.getMetaGeomFromDataFrame(data[labelGeom])
        #epsg = "epsg:" + metaGeom[0][1]
        # on clean la geom pour avoir un WKT
        data = self.cleanGeomWKT(df=data, meta=metaGeom, labelGeom=labelGeom)
        labelGeom = "geometry"  # maintenant c'est geometry pour etre compatible avec la classe GeomDictInterface
        data[labelGeom] = data[labelGeom].apply(wkt.loads)
        crs_proj4 = crsRgnc.proj4_init
        data = gpd.GeoDataFrame(data, geometry=labelGeom, crs=crs_proj4)

        return data.to_crs(toEpsg)


class PsudGeoCat():
    def __init__(self):
        return

class PsudDatabase():
    def __init__(self, dataBaseConnection):
        return

class csvFile():
    def __init__(self):
        return
