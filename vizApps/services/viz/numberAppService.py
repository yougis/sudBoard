from vizApps.services.viz.baseVizAppService import BaseVizApp
from vizApps.domain.TypeVizEnum import TypeVizEnum
import panel as pn
import holoviews as hv
import param
import hvplot.pandas

class NumberApp(BaseVizApp):
    column = param.Selector()

    def __init__(self, **params):
        self.type = TypeVizEnum.TABLE
        super(NumberApp, self).__init__(**params)

    def getView(self):

        return self.overlays

    @param.depends('column')
    def createOverlay(self, **kwargs):
        data = kwargs.get("traceParam").data

        return pn.Row(pn.pane.HTML(data[self.column]))