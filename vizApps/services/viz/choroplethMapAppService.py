from vizApps.services.viz.baseMapAppService import BaseMapApp
import param
from vizApps.domain.TypeVizEnum import TypeVizEnum
import hvplot.pandas
from cartopy import crs
import geoviews as gv

fondecarte = gv.tile_sources.Wikipedia

maillage = ["ISEE","Commune","Province"]

class ChoroplethMapAppService(BaseMapApp):

    maillageChoice = param.ObjectSelector(default=maillage[0], objects=maillage)
    selector = param.Selector(objects=["red", "yellow", "green"])
    num = param.Number()

    def __init__(self, **params):
        self.type = TypeVizEnum.CHOROPLETH_MAP
        super(ChoroplethMapAppService, self).__init__(**params)

    def getView(self):
        # customize defaut options
        self.overlays = self.overlays.opts(active_tools=['pan', 'wheel_zoom'])

        return self.overlays

    def createViz(self,**kwargs):
        self.data = kwargs["data"]
        points = fondecarte * gv.Points(self.data, crs=crs.GOOGLE_MERCATOR)
        polygons =  gv.Polygons(self.data)

        return points
