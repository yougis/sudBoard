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


class ProportionalPointMapAppService(BaseMapApp):
    variable_taille_point = param.Selector()



    def __init__(self, **params):
        self.type = TypeVizEnum.POINT_MAP
        self._listeEntier = []

        super(ProportionalPointMapAppService, self).__init__(**params)


    def getConfigTracePanel(self):
        self.configTracePanel = pn.Column(self.param.variable_taille_point)
        return super().getConfigTracePanel()

    def getVizConfig(self):
        self.configVizPanel.append()
        return super().getConfigVizPanel()

    def getView(self):
        # customize defaut options
        return super().getView()

    @param.depends('variable_taille_point', watch=True)
    def changePointSize(self):
        pass
        #self.param.variable_taille_point.objects = self._listeEntier
       #if self.tracePContext:
       #    self.tracePContext = None
       #    self.doRefreshByTraceParam(self.tracePContext)

    def createOverlay(self,**kwargs):

        traceP = kwargs.get("traceParam")
        data = traceP.data
        label  = kwargs.get("label")
        self._listeEntier = traceP.listeEntier
        self.param.variable_taille_point.objects = self._listeEntier

        if not self.variable_taille_point:
            self.variable_taille_point = self._listeEntier[0]

        self.tracePContext=traceP
        vdims = traceP.listeEntier
        size = self.variable_taille_point
        ndOverlays= []

        arrayGeomType = data.geom_type.unique()

        for geomType in arrayGeomType:

            data = data[data['geometry'].apply(lambda x: x.geom_type == geomType)]

            if geomType in POINT:
                geomNdOverlay = gv.Points(data, vdims=vdims, crs=crs.GOOGLE_MERCATOR, label=label, group=POINT[0]).opts(size=dim(size))
            elif geomType in POLYGONE:
                data['geometry'] = data.simplify(STRONG_SIMPLIFY,True)
                geomNdOverlay =  gv.Polygons(data,vdims=vdims, crs=crs.GOOGLE_MERCATOR,label=label, group=POLYGONE[0])

            elif geomType in LINESTRING:
                data['geometry'] = data.simplify(SOFT_SIMPLIFY, True)
                geomNdOverlay = gv.Path(data, crs=crs.GOOGLE_MERCATOR,label=label, group=LINESTRING[0])

            elif geomType in MULTILINESTRING:
                data['geometry'] = data.simplify(SOFT_SIMPLIFY, True)
                geomNdOverlay = gv.Path(data, crs=crs.GOOGLE_MERCATOR, label=label, group=MULTILINESTRING[0])

            elif geomType in MULTIPOLYGONE:
                data['geometry'] = data.simplify(STRONG_SIMPLIFY,True)
                geomNdOverlay =  gv.Polygons(data, vdims=vdims, crs=crs.GOOGLE_MERCATOR,label=label, group=MULTIPOLYGONE[0])
            else:
                geomNdOverlay = None

            ndOverlays.append(geomNdOverlay.opts(tools=['hover', 'tap'],color=vdims[0], cmap='Category20'))


        overlays = hv.Overlay(ndOverlays)



        return overlays

