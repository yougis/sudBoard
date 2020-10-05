from sudBoard.settings import BASE_URL
import requests
import pandas as pd
import json
import geopandas as gpd
from vizApps.Utils.geomUtils import GeomUtil

from sqlalchemy import create_engine

from sudBoard.settings import EXTERNE_DATABASES

from vizApps.services.JossoSessionService import JossoSession

# limit de nombre d'objet par requete
LIMIT_PARAM = 1000

FULL = "FULL"
SAMPLE = "SAMPLE"

class ConnectorInterface():
    instances = []

    def __init__(self, json):
        self.id = json["connector-id"]
        self.data = pd.DataFrame()
        self.sample_data = pd.DataFrame()
        self.full_data = pd.DataFrame()
        self.sample_or_full_from_cache = None #SAMPLE or FULL
        self.sample = False
        self.no_cache = False
        self.caching_in_progress = False
        ConnectorInterface.instances.append(self)
        if (json["connector"] == "RestApi"):
            self.connector = PsudRestApi(json['url'], json['extraParams'])
        elif (json["connector"] == "Database"):
            self.connector = PsudDatabase(json['db'], json['Table'], json['whereClause'])

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
            print('Pas de données {} en cache pour le type de demande'.format(self.askFromCacheOrNot))
            return None

    def returnSampleOrFullData(self):
        data = {
            SAMPLE: self.sample_data,
            FULL : self.full_data
        }
        return data.get(self.sample_or_full_from_cache)

    def getData(self):
        data = self.connector.getData(self.sample)

        if not isinstance(data, gpd.GeoDataFrame):
            if (GeomUtil.getIsGeo(self, dataframe=data)):
                data = GeomUtil.transformToGeoDf(self,dataframe=data)

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
    baseUrl = BASE_URL.__getitem__(1)[1]
    endPointUrl = ""
    extraParams = {}
    jossoSession = JossoSession()

    def __init__(self, url, extraParams):
        self.jossoSession = JossoSession()
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
        extraParams['limit']=10
        result = self.makeRequest(url, extraParams)
        while result.status_code == 503:
            result = self.makeRequest(url, extraParams)
            break

        if result.status_code == 200:
            jsonResult = json.loads(result.text)
            self.totalNbEntity = jsonResult['total']
            print(self.totalNbEntity)
        elif result.status_code == 500:
            dataFrame = pd.DataFrame(data={'0':["Data-Acces-Error"]})
            return dataFrame
        elif result.status_code == 503 :
            return print('503 ERROR')

        self.nbRequest = int((self.totalNbEntity - modulo) / LIMIT_PARAM)

        if sampleOnly:
            self.data = self.createDataframeFromJson(result)
            # on supprime le parametre limit et en fonction du nombre total de donnée on va paginer nos requetes pour pas killer le serveur.
            extraParams.pop('limit')
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
                    result = self.makeRequest(url, extraParams)
                    break

                if result.status_code == 200:
                    df = self.createDataframeFromJson(result)
                elif result.status_code == 500:
                    dataFrame = pd.DataFrame({'0':"data-Acces-Error"})
                    return dataFrame
                elif result.status_code == 503:
                    print("Huston 503")
                else:
                    print("on a un problème Huston")
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

        print(data.head())
        print(extraParams)
        return data

class PsudGeoCat():
    def __init__(self):
        return


class PsudDatabase():

    def __init__(self, dataBaseConnection, table, whereClause):
        self.database = EXTERNE_DATABASES.get(dataBaseConnection)
        self.engine = create_engine('postgresql://{}@{}:5432/{}'.format(self.database.get('USER'),
                                                                        self.database.get('HOST'),
                                                                        self.database.get('NAME')))
        self.table = table
        self.whereClause = whereClause
        self.conn = None


    def getData(self):
        # self.conn = psycopg2.connect(host=self.database.get('HOST'),
        #                             database=self.database.get('NAME'),
        #                             user=self.database.get('USER'),
        #                             password=self.database.get('PASSWORD'))

        dataframe = pd.read_sql_query("SELECT * from {} {}".format(self.table, self.whereClause), con=self.engine)

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
