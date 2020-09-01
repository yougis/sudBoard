import param
import pandas as pd
# data Type

#import des wrappers data -> HoloView

#libs plot
import geoviews.tile_sources as gts
import holoviews as hv
import hvplot.pandas

# libs carto

# class vizApp
from vizApps.domain.TypeVizEnum import TypeVizEnum


maillage = ["ISEE","Commune","Province"]


vizInstancesList = []

def getVizInstancesById(id):
    instance = [inst for inst in vizInstancesList if inst.id == id]
    if len(instance)>=1:
        return instance[0]  # on renvoit uniquement un objet
    return None


class BaseVizConstructor(param.Parameterized):

    def __init__(self, **params):
        self.overlays = None
        self.id = params["id"]
        super(BaseVizConstructor, self).__init__(**params)

    def formatter(value):
        return str(value)

    def connectTraceToViz(self,trace):
        viz = self
        trace.loadData()
        overlay = self.createViz(trace.data)
        self.addOverlay(overlay)

    def addOverlay(self,trace):
        if self.overlays:
            precedentOverlays = self.overlays
            self.overlays = precedentOverlays * trace
        else:
            self.overlays = trace
        return self.overlays

    def view(self):
        return self.getView()

    def setOption(self, option):
        options= hv.Options(option)
        return self.opts(options)

class BarGraphConstructor(BaseVizConstructor):

    def __init__(self, **params):
        self.type = TypeVizEnum.BAR_GRAPH
        vizInstancesList.append(self)
        super(BarGraphConstructor, self).__init__(**params)

    def getView(self):
        return self.overlays

    def createViz(self,data):
        data = pd.DataFrame(data)
        return data.hvplot.table(['numero'])


class MapConstructor(BaseVizConstructor):
    overlays = gts.OSM()

    def __init__(self, **params):
        super(MapConstructor, self).__init__(**params)

    def changeBaseMapToOSM(self):
        self.overlays = gts.OSM()

    def getView(self):
        return self.overlays


class ChoroplethMapConstructor(MapConstructor):
    maillageChoice = param.ObjectSelector(default=maillage[0], objects=maillage)
    selector = param.Selector(objects=["red", "yellow", "green"])
    num = param.Number()

    def __init__(self, **params):
        self.type = TypeVizEnum.CHOROPLETH_MAP
        vizInstancesList.append(self)
        super(ChoroplethMapConstructor, self).__init__(**params)

    def getView(self):
       self.overlays = self.overlays.opts(active_tools=['pan','wheel_zoom','lasso_select','box_select'])
       return self.overlays

    def createViz(self,data):
        return data.hvplot(tiles=True)
