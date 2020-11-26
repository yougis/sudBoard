from sudBoard.settings import BASE_URL
import requests
import pandas as pd
import json
import geopandas as gpd
from vizApps.Utils.dataUtils import DataUtils
from vizApps.Utils.geomUtils import GeomUtil

from sqlalchemy import create_engine

from sudBoard.settings import EXTERNE_DATABASES

from vizApps.services.JossoSessionService import JossoSession

# limit de nombre d'objet par requete
LIMIT_PARAM = 5000
SAMPLE_LIMIT = 100


REST_API = "Url"
DATABASE = "SQL"
FILE = "Fichier"

CONNECTOR_LIST = [(REST_API,"WEB - Application métier Province Sud"),
                  (DATABASE,"DB -Base de données interne à la Province Sud"),
                  (FILE,"Import de fichier (Xls, Csv, ShapeFile)")
                  ]


FULL = "FULL"
SAMPLE = "SAMPLE"

class ConnectorInterface():
    instances = []

    def __init__(self, json):
        self.jossoSession = JossoSession()
        self.id = json["connector-id"]
        self.data = pd.DataFrame()
        self.sample_data = pd.DataFrame()
        self.full_data = pd.DataFrame()
        self.sample_or_full_from_cache = None #SAMPLE or FULL
        self.sample = False
        self.no_cache = False
        self.caching_in_progress = False
        self.connectorType= json["connector"]
        self.message = None
        ConnectorInterface.instances.append(self)
        if (json["connector"] == REST_API ):
            self.connector = PsudRestApi(json['url'], json['extraParams'],self.jossoSession)
        elif (json["connector"] == DATABASE):
            self.connector = PsudDatabase(json['db'], json['table'], json['whereClause'],self.jossoSession)

    def configureConnector(self,sampleOrFull):
        print("Configuration du connector Interface en mode {}".format(sampleOrFull))
        if sampleOrFull == SAMPLE:
            self.toSampleOnly()
        elif sampleOrFull == FULL:
            self.toFullData()

    @classmethod
    def get(cls, jsonParams):
        id = jsonParams["connector-id"]
        instance = [inst for inst in cls.instances if inst.id == id]
        if len(instance) >= 1:
            return instance[0]  # on renvoit uniquement un objet
        return ConnectorInterface(jsonParams)

    def isDataInCache(self):
        if self.sample_or_full_from_cache == SAMPLE and not self.sample_data.empty:
            return True
        elif self.sample_or_full_from_cache == FULL and not self.full_data.empty:
            return True
        else:
            return False

    def lookCachedData(self):
        if self.isDataInCache():
             self.data = self.returnSampleOrFullData()
             return self.data
        else:
            self.message = 'Pas de données {} en cache pour le type de demande'.format(self.sample_or_full_from_cache)
            print(self.message)
            return None

    def returnSampleOrFullData(self):
        data = {
            SAMPLE: self.sample_data,
            FULL : self.full_data
        }
        return data.get(self.sample_or_full_from_cache)

    def getData(self):
        self.message = "Loading des données -- ", "connecteur :", self.connectorType, "mode Sample: ", self.sample
        print(self.message)

        data = self.connector.getData(self.sample)

        if data is None :
            return None

        if not isinstance(data, gpd.GeoDataFrame):
            if (GeomUtil.getIsGeo(self, dataframe=data)):
                data = GeomUtil.transformToGeoDf(self,dataframe=data)
            else:
                data = DataUtils.dataCleaner(self, data)
        self.setData(data)
        return self.data







    def setData(self, data):
        if self.sample_or_full_from_cache == SAMPLE and self.sample:
            self.sample_data = data
            self.data = self.sample_data
        elif self.sample_or_full_from_cache == FULL and not self.sample:
            self.full_data = data
            self.data = self.full_data

    def toSampleOnly(self):
        self.sample_or_full_from_cache = SAMPLE
        self.sample = True

    def toFullData(self):
        self.sample_or_full_from_cache = FULL
        self.sample = False

    def disconnect(self):
        self.connector.disconnect()
        self.caching_in_progress = False


