import param
import pandas as pd
import movingpandas as mpd
# data Type

#import des wrappers data -> HoloView

#libs plot
import geoviews.tile_sources as gts
import holoviews as hv
import hvplot.pandas

# libs carto

# class vizApp
from vizApps.domain.TypeVizEnum import TypeVizEnum

#crsRgnc = ccrs.LambertConformal(central_longitude=166,
#                                standard_parallels=(-20.66666666666667, -22.33333333333333),
#                                central_latitude=-21.5,
#                                false_easting=400000,
#                                false_northing=300000,
#                                cutoff=0,
#                                globe=ccrs.Globe(ellipse='GRS80'))
#
#epsg3163 = pyepsg.get(3163)
#proj4jRGNC = epsg3163.as_proj4().strip()
#bound =  epsg3163.domain_of_validity()
#proj4CRS = CRS.from_proj4(proj4jRGNC)

#dic = {'Commune':'/ref/dittt/CommuneNC', 'Adresse':'/ref/serail/Adresse'}

#datasourceListe =[]
#for key in dic:
#    datasourceListe.append(key)
#
maillage = ["ISEE","Commune","Province"]


#class DataSource(param.Parameterized):
#   instances = []
#   dataSourceCatalogue = param.ObjectSelector(default=datasourceListe[1], objects=datasourceListe)
#   dataFrame = pd.DataFrame()
#   dataFrameInstancies = []

#   #json = {"connector": "RestApi","url":""}
#   #dataConnector = ConnectorInterface(json=json)
#   labelGeom = None

#   def __init__(self, name="haha", **params):
#       super(DataSource, self).__init__(**params)
#       DataSource.instances.append(self)

#   def refreshDataFrame(self):
#       # faire un check si la donnée doit être rafraichie ou non
#       extraParams = []
#       dataFrameInsatance = self.checkIfAlredayLoad(self.dataSourceCatalogue)

#       if len(dataFrameInsatance)==0:
#           self.dataFrame = self.setDataFrame(self.dataConnector,extraParams)
#       else:
#           self.dataFrame = dataFrameInsatance[0][1]

#   def checkIfAlredayLoad(self,dataSourceCatalogue):
#       return [inst for inst in self.dataFrameInstancies if inst[0] == dataSourceCatalogue]


#   def getUrlFromDataSourceSelector(self, selected):
#       url = dic[selected]
#       return url


#   def setDataFrame(self, dataConnector,extraParams=[]):
#       #self.dataConnector = dataConnector
#       #extraParams = extraParams
#       # on va chercher l'url de lobjectSelector
#       #url = self.getUrlFromDataSourceSelector(selected=self.dataSourceCatalogue)
#       url = self.getUrlFromDataSourceSelector(selected=self.dataSourceCatalogue)
#       #self.dataFrame = dataConnector.getDataFromUrlPandaDataframe(url=url,extraParams=extraParams)
#       self.dataFrame = dataConnector()
#       labelGeom = dataConnector.isDataFrameHasGeom(self.dataFrame)

#       if labelGeom:
#           #on recupère l'EPSG
#           metaGeom =  dataConnector.getMetaGeomFromDataFrame(self.dataFrame[labelGeom])
#           epsg = "epsg:"+metaGeom[0][1]
#           #on clean la geom pour avoir un WKT
#           self.dataFrame = dataConnector.cleanGeomWKT(df=self.dataFrame, meta=metaGeom,labelGeom=labelGeom)
#           labelGeom = "geometry" # maintenant c'est geometry pour etre compatible avec la classe GeomDictInterface

#           self.dataFrame[labelGeom] = self.dataFrame[labelGeom].apply(wkt.loads)
#           crs_proj4 = crsRgnc.proj4_init

#           gdf = gpd.GeoDataFrame(self.dataFrame, geometry=labelGeom , crs=crs_proj4)
#           #gdf = gdf.to_crs(crs_proj4)
#           self.dataFrame = gdf

