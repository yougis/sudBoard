import param
import holoviews as hv
import hvplot.pandas

class BaseVizApp(param.Parameterized):

    def __init__(self, **params):
        self.overlays = None
        self.data = None
        self.id = params["viz_instance"].id
        self.dictParameters = self.get_param_values()
        super(BaseVizApp, self).__init__(**params)

    def formatter(value):
        return str(value)

    def connectTraceToViz(self,trace):
        trace.loadData()
        data = trace.data
        overlay = self.createViz(data=data)
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

    def createViz(self,**kwargs):
        data = kwargs["data"]
        return data.hvplot()