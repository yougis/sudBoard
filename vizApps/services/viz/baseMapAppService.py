from vizApps.services.viz.baseVizAppService import BaseVizApp
import holoviews as hv
import geoviews as gv
import geoviews.tile_sources as gts
import param
from holoviews import opts, Overlay

liste_background = [name[0] for name in hv.element.tiles.tile_sources.items()]

class BaseMapApp(BaseVizApp):
    _opts = opts.defaults()

    overlays = None
    fond_de_carte = param.ObjectSelector(default=liste_background[0], objects=liste_background)
    extent = [(-22,166),(-22.5,166.5)]


    def __init__(self, **params):
        self.changeBaseMap()
        super(BaseMapApp, self).__init__(**params)

    @param.depends('fond_de_carte', watch=True)
    def changeBaseMap(self):
        if self.overlays :
            # on change uniquement le flux WMTS
            self.overlays = [ts() for name, ts in hv.element.tiles.tile_sources.items() if name == self.fond_de_carte][0] * self.overlays.get(len(self.overlays)-1)
        else: # on charge le flux WMTS
            self.overlays = [ts() for name , ts in hv.element.tiles.tile_sources.items() if name == self.fond_de_carte][0]

    def getView(self):
        return self.overlays
