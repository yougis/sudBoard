from vizApps.services.viz.baseVizAppService import BaseVizApp
from vizApps.Utils.geomUtils import GeomUtil


import holoviews as hv
import geoviews as gv
import geoviews.tile_sources as gts
from cartopy import crs

import param
import panel as pn
from holoviews import opts
from holoviews.core import AttrTree
from bokeh.models import WheelZoomTool, SaveTool


POINT = ['Point','point[int64]','multipoint[int64]']
POLYGONE = ['Polygon','MultiPolygon', 'polygon[int64]','multipolygon[int64]']
MULTIPOLYGONE = 'MultiPolygon'
MULTILINESTRING = 'MultiLineString'
LINESTRING = ['LineString','MultiLineString','MultiLine','line[int64]','multiline[int64]']

STRONG_SIMPLIFY = 500.0
SOFT_SIMPLIFY = 50.0


liste_background = [name[0] for name in hv.element.tiles.tile_sources.items()]

class BaseMapApp(BaseVizApp):
    _opts = opts.defaults()
    fond_de_carte = param.ObjectSelector(default=liste_background[0], objects=liste_background)
    extent = [(-22,166),(-22.5,166.5)]

    def __init__(self, **params):
        super(BaseMapApp, self).__init__(**params)
        # on surcharge l overlays du parent avec le fond de carte
        self.baseTileMap = [ts() for name, ts in hv.element.tiles.tile_sources.items() if name == self.fond_de_carte][0]

        self.overlays = hv.Overlay() * self.baseTileMap

    def debugPanel(self):
        return super().debugPanel()


    @param.depends("viewable", "loaded","fond_de_carte", "change_state") # on met les même event que pour la baseclass en ajoutant la gestion du fond de carte
    def view(self):
        return super().view()


    def getView(self):
        self.changeBaseMap()
        ## on ajoute les options Carte par défaut
        wheel_zoom = WheelZoomTool(zoom_on_axis=False)

        self.overlays = self.overlays.options(
            toolbar='above',
            default_tools=[wheel_zoom],
            active_tools=['wheel_zoom'],

            #xaxis=None,
            #yaxis=None,
        )
        return self.overlays.opts( width=800, height=600)

    def getConfigTracePanel(self, **params):

        return super().getConfigTracePanel()

    def getConfigVizPanel(self):

        self.configVizPanel = pn.Column(self.param.fond_de_carte)

        return super().getConfigVizPanel()

    def createOverlay(self, **kwargs):
        traceP = kwargs.get("traceParam")
        data = traceP.data
        label = kwargs.get("label")
        vdims = traceP.listeEntier

        geomNdOverlay = GeomUtil.getGeoElementFromData(self,data=data,vdims=vdims)


        overlay = hv.Overlay(
            [geomNdOverlay.opts(tools=['hover', 'tap'])]
        )
        return overlay


    def changeBaseMap(self):
        if self.overlays and len(self.overlays)>1:
            # on change  le flux WMTS et on reprend la couche l'entité (la plus haute de la pile)
            self.baseTileMap = [ts() for name, ts in hv.element.tiles.tile_sources.items() if name == self.fond_de_carte][0]
            allLayers = self.getAllLayersWithoutBaseMap()
            self.overlays = hv.Overlay() * self.baseTileMap
            self.overlays.update(allLayers)
        else: # on charge le flux WMTS
            self.overlays = hv.Overlay() * [ts() for name , ts in hv.element.tiles.tile_sources.items() if name == self.fond_de_carte][0]

    # surcharge de la methode delOverlay à cause de l'overlay Tile (Tiles currently does not support getitem)
    def delOverlay(self, overlayToDel):
        #ov = self.recursiveOverlayFinderById(tree=self.overlays, overlayId=overlayToDel.id)
        overlaysToSearchIn = self.getAllLayersWithoutBaseMap()
        list = self.findAllPathStringOverlayWithout(overlayToDel)
        #newAttrTree = overlaysToSearchIn.pop('Point')
        if list:
            return overlaysToSearchIn.filter(list)
        else:
            return self.clearAllLayers()

    def findAllPathStringOverlayWithout(self, idToNotKeep):
        pathList = []
        for keys, overlay in self.getAllLayersWithoutBaseMap().data.items():
            if overlay.id != idToNotKeep.id:
                pathList.append('.'.join(keys))
        if len(pathList) != 0:
            return pathList
        else:
            None

    def getAllLayersWithoutBaseMap(self):
        new_attrtree = AttrTree()
        for path, item  in self.overlays.data.items():
            if path[0] != 'Tiles':
                new_attrtree.set_path(path, item)
        return new_attrtree

    def getBaseMap(self):
        new_attrtree = AttrTree()
        for path, item  in self.overlays.data.items():
            if path[0] == 'Tiles':
                new_attrtree.set_path(path, item)
        return new_attrtree

    def getLayer(self,groupName):
        new_attrtree = AttrTree()
        for path, item  in self.overlays.data.items():
            if path[0] == groupName:
                new_attrtree.set_path(path, item)
        return new_attrtree

    def clearAllLayers(self):
        self.overlays = hv.Overlay() * self.baseTileMap



