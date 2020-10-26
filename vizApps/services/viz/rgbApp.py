from vizApps.services.viz.baseVizAppService import BaseVizApp
from vizApps.domain.TypeVizEnum import TypeVizEnum
import holoviews as hv

class RgbApp(BaseVizApp):

    def __init__(self, **params):
        self.type = TypeVizEnum.BAR_GRAPH
        super(RgbApp, self).__init__(**params)

    def getView(self):
        return self.overlays

    def createOverlay(self, **kwargs):
        path = kwargs.get('path')

        return hv.RGB.load_image(path)