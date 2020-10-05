from vizApps.services.viz.baseVizAppService import BaseVizApp
from vizApps.domain.TypeVizEnum import TypeVizEnum
import pandas as pd
import hvplot.pandas

class TableApp(BaseVizApp):

    def __init__(self, **params):
        self.type = TypeVizEnum.TABLE
        super(TableApp, self).__init__(**params)

    def getView(self):
        return self.overlays

    def createOverlay(self, **kwargs):
        data = pd.DataFrame( kwargs.get("data"))
        return data.hvplot.table()