#       DataSource.dataFrameInstancies.append((self.dataSourceCatalogue,self.dataFrame))
#       return self.dataFrame

#   def _getByName(cls, name):
#       return [inst for inst in cls.instances if inst.name==name][0]

vizInstancesList = []

def getVizInstancesById(id):
    #instance = [inst for inst in cls.instances if inst.id == id]
    instance = [inst for inst in vizInstancesList if inst.id == id]
    if len(instance)>=1:
        return instance[0]  # on renvoit uniquement un objet
    return None

#dataSource = [DataSource(),DataSource("tata")]

class BaseVizConstructor(param.Parameterized):

    def __init__(self, **params):
        self.overlays = None
        self.id = params["id"]
        super(BaseVizConstructor, self).__init__(**params)

    def formatter(value):
        return str(value)

    def connectTraceToViz(self,trace):
        viz = self
        trace.loadData()
        overlay = self.createViz(trace.data)
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

class BarGraphConstructor(BaseVizConstructor):

    def __init__(self, **params):
        self.type = TypeVizEnum.BAR_GRAPH
        vizInstancesList.append(self)
        super(BarGraphConstructor, self).__init__(**params)

    def getView(self):
        return self.overlays

    def createViz(self,data):
        #data = pd.DataFrame(data)
        return data.hvplot.table(['numero'])





class MapConstructor(BaseVizConstructor):
    overlays = gts.OSM()

    def __init__(self, **params):
        super(MapConstructor, self).__init__(**params)

    def changeBaseMapToOSM(self):
        self.overlays = gts.OSM()

    def getView(self):
        return self.overlays


class ChoroplethMapConstructor(MapConstructor):
    maillageChoice = param.ObjectSelector(default=maillage[0], objects=maillage)
    selector = param.Selector(objects=["red", "yellow", "green"])
    num = param.Number()

    def __init__(self, **params):
        self.type = TypeVizEnum.CHOROPLETH_MAP
        vizInstancesList.append(self)
        super(ChoroplethMapConstructor, self).__init__(**params)

    def getView(self):
       self.overlays = self.overlays.opts(active_tools=['pan','wheel_zoom','lasso_select','box_select'])
       return self.overlays

    def createViz(self,data):
        return data.hvplot(tiles=True)


   #@param.depends('datasource','datasource.dataSourceCatalogue')
   #def mapViewer(self):
   #    # hack pour ne pas conserver les nouveaux watchers créés à chaque ouverture de page (bug watcher subobject)
   #    popWatcher(self.param.datasource.watchers)
   #    popWatcher(self.datasource.param.dataSourceCatalogue.watchers)

   #    self.datasource.refreshDataFrame()
   #    if self.datasource.dataFrame.empty:
   #       self.datasource.dataFrame = self.datasource.setDataFrame(self.datasource.dataConnector)
   #       if self.datasource.dataFrame.empty:
   #           return "Aucune source de donnée"

   #    isGeo = self.datasource.dataConnector.isDataFrameHasGeom(self.datasource.dataFrame)


   #    if isGeo:
   #        dataFrame = self.datasource.dataFrame.to_crs("EPSG:3857")
   #        geo_bg = gv.tile_sources.EsriImagery.options(alpha=0.6, bgcolor="black")
   #        point = dataFrame.hvplot().opts(active_tools=['pan','wheel_zoom'])
   #        return gts.EsriImagery()*point
   #    else:
   #        return "Impossible d'afficher les données sur la carte car La source de donnée n'a pas de géometrie reconnue"

   #def changeDataSource(self):
   #    self.datasource.dataFrame = self.setDataSource(dataConnector=self.dataConnector)




def popWatcher(watcher):
    if watcher:
        if len(watcher['constant'])>=1:
            watcher['constant'].pop()
            watcher['precedence'].pop()
            watcher['label'].pop()
            watcher['objects'].pop()
            if watcher.get('value') is not None:
                watcher['value'].pop()
                watcher['value'].pop()