class PsudRestApi():
    baseUrl = BASE_URL.__getitem__(0)[1]
    #endPointUrl = ""
    extraParams = {}

    def __init__(self, url, extraParams,jossoSession):
        self.jossoSession = jossoSession
        self.endPointUrl = url
        self.extraParams = extraParams
        self.totalNbEntity = 0
        self.nbEntityLoaded = 0
        self.nbRequest = 1

    def disconnect(self):
        pass

    def getData(self, sampleOnly):


        url = self.endPointUrl
        extraParams = self.extraParams
        data = pd.DataFrame()
        modulo = self.totalNbEntity % LIMIT_PARAM

        # on récupère les meta data à partir d'une seul entité
        extraParams['limit']= SAMPLE_LIMIT
        result = self.makeRequest(url, extraParams)
        while result.status_code == 503:
            result = self.makeRequest(url, extraParams)
            break

        if result.status_code == 200:
            try:
                jsonResult = json.loads(result.text)
                if jsonResult['success']:
                    total = jsonResult.get('total')
                    if total:
                        self.totalNbEntity = total
                    else:
                        # on devrait être dans le cas ou on demande une seule entité à l'application COMMON
                        self.totalNbEntity = 1
            except ValueError as e:
                self.message = "la donnée n\'est pas un JSON valide"
                print(self.message)
                return None

        elif result.status_code == 500:
            self.message = "erreur 500"
            dataFrame = pd.DataFrame(data={'0':["Data-Acces-Error"]})
            print(self.message)
            return dataFrame
        elif result.status_code == 503 :
            self.message = "erreur 503" + " " + result.reason
            return print(self.message)
        elif result.status_code == 404 :
            self.message = "erreur 404 " + result.reason
            return print( self.message )

        nbRequest = int((self.totalNbEntity - modulo) / LIMIT_PARAM)


        self.nbRequest = nbRequest if nbRequest > 0 else 1

        if sampleOnly:
            self.data = self.createDataframeFromJson(result)
            # on supprime le parametre limit et en fonction du nombre total de donnée on va paginer nos requetes pour pas killer le serveur.
            extraParams.pop('limit')
            self.nbEntityLoaded = self.data.shape[0]
            return self.data

        if (self.totalNbEntity < LIMIT_PARAM):
            result = self.makeRequest(url, extraParams)
            data = self.createDataframeFromJson(result)

        else:
            extraParams['limit'] = LIMIT_PARAM

            for i in range(0, self.totalNbEntity, LIMIT_PARAM):
                extraParams['start'] = i
                result = self.makeRequest(url, extraParams)
                df = pd.DataFrame()

                while result.status_code == 503:
                    self.message = "erreur 503"
                    print(self.message)
                    result = self.makeRequest(url, extraParams)
                    break

                if result.status_code == 200:
                    df = self.createDataframeFromJson(result)
                elif result.status_code == 500:
                    self.message = "erreur 500"
                    dataFrame = pd.DataFrame({'0':"data-Acces-Error"})
                    print(self.message)
                    return dataFrame
                elif result.status_code == 503:
                    self.message = "erreur 503"
                    print(self.message)
                else:
                    self.message ="on a un problème Huston " + result.status_code
                    print(self.message)
                    raise Exception('PsudRestApi Error', 'Request status code: ', result.status_code)

                if (data.size == 0):
                    data = df
                else:
                    data = data.append(df)

                self.nbEntityLoaded = data.shape[0]

                extraParams.pop('start')

        self.data = data
        return self.data

    def makeRequest(self, url, extraParams):
        params = ""
        for key, value in extraParams.items():
            params += "&" + key + "=" + str(value)

        result = requests.get(self.baseUrl + url + "?_responseMode=json" + params,
                              cookies=self.jossoSession.cookies, headers=self.jossoSession.headers)
        return result

    def createDataframeFromJson(self, result):
        jsonResult = json.loads(result.text)
        # on nettoie les données null en dict vide
        for i in jsonResult['data']:
            for  key, value in i.items():
                if value == None:
                    i[key] = {}

        dataFrame = pd.json_normalize(jsonResult['data'])
        return dataFrame

    def getSlicedData(self):
        url = self.endPointUrl
        extraParams = self.extraParams
        data = pd.DataFrame()


        result = self.makeRequest(url, extraParams)

        while result.status_code == 503:
            result = self.makeRequest(url, extraParams)
            break

        if result.status_code == 200:
            data = self.createDataframeFromJson(result)

        self.nbEntityLoaded += data.shape[0]

        return data

class PsudGeoCat():
    def __init__(self):
        return


class PsudDatabase():

    def __init__(self, dataBaseConnection, table, whereClause, jossoSession):
        self.jossoSession = jossoSession
        self.nbRequest = 1
        self.totalNbEntity = 0
        self.nbEntityLoaded = 0

        self.database = EXTERNE_DATABASES.get(dataBaseConnection)
        self.extraParams = whereClause

        user = jossoSession.login.split('@')[0]
        password = jossoSession.password
        host = self.database.get('HOST')
        namedb = self.database.get('NAME')

        url = 'postgresql://{}:{}@{}:5432/{}'.format(user,password,host,namedb)

        self.engine = create_engine(url)



        self.table = table
        self.whereClause = whereClause
        self.conn = None


    def getData(self, sampleOnly):
        # self.conn = psycopg2.connect(host=self.database.get('HOST'),
        #                             database=self.database.get('NAME'),
        #                             user=self.database.get('USER'),
        #                             password=self.database.get('PASSWORD'))
        query = "SELECT * from {} {}".format(self.table, self.whereClause)

        print("SQL query Log : {}".format(query))

        dataframe = pd.read_sql_query(query, con=self.engine)

        self.totalNbEntity = dataframe.shape[0]
        self.nbEntityLoaded = dataframe.shape[0]

        return dataframe

    def disconnect(self):
        self.closeConnection()
        pass

    def closeConnection(self):
        if self.conn is not None:
            self.conn.close()
            print('Database connection closed.')


class csvFile():
    def __init__(self):
        return
