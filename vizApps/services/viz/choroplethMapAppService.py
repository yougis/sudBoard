from vizApps.services.viz.baseMapAppService import BaseMapApp
import param
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

    def getView(self):
        # customize defaut options
        return super().getView()

    def createOverlay(self,**kwargs):
        traceP = kwargs.get("traceParam")
        data = traceP.data
        label  = kwargs.get("label")
        vdims = traceP.listeEntier
        size = 1 if not traceP.listeEntier else traceP.listeEntier[0]

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

