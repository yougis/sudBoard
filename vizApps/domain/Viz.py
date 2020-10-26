from django.contrib.postgres.fields import JSONField
import json
from django.db import models
from vizApps.Utils.utils import DicoUtils, ParamsUtils
from vizApps.services.viz.choroplethMapAppService import ChoroplethMapAppService
from vizApps.services.viz.barGraphAppService import BarGraphApp
from vizApps.services.viz.tableAppService import TableApp
from vizApps.services.viz.proportionalPointMapAppService import ProportionalPointMapAppService


from vizApps.domain.TypeVizEnum import TypeVizEnum

import vizApps.services.viz.VizInstanceService as VizConstructor


class VizManager(models.Manager):

    def create(cls, viz):
        viz = cls.create(_viz=viz)
        return viz

    @classmethod
    def from_db(*args, **kwargs):  # cls, db, field_names, values
        args
        super().from_db(*args, **kwargs)


    def addVizAppInstance(cls, viz=None):
        _viz = {'vizApp': viz}



class VizEntity(models.Model):

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
        #self._vizApp = self.createVizAppFromJsonParameters(initSession=True)

    def __str__(self):
        return self.title + ' - ' + self.type

    def updateVizApp(self,vizApp):
        self._vizApp = {'vizApp': vizApp}


    def dicWrapper(self, typeViz, session=None):
        switcher = {
            TypeVizEnum.CHOROPLETH_MAP.name: ChoroplethMapAppService(viz_instance=self, session=session),
            TypeVizEnum.BAR_GRAPH.name: BarGraphApp(viz_instance=self, session=session),
            TypeVizEnum.TABLE.name : TableApp(viz_instance=self, session=session),
            TypeVizEnum.POINT_MAP.name: ProportionalPointMapAppService(viz_instance=self, session=session)
        }
        return switcher.get(typeViz, None)

    def save(self, *args, **kwargs):
        excludeKey = {"name"} # on ne peut pas modifier le nom d'une viz (?)



        if not self.getVizApp: # on est dans le cas d'une création API
            vizApp = self.dicWrapper(self.type)
            result_dict = ParamsUtils.jsonParamsContructor(self,
                                                           dictionnary=DicoUtils.excludingkeys(self,
                                                                                               dico=json.loads(
                                                                                                   self.parameters),
                                                                                               excludingKey=excludeKey))
            for p in result_dict:
                vizApp.param.set_param(p[0], p[1])
                # typeViz est maintenant une instance Viz parmétrée

            self._vizApp = {'vizApp': vizApp}




        dicParam = ParamsUtils.recursiveParamToJsonDict(self,
                                                        parameters=self.getVizApp.param.get_param_values())

        # on eject aussi les boutons actions
        for p in dicParam:
            if hasattr(dicParam[p], '__call__'):
                excludeKey.add(p)

        parameters = DicoUtils.excludingkeys(self,
                                             (dicParam),
                                             excludeKey)
        self.parameters = json.dumps(parameters)
        super().save(*args, **kwargs)

    def createVizAppFromJsonParameters(self, initSession=None, session=None):
        # On cherche si l'instance de la viz existe déjà dans la session
        vizApp = VizConstructor.getVizAppInstancesById(id(self))
        if (vizApp and initSession == False):
            print('vizApp exist : ', vizApp, ' adresse mémoire :', id(vizApp))
            return {'vizApp': vizApp}
        else:
            vizApp = self.dicWrapper(self.type,session)
            excludeKey = {"name"}  # on ne peut pas modifier le nom de la classe d'un type de viz
            result_dict = ParamsUtils.jsonParamsContructor(self,
                                                           dictionnary=DicoUtils.excludingkeys(self,
                                                                                                     dico=json.loads(self.parameters),
                                                                                                     excludingKey=excludeKey))
            for p in result_dict:
                vizApp.param.set_param(p[0], p[1])
                # typeViz est maintenant une instance Viz parmétrée
        VizConstructor.vizInstancesList.append(vizApp)
        print('vizApp Created : ', vizApp, ' adresse mémoire :', id(vizApp))
        return  {'vizApp': vizApp}

    @property
    def getVizApp(self):
        try:
            return self._vizApp.get("vizApp")
        except:
            return None


