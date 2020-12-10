from sudBoard.settings import BASE_URL
import requests
import pandas as pd
import json
import param
import intake

import geopandas as gpd
from vizApps.Utils.dataUtils import DataUtils
from vizApps.Utils.geomUtils import GeomUtil
from lumen.sources.base import  Source, cached
from lumen.util import get_dataframe_schema



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

from sqlalchemy import create_engine

from sudBoard.settings import EXTERNE_DATABASES

from vizApps.services.JossoSessionService import JossoSession



class PsudRestApi(Source):

    url = param.String(doc="URL of the REST endpoint to monitor.")

    def __init__(self, **params):
        super().__init__(**params)

    source_type = 'psud'
    baseUrl = BASE_URL.__getitem__(0)[1]
    #endPointUrl = ""
    extraParams = {}

   #def __init__(self, url, extraParams,jossoSession):
   #    self.jossoSession = jossoSession
   #    self.endPointUrl = url
   #    self.extraParams = extraParams
   #    self.totalNbEntity = 0
   #    self.nbEntityLoaded = 0
   #    self.nbRequest = 1

    def disconnect(self):
        pass

    def get_schema(self, table=None):
        if table:
            cat = self.cat[table].to_dask()
            return get_dataframe_schema(cat)['items']['properties']
        else:
            return {name: get_dataframe_schema(cat.to_dask())['items']['properties']
                    for name, cat in self.cat.items()}

    @cached
    def get(self, table, **query):

        sampleOnly= True


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
