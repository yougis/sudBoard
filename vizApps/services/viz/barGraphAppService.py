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

    def createOverlay(self, **kwargs):
        data = pd.DataFrame(kwargs.get("data"))
        dimension = kwargs.get("dim") if kwargs.get("dim") else []
        groupby= kwargs.get("groupby")

        return data.hvplot.hist(dimension=dimension,groupby=groupby)