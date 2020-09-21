from sudBoard.settings import BASE_URL
import requests
import pandas as pd
import json
import geopandas as gpd
from vizApps.Utils.geomUtils import GeomUtil

from sqlalchemy import create_engine

from sudBoard.settings import EXTERNE_DATABASES

from vizApps.services.JossoSessionService import JossoSession

LIMIT_PARAM = 100

class ConnectorInterface():
    instances = []

    def __init__(self, json):
        self.id = json["connector-id"]
        self.data = None
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

    def getData(self, force=False):
        if force == True:
            self.data = self.connector.getData()

        if isinstance(self.data, pd.DataFrame) or isinstance(self.data, gpd.GeoDataFrame):
            if self.data.empty:
                self.data = self.connector.getData()
            else:
                return self.data

        if self.data != None:
            return self.data
        else:
            self.data = self.connector.getData()

        if GeomUtil.getIsGeo(self,dataframe=self.data):
            self.data = GeomUtil.transformToGeoDf(self,dataframe=self.data)

        return self.data

    def refreshData(self):
        return self.getData(self, force=True)


class PsudRestApi():
    baseUrl = BASE_URL.__getitem__(1)[1]
    endPointUrl = ""
    extraParams = ""
    jossoSession = JossoSession()

    def __init__(self, url, extraParams):
        self.jossoSession = JossoSession()
        self.endPointUrl = url
        self.extraParams = extraParams

    def getData(self):
        url = self.endPointUrl
        extraParams = self.extraParams
        # on récupère les meta data à partir d'une seul entité
        extraParams.append('limit=1')
        result = requests.get(self.baseUrl + url + "?_responseMode=json&" + '&'.join(extraParams),
                              cookies=self.jossoSession.cookies, headers=self.jossoSession.headers)

        if result.status_code == 200:
            jsonResult = json.loads(result.text)
            nbEntity = jsonResult['total']
            print(nbEntity)

        else:
            print("on a un problème Huston")
            raise Exception('PsudRestApi Error', 'Data')

        # on supprime le parametre limit et en fonction du nombre total de donnée on va paginer nos requetes pour pas killer le serveur.
        extraParams.pop()

        data = pd.DataFrame()
        if (nbEntity < LIMIT_PARAM):
            data = self.makeRequest(url, extraParams)

        else:
            modulo = nbEntity % LIMIT_PARAM
            nbOfRequest = int((nbEntity - modulo) / LIMIT_PARAM)
            limitParam = 'limit=' + str(LIMIT_PARAM)

            extraParams.append(limitParam)

            nbEntity = 10

            for i in range(0, nbEntity, LIMIT_PARAM):
                extraParams.append('start=' + str(i))
                df = self.makeRequest(url, extraParams)

                if (data.size == 0):
                    data = df
                else:
                    data = data.append(df)
                print(data.head())

                extraParams.pop()

        self.data = data
        return self.data

    def makeRequest(self, url, extraParams):
        result = requests.get(self.baseUrl + url + "?_responseMode=json&" + '&'.join(extraParams),
                              cookies=self.jossoSession.cookies, headers=self.jossoSession.headers)
        jsonResult = json.loads(result.text)
        dataFrame = pd.json_normalize(jsonResult['data'])
        return dataFrame

    def paginatedRequest(self, url, extraParams):
        resultPage = self.makeRequest(url, extraParams)
        return resultPage


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

    def getData(self):
        # self.conn = psycopg2.connect(host=self.database.get('HOST'),
        #                             database=self.database.get('NAME'),
        #                             user=self.database.get('USER'),
        #                             password=self.database.get('PASSWORD'))

        dataframe = pd.read_sql_query("SELECT * from {} {}".format(self.table, self.whereClause), con=self.engine)

        return dataframe

    def closeConnection(self):
        if self.conn is not None:
            self.conn.close()
            print('Database connection closed.')


class csvFile():
    def __init__(self):
        return
