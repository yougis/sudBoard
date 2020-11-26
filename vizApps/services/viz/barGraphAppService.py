from vizApps.services.viz.baseVizAppService import BaseVizApp
from vizApps.domain.TypeVizEnum import TypeVizEnum
import holoviews as hv
import pandas as pd
import hvplot.pandas
import param

class BarGraphApp(BaseVizApp):
        # discrete, numerical comparisons across categories.
    # http://holoviews.org/reference/elements/bokeh/Bars.html#elements-bokeh-gallery-bars

    def __init__(self, **params):
        self.type = TypeVizEnum.BAR_GRAPH
        super(BarGraphApp, self).__init__(**params)

    def getView(self):
        return self.overlays

    def createOverlay(self, **kwargs):
        traceP= kwargs["traceParam"]
        data = traceP.data
        groupby= kwargs.get("groupby")

        return hv.Overlay([data.hvplot.bar()])# * hv.Histogram(data)