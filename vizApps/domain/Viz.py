from django.contrib.postgres.fields import JSONField
import json
from django.db import models
from vizApps.Utils.Utils import DicoUtils, ParamsUtils
from vizApps.services.VizConstructorService import ChoroplethMapConstructor, BarGraphConstructor
from vizApps.domain.TypeVizEnum import TypeVizEnum

import vizApps.services.VizConstructorService as VizConstructor


class VizEntity(models.Model):
    session = None
    title = models.CharField(max_length=30)
    slug = models.SlugField(max_length=50, unique=True)
    parameters = JSONField(blank=True)
    _viz = {'vizApp':None}

    type = models.CharField(
        max_length=15,
        choices=[(type.name, type.value) for type in TypeVizEnum],
        default=TypeVizEnum.TABLE
    )

    def __str__(self):
        return self.title + ' - ' + self.type

    def dicWrapper(self, typeViz):
        switcher = {
            TypeVizEnum.CHOROPLETH_MAP.name: ChoroplethMapConstructor(id=self.id),
            TypeVizEnum.PARAM.name: BarGraphConstructor(id=self.id)
        }
        return switcher.get(typeViz,None)


    def save(self, *args, **kwargs):
        excludeKey = {"name"}  # on ne peut pas modifier le nom d'une viz
        dicParam = ParamsUtils.recursiveParamToJsonDict(self, parameters=self.getVizParam.param.get_param_values())
        parameters = DicoUtils.excludingkeys(self, (dicParam), excludeKey)
        self.parameters = json.dumps(parameters)
        super().save(*args, **kwargs)


    def createVizFromJsonParameters(self, initSession):
        # On cherche si l'instance de la viz existe déjà dans la session

        viz = VizConstructor.getVizInstancesById(self.id)
        if(viz and initSession == False):
            print(viz, ' ', id(viz))
            return viz
        else:
            viz = self.dicWrapper(self.type)
            excludeKey = {"name"}  # on ne peut pas modifier le nom de la classe d'un type de viz
            result_dict = ParamsUtils.jsonParamsContructor(self,dictionnary=DicoUtils.excludingkeys(self, dico=json.loads(self.parameters), excludingKey=excludeKey))

            for p in result_dict:
                viz.param.set_param(p[0],p[1])
                # typeViz est maintenant une instance Viz parmétrée

        print(viz, ' ', id(viz))
        return viz

    def getVizById(self, id):
        return VizConstructor.get(id)

    @property
    def getVizParam(self):
        return self._viz["vizApp"]

