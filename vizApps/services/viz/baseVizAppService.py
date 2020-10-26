import param
import holoviews as hv
import hvplot.pandas
from holoviews import Overlay, NdOverlay
from holoviews.plotting.links import DataLink

from contextlib import contextmanager
import vizApps.services.viz.VizInstanceService as VizConstructor
import vizApps.services.DataConnectorSevice as connector

# ajout des lib pour l'async
from tornado.ioloop import IOLoop
from concurrent.futures import ThreadPoolExecutor
from vizApps.services.trace.traceParam import TraceParam
from vizApps.services.DataConnectorSevice import LIMIT_PARAM, SAMPLE, FULL

import time
from holoviews.core import AttrTree


from ..testDebug.testDebug import *




executor = ThreadPoolExecutor(max_workers=2)
EMPTY_PLOT = hv.Div("Click UPDATE to load!")


def blocking_function(self, trace, step):


    dataConnector = trace.connectorInterface

    if step >= 1000:
        return self, trace

    # on test si les données n'ont pas déjà été chargé pour un autre viz
    extraParams = {
        "start": step,
        "end": step + LIMIT_PARAM,
        "limit": LIMIT_PARAM
    }
    if dataConnector.connectorType == connector.REST_API:
        trace.loadSliceData(extraParams=extraParams)
    if dataConnector.connectorType == connector.DATABASE:
        trace.loadData()

    return self, trace


