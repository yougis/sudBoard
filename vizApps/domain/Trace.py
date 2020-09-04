from django.contrib.postgres.fields import JSONField
from django.db import models
from vizApps.services.DataConnectorSevice import ConnectorInterface
from vizApps.domain.Board import BoardEntity
from vizApps.domain.Viz import  VizEntity
from numpy import random

dic = {'Commune':'/ref/dittt/CommuneNC', 'Adresse':'/ref/serail/Adresse'}

datasourceListe =[]
for key in dic:
    datasourceListe.append(key)

maillage = ["ISEE","Commune","Province"]

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
        if (dataConnector.getIsGeo(self.data)):
            self.isGeo = True
            self.labelGeom = dataConnector.getLabelGeom(self.data)


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


