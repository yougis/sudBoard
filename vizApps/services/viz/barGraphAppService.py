from vizApps.services.viz.baseVizAppService import BaseVizApp
from vizApps.domain.TypeVizEnum import TypeVizEnum
import pandas as pd
import hvplot.pandas

class BarGraphApp(BaseVizApp):

    def __init__(self, **params):
        self.type = TypeVizEnum.BAR_GRAPH
        super(BarGraphApp, self).__init__(**params)

    def getView(self):
        return self.overlays

    def createViz(self, **kwargs):
        data = pd.DataFrame( kwargs["data"])
        return data.hvplot.table(['numero'])