from django.contrib.postgres.fields import JSONField
import json
from django.db import models
from vizApps.Utils.Utils import DicoUtils, ParamsUtils
from vizApps.services.VizConstructorService import ChoroplethMapConstructor, BarGraphConstructor
from vizApps.domain.TypeVizEnum import TypeVizEnum

import vizApps.services.VizConstructorService as VizConstructor


class VizManager(models.Manager):

    def create(cls, viz):
        viz = cls.create(_viz=viz)
        return viz

    def from_db(*args, **kwargs):  # cls, db, field_names, values
        args
        super().from_db(*args, **kwargs)


    def addVizAppInstance(cls, viz=None):
        _viz = {'vizApp': viz}



class VizEntity(models.Model):
    session = None
    title = models.CharField(max_length=30)
    slug = models.SlugField(max_length=50, unique=True)
    parameters = JSONField(null=True)

    type = models.CharField(
        max_length=15,
        choices=[(type.name, type.value) for type in TypeVizEnum],
        default=TypeVizEnum.TABLE
    )
    objects = VizManager()

    def __init__(self, *args, **kwargs):
        super(VizEntity, self).__init__(*args, **kwargs)
        self._vizApp = self.createVizAppFromJsonParameters(True)

    def __str__(self):
        return self.title + ' - ' + self.type


    def dicWrapper(self, typeViz):
        switcher = {
            TypeVizEnum.CHOROPLETH_MAP.name: ChoroplethMapConstructor(id=self.id),
            TypeVizEnum.BAR_GRAPH.name: BarGraphConstructor(id=self.id)
        }
        return switcher.get(typeViz, None)

    def save(self, *args, **kwargs):
        excludeKey = {"name"}  # on ne peut pas modifier le nom d'une viz
        dicParam = ParamsUtils.recursiveParamToJsonDict(self,
                                                        parameters=self.getVizApp.param.get_param_values())
        parameters = DicoUtils.excludingkeys(self,
                                             (dicParam),
                                             excludeKey)
        self.parameters = json.dumps(parameters)
        super().save(*args, **kwargs)

    def createVizAppFromJsonParameters(self, initSession):
        # On cherche si l'instance de la viz existe déjà dans la session
        vizApp = VizConstructor.getVizAppInstancesById(self.id)
        if (vizApp and initSession == False):
            #self._vizApp(vizApp=vizApp)
            print(vizApp, ' ', id(vizApp))
            return {'vizApp': vizApp}
        else:
            vizApp = self.dicWrapper(self.type)
            excludeKey = {"name"}  # on ne peut pas modifier le nom de la classe d'un type de viz
            result_dict = ParamsUtils.jsonParamsContructor(self,
                                                           dictionnary=DicoUtils.excludingkeys(self,
                                                                                                     dico=json.loads(self.parameters),
                                                                                                     excludingKey=excludeKey))
            for p in result_dict:
                vizApp.param.set_param(p[0], p[1])
                # typeViz est maintenant une instance Viz parmétrée

        #self._vizApp["vizApp"] = vizApp

        print(vizApp, ' ', id(vizApp))
        return  {'vizApp': vizApp}

    def getVizById(self, id):
        return VizConstructor.get(id)

    @property
    def getVizApp(self):
        return self._vizApp["vizApp"]


