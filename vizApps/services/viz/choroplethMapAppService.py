from vizApps.services.viz.baseMapAppService import BaseMapApp
import param, panel as pn
from vizApps.domain.TypeVizEnum import TypeVizEnum
import hvplot.pandas
from cartopy import crs
import holoviews as hv
import geoviews as gv
from geoviews import dim

POINT = ['Point','point[int64]','multipoint[int64]']
POLYGONE = ['Polygon','MultiPolygon', 'polygon[int64]','multipolygon[int64]']
MULTIPOLYGONE = 'MultiPolygon'
MULTILINESTRING = 'MultiLineString'
LINESTRING = ['LineString','MultiLineString','MultiLine','line[int64]','multiline[int64]']

STRONG_SIMPLIFY = 500.0
SOFT_SIMPLIFY = 50.0

maillage = ["ISEE","Commune","Province"]

class ChoroplethMapAppService(BaseMapApp):

    maillageChoice = param.ObjectSelector(default=maillage[0], objects=maillage)
    selector = param.Selector(objects=["red", "yellow", "green"])
    num = param.Number()

    def __init__(self, **params):
        self.type = TypeVizEnum.CHOROPLETH_MAP
        super(ChoroplethMapAppService, self).__init__(**params)

    def getConfigTracePanel(self, **params):
        self.configTracePanel = pn.Column(self.param.maillageChoice, self.param.selector, self.param.num)
        return super().getConfigTracePanel()

    def getVizConfig(self):
        self.configVizPanel.append()
        return super().getConfigVizPanel()

    def getView(self):
        # customize defaut options
        return super().getView()


    @param.depends('maillageChoice', 'selector', 'num', watch=True)
    def changeProperties(self):
        if not self.silently:
            self.refreshViz()
        self.silently = False

    def createOverlay(self,**kwargs):

        return super().createOverlay(**kwargs)