class BaseVizApp(param.Parameterized):
    rafraichir =  param.Action(lambda self : self.refreshViz())

    nb_loaded = param.String(default='')
    viewable = param.Boolean(True)
    loaded = param.Boolean(default=False)
    change_state = param.Boolean(True)
    traceSelector = param.ObjectSelector()

    def __init__(self, **params):
        self._session =  params.get("session")
        self.title = params.get("viz_instance").title
        self.overlays = Overlay()
        self.traces = []
        self.tracesParam = []
        self.id = params.get("viz_instance").id
        self.dictParameters = self.get_param_values()
        self.configTracePanel = pn.Column()
        self.configVizPanel = pn.Column()
        self.debugPanel = pn.Column()
        super(BaseVizApp, self).__init__(**params)

    @param.depends("viewable", "loaded","change_state") # ajouter aussi dans les classe heritant de la baseVizApp
    def view(self):

        if self.viewable and not self.loaded :
            # lorque la Viz app est chargé coté client on lance les chargements assynchrone des données FULL
            print("Chargement assynchrone des données ")
            self.tracesLoader(assyncLoading=True)

        if self.viewable != True:
            return

        elif self.viewable :
            print("""
            --------------------
            Rendu du composant {}
            --------------------
            """.format(self))

            return self.getView()

    def getDebugPanel(self):
        self.debugPanel = pn.Column(self.param)
        return self.debugPanel


    def getConfigTracePanel(self):
        return self.configTracePanel

    def getConfigVizPanel(self):
        return self.configVizPanel

   #@param.depends("traceSelector")
   #def traceParamPanel(self):
   #    self.getPanel()
   #    self.param.traceSelector.objects = self.getAllTraceParam()
   #    panel = pn.Column(self.param.traceSelector, expand_button=False, expand=True)
   #    return panel


    def refreshViz(self):
        for trace in self.traces:
            self.doRefreshByTrace(trace)

    def doRefreshByTrace(self, trace):

        overlay = self.configureOverlay(trace)
        self.refreshOverlay(overlay)
        #self.clearAllOverlays()
        #for trace in self.traces:
        self.changeState()


    def doRefreshByTraceParam(self, traceP):

        trace = self.getTraceByTraceParam(traceP)

        overlay = self.configureOverlay(trace)
        self.refreshOverlay(overlay)
        #self.clearAllOverlays()
        #for trace in self.traces:

        self.changeState()

    def changeState(self):
        if self.change_state == True:
            self.change_state = False
        else:
            self.change_state = True


    def formatter(value):
        return str(value)

    def addTrace(self, trace):
        if not trace in self.traces:
            self.traces.append(trace)

    def tracesLoader(self, assyncLoading=True):
        for trace in self.traces:
            self.dataLoader(trace, assyncLoading)
            self.nb_loaded = str(trace.dataFrame.shape[0])
            if not assyncLoading:
                self.setLoaded()
                trace.setReady()

    def dataLoader(self, trace, assyncLoading=True):
        allDataAlreadyGetFromCache = None

        # on regarde d'abord si les full data sont en cache
        trace.configureConnector(FULL)

        if trace.isDataInCache:
            trace.lookCachedData()
            allDataAlreadyGetFromCache = True
        else:
            print("Les données Full ne sont pas en cache")
            # on regarde maintenant si le sample est en cache
            trace.configureConnector(SAMPLE)
            if trace.isDataInCache:
                trace.lookCachedData()
            else:
                print("Les données SAMPLE ne sont pas en cache")
                # sinon on charge les données sample
                trace.loadData()
                trace.finishConnection()



        if trace.getTotalNbEntity == trace.dataFrame.shape[0]:
            # on a toute les données disponible même avec le sample
            allDataAlreadyGetFromCache = True
            self.nb_loaded = str(trace.dataFrame.shape[0])


        if allDataAlreadyGetFromCache:

            #self.refreshAllVizWithSameTrace(trace=trace)
            self.setLoaded()
            trace.setReady()
            self.doRefreshByTrace(trace)
            return
        else:
            overlay = self.configureOverlay(trace=trace)
            self.addOverlay(overlay)
            #self.createAllVizWithSameTrace(trace)

        if assyncLoading == True:
            self.initProgressBarForAllVizWithSameTrace(trace=trace)
            self.assyncLoading(trace)
        else:
            print(trace.dataFrame.head())

    def assyncLoading(self, trace):
        trace.configureConnector(FULL)
        # on va chercher toutes les données en assync

        # tache assynchrone de loading de l'ensemble des entités
        loop = IOLoop.current()
        traceParam = self.getTraceParamByTrace(trace)
        trace.connectorInterface.connector.nbEntityLoaded = 0
        for i in range(0, traceParam.progress.num_tasks):
            future = executor.submit(blocking_function, self, trace=trace, step=i * LIMIT_PARAM)
            loop.add_future(future, self.updateProgressBar)

        loop.add_future(future, self.update)

    def updateProgressBar(self, future):
        trace = future.result()[1]
        traceParam = self.getTraceParamByTrace(trace)

        with pn.io.unlocked():
            traceParam.progress.completed += 1
            if traceParam.progress.completed == traceParam.progress.num_tasks:
                traceParam.progress.reset()
                self.setLoaded()
                trace.setReady()

    def update(self, future):
        trace = future.result()[1]
        viz = future.result()[0]

        #self.refreshAllVizWithSameTrace(trace=trace)

        with pn.io.unlocked():
            self = viz
            # update des reference pour le cache
            trace.connectorInterface.full_data = trace.dataFrame
            #self.setLoaded()
            #trace.setReady()
            #self.refreshAllVizWithSameTrace(trace)
            self.doRefreshByTrace(trace)

    def setLoaded(self):
        if self.loaded == False:
            self.loaded = True
        self.loaded = True

    def configureOverlay(self, trace, viz=None):
        # on ajoute une traceParam à la viz pour pouvoir la manipuler par la suite
        if not viz == None:
            self = viz
        traceP = self.getTraceParamByTrace(trace)
        if not traceP:
            traceP = TraceParam(trace=trace, data=trace.dataFrame, viz=self)
            self.tracesParam.append((trace, traceP))

            self.param.traceSelector.objects = self.getAllTraceParam()
            traceP.populateListeType(trace.dataFrame)

        else:
            # on met à jour le dataframe de la traceP
            traceP.data = traceP.getUpdatedData(trace.dataFrame)


            # dans ce cas on doit aussi rafraichir cette autre viz
        kdims =  []
        overlay = self.createOverlay(traceParam=traceP, label=trace.name)
        overlay.id = trace.id
        if isinstance(overlay, Overlay) or isinstance(overlay, NdOverlay):
            for k, v in overlay.items():
                traceP.overlay = v
        else:
            traceP.overlay = overlay

        self.nb_loaded = str(trace.dataFrame.shape[0])
        return overlay

    def configureOverlayByTraceP(self, traceP, viz=None):
        return


    def recursiveOverlayFinderById(self, tree,overlayId):
        children = tree.get('children')
        for child in children:
            node = tree.get(child)
            if node.id == overlayId:
                return node
            else:
                if hasattr(node,'children'):
                    self.recursiveOverlayFinderById(node, overlayId)
                else:
                    return None



    def addOverlay(self, newOverlay):


        if self.overlays:
            ov = self.recursiveOverlayFinderById(self.overlays, newOverlay.id)

            if ov: # on remplace si l'id existe déja
                precedentOverlays = self.overlays
                self.overlays = precedentOverlays * newOverlay

            #for ov in self.overlays:
            #    if ov.id == newOverlay.id:
            #        ov = newOverlay
            #        return self.overlays
                precedentOverlays = self.overlays
                self.overlays = precedentOverlays * newOverlay
            else:
                self.overlays = self.overlays * newOverlay

        else:
            self.overlays = hv.Overlay() * newOverlay
        return self.overlays

    def delOverlay(self, overlayToDel):
        overlaysToSearchIn = self.getAllOverlay()
        list = self.findAllPathStringOverlayWithout(overlayToDel)
        if list:
            return overlaysToSearchIn.filter(list)
        else:
            return self.clearAllOverlays()

    def clearAllOverlays(self):
        self.overlays = hv.Overlay()

    def getAllOverlay(self):
        new_attrtree = AttrTree()
        for path, item in self.overlays.data.items():
            if path[0] != 'Tiles':
                new_attrtree.set_path(path, item)
        return new_attrtree

    def replaceOverlay(self, overlay, newOverlay):
        self.delOverlay(overlay)
        self.addOverlay(newOverlay)

    def refreshOverlay(self, overlay):
        self.delOverlay(overlay)
        self.addOverlay(overlay)

    def findAllPathStringOverlayWithout(self, idToNotKeep):
        pathList = []
        for keys, overlay in self.overlays.data.items():
            if overlay.id != idToNotKeep.id:
                pathList.append('.'.join(keys))
        return pathList

    def findPathStringOverlayByTraceId(self, overlayId):
        for keys, overlay in self.overlays.data.items():
            if overlay.id == overlayId:
                pathString = '.'.join(keys)
                return pathString

    def setOption(self, option):
        options = hv.Options(option)
        return self.opts(options)


    def getTraceParamByTrace(self, trace):
        for tuple in self.tracesParam:
            if tuple[0] == trace:
                return tuple[1]

    def getTraceByTraceParam(self, traceParam):
        for tuple in self.tracesParam:
            if tuple[1] == traceParam:
                return tuple[0]

    def getAllTraceParam(self):
        return [tuple[1] for tuple in self.tracesParam]


    def refreshAllVizWithSameTrace(self,trace=None):
        vizListe = VizConstructor.getVizByTraceIdAndSessionId(traceId=trace.id, sessionId=self._session)
        for viz in vizListe:
            viz.doRefreshByTrace(trace)


    def createAllVizWithSameTrace(self, trace=None):
        vizListe = VizConstructor.getVizByTraceIdAndSessionId(traceId=trace.id, sessionId=self._session)
        for viz in vizListe:
            overlay = self.configureOverlay(trace=trace, viz=viz)
            viz.addOverlay(overlay)

        if len(vizListe)>1:
            pass
            #DataLink(vizListe[0].overlays.Polygons, vizListe[1].overlays.Polygons)



    def initProgressBarForAllVizWithSameTrace(self,trace=None):
        traceParam = self.getTraceParamByTrace(trace)
        traceParam.progress.num_tasks = trace.getNbRequest




    ############## @abstractmethod

    # abstractMethod
    def createOverlay(self, **kwargs):
        data = kwargs["traceParam"].data
        return data.hvplot()

    def getView(self):
        pass

    def getPanel(self):
        pass