from django.contrib.postgres.fields import JSONField
from django.db import models
from vizApps.services.DataConnectorSevice import ConnectorInterface
from vizApps.Utils.geomUtils import GeomUtil
from vizApps.domain.Board import BoardEntity
from vizApps.domain.Viz import  VizEntity
from numpy import random
from vizApps.services.dataSource.dataFrameProfile import  DataFrameProfile

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

    def getConnector(self):
        connector = ConnectorInterface.get(self.dataConnectorParam)
        return connector

    def loadData(self):
        dataConnector = self.getConnector()
        self.data = dataConnector.getData()
        if (GeomUtil.getIsGeo(self, dataframe=self.data)):
            self.isGeo = True
            self.labelGeom = GeomUtil.getLabelGeom(self,dataframe=self.data)

    def dataProfileApp(self):
        data = self.data
        if self.isGeo:
            data = GeomUtil.transformGdfToDf(self,dataframe=data)
        profileApp = DataFrameProfile(data)
        profileApp.makeProfile()
        return profileApp.profile

    #### CRUD METHOD ###

    def save(self, *args, **kwargs):
        json = {}
        id = random.randint(0,10000000)
        json['connector-id'] = str(id)
        json['connector'] = "RestApi"
        json['url'] = "/ref/serail/Adresse"
        json['extraParams']=['tat','cac']
        self.dataConnectorParam = json
        super().save(*args, **kwargs)


