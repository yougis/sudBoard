from django.contrib.postgres.fields import JSONField
from django.db import models
from vizApps.domain.Board import BoardEntity

from vizApps.services.DataConnectorSevice import ConnectorInterface, SAMPLE, FULL
from vizApps.Utils.geomUtils import GeomUtil
from vizApps.domain.Viz import  VizEntity
from numpy import random

import pandas as pd
import geopandas as gpd
from vizApps.services.viz.progressExtModule import ProgressExtMod



#from vizApps.services.dataSource.dataFrameProfile import  DataFrameProfile

dic = {'Commune':'/ref/dittt/CommuneNC', 'Adresse':'/ref/serail/Adresse'}

datasourceListe =[]
for key in dic:
    datasourceListe.append(key)

class DataCatalogue(models.Model):
    name = models.CharField(max_length=30)
    sourceList = datasourceListe


class TraceEntity(models.Model):
    name = models.CharField(max_length=30)
    dataConnectorParam = JSONField(blank=True)
    board = models.ForeignKey(BoardEntity, on_delete=models.CASCADE)
    vizListe = models.ManyToManyField(VizEntity, verbose_name="liste des viz",blank=True)
    isGeo = False
    labelGeom=None

    def __str__(self):
        return self.name

    def initializeLoading(self):
        self.dataLoading = False
        self.dataReady = False
        self.dataFrame = pd.DataFrame()

    def setConnector(self):
        self.connectorInterface = ConnectorInterface.get(self.dataConnectorParam)
        print('Récupération du connecteur {} de la trace {}'.format(self.connectorInterface.connectorType, self.name))
        return self.connectorInterface

    @property
    def isDataInCache(self):
        return self.connectorInterface.isDataInCache()

    @property
    def getSample_data(self):
        return self.connectorInterface.sample_data

    def lookCachedData(self):
        self.connectorInterface.caching_in_progress = True
        self.dataFrame = self.connectorInterface.lookCachedData()
        print("Récupération des Data {} en cache".format(self.connectorInterface.sample_or_full_from_cache))

    @property
    def getTotalNbEntity(self):
        return self.connectorInterface.connector.totalNbEntity

    @property
    def getNbEntityLoaded(self):
        return self.connectorInterface.connector.nbEntityLoaded

    @property
    def getNbRequest(self):
        return self.connectorInterface.connector.nbRequest

    def configureConnector(self,sampleOrFull):
        print("Configuration du connector Interface en mode {} pour la trace {}".format(sampleOrFull, self.name))
        self.setConnector()
        self.dataFrame = pd.DataFrame()

        if sampleOrFull == SAMPLE:
            self.connectorInterface.toSampleOnly()
        elif sampleOrFull == FULL:
            self.connectorInterface.toFullData()

    def finishConnection(self):
        self.setReady()
        self.connectorInterface.disconnect()
        print("Connection terminée pour la trace {}".format(self.name))

    def loadData(self):
        self.setLoading()
        self.dataFrame = self.connectorInterface.getData()
        print("Loading des données avec extraParams {}".format(self.connectorInterface.connector.extraParams))


    def loadSliceData(self, extraParams):
        self.connectorInterface.connector.extraParams = extraParams

        # pour la dernière passe
        if extraParams["end"] >= self.getTotalNbEntity:
            self.setReady()
        else:
            self.setLoading()

        data = self.connectorInterface.connector.getSlicedData()

        print("Loading des données en mode SLICED avec extraParams {}".format(self.connectorInterface.connector.extraParams))


        if not isinstance(data, gpd.GeoDataFrame):
            if (GeomUtil.getIsGeo(self, dataframe=data)):
                data = GeomUtil.transformToGeoDf(self.connectorInterface,dataframe=data)
                self.isGeo = True
                print("Donnée rendu compatible pour les traitements spatiaux")

        self.dataFrame= self.dataFrame.append(data)

        print(
        """
        Entités en cours d'upload : {} 
        {}        
        """.format(data.shape[0], data.head()))

        print("Entités chargées dans la trace : {}".format(self.dataFrame.shape[0]))

    def setLoading(self):
        self.dataLoading = True
        self.dataReady = False
        print("Donnée en cours de chargement pour la trace {}".format(self.name))

    def setReady(self):
        self.dataLoading = False
        self.dataReady = True
        print("Donnée prête pour la trace {}".format(self.name))

    def dataProfileApp(self):
        data = self.data
        if self.isGeo:
            data = GeomUtil.transformGdfToDf(self,dataframe=data)
        #profileApp = DataFrameProfile(data)
        #profileApp.makeProfile()
        return "profileApp.profile"

    #### CRUD METHOD ###

    def save(self, *args, **kwargs):
        json = {}
        id = random.randint(0,10000000)
        json['connector-id'] = str(id)
        json['connector'] = "Url"
        json['url'] = "/ref/serail/Voirie"
        json['extraParams']={'tat':"dd",'cac':"a"}
        self.dataConnectorParam = json
        super().save(*args, **kwargs)


