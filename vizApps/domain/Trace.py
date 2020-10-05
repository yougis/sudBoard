from django.contrib.postgres.fields import JSONField
from django.db import models
from vizApps.services.DataConnectorSevice import ConnectorInterface, SAMPLE, FULL
from vizApps.Utils.geomUtils import GeomUtil
from vizApps.domain.Board import BoardEntity
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

    def manual_init(self):
        self.dataLoading = False
        self.dataReady = False
        self.progressBar = ProgressExtMod()

    def getConnector(self):
        connector = ConnectorInterface.get(self.dataConnectorParam)
        return connector

    @property
    def isDataInCache(self):
        dataConnector = self.getConnector()
        return dataConnector.isDataInCache()

    @property
    def getSample_data(self):
        dataConnector = self.getConnector()
        return dataConnector.sample_data

    def lookCachedData(self):
        dataConnector = self.getConnector()
        self.data = dataConnector.lookCachedData()

    @property
    def getTotalNbEntity(self):
        dataConnector = self.getConnector()
        return dataConnector.connector.totalNbEntity

    @property
    def getNbEntityLoaded(self):
        dataConnector = self.getConnector()
        return dataConnector.connector.nbEntityLoaded

    @property
    def getNbRequest(self):
        dataConnector = self.getConnector()
        return dataConnector.connector.nbRequest

    def configureConnector(self,sampleOrFull):
        self.data = pd.DataFrame()
        dataConnector = self.getConnector()
        dataConnector.caching_in_progress = True
        self.setLoading()

        if sampleOrFull == SAMPLE:
            dataConnector.toSampleOnly()
        elif sampleOrFull == FULL:
            dataConnector.toFullData()

    def finishConnection(self):
        dataConnector = self.getConnector()
        dataConnector.caching_in_progress = False
        self.setReady()
        dataConnector.disconnect()

    def loadData(self):
        dataConnector = self.getConnector()
        self.data = dataConnector.getData()

    def loadSliceData(self, extraParams):
        dataConnector = self.getConnector()
        dataConnector.connector.extraParams = extraParams
        data = dataConnector.connector.getSlicedData()

        if not isinstance(data, gpd.GeoDataFrame):
            if (GeomUtil.getIsGeo(self, dataframe=data)):
                data = GeomUtil.transformToGeoDf(self,dataframe=data)
        self.data = self.data.append(data)

        # pour la dernière passe
        if extraParams["end"] >= self.getTotalNbEntity:
            self.setReady()
        else:
            self.setLoading()

    def setLoading(self):
        self.dataLoading = True
        self.dataReady = False

    def setReady(self):
        self.dataLoading = False
        self.dataReady = True



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
        json['connector'] = "RestApi"
        json['url'] = "/ref/serail/Adresse"
        json['extraParams']={'tat':"dd",'cac':"a"}
        self.dataConnectorParam = json
        super().save(*args, **kwargs)


