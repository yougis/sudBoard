import param
import panel as pn
import holoviews as hv
import hvplot.pandas
from holoviews import  Overlay

from contextlib import contextmanager
import vizApps.services.viz.VizInstanceService as VizConstructor


# ajout des lib pour l'async
from tornado.ioloop import IOLoop
from concurrent.futures import ThreadPoolExecutor
from vizApps.services.viz.progressExtModule import ProgressExtMod
from vizApps.services.DataConnectorSevice import LIMIT_PARAM, SAMPLE, FULL

import time
executor = ThreadPoolExecutor(max_workers=2)
EMPTY_PLOT = hv.Div("Click UPDATE to load!")


def blocking_function(self, step):

    if step > 10000:
        return self

    # on test si les données n'ont pas déjà été chargé pour un autre viz
    extraParams ={
        "start" : step,
        "end" : step + LIMIT_PARAM,
        "limit": LIMIT_PARAM
    }
    self.trace.loadSliceData(extraParams=extraParams)
    return self



class BaseVizApp(param.Parameterized):
    nb_Loaded = param.String(default='')

    def __init__(self, **params):
        self.overlays = Overlay()
        self.trace = None
        self.sample = None
        self.id = params.get("viz_instance").id
        self.dictParameters = self.get_param_values()
        self.progress = ProgressExtMod()
        self.progression = self.progress.view
        super(BaseVizApp, self).__init__(**params)

    def formatter(value):
        return str(value)

    def addTrace(self, trace):
        self.trace = trace

    def dataLoader(self):

        allDataAlreadyGetFromCache = None

        # on regarde d'abord si les full data sont en cache
        self.trace.configureConnector(FULL)

        if self.trace.isDataInCache:
            self.trace.lookCachedData()
            allDataAlreadyGetFromCache = True
        else:
            # on regarde maintenant si le sample est en cache
            self.trace.configureConnector(SAMPLE)
            if self.trace.isDataInCache:
                self.trace.lookCachedData()
            else:
                # sinon on charge les données sample
                self.trace.loadData()
                self.trace.finishConnection()


        self.createAllVizWithSameTrace()


        if allDataAlreadyGetFromCache:
            return
        else:
            self.trace.configureConnector(FULL)
            # on va chercher toutes les données en assync

            # tache assynchrone de loading de l'ensemble des entités
            loop = IOLoop.current()
            for i in range(0, self.progress.num_tasks):
                future = executor.submit(blocking_function, self, i * LIMIT_PARAM)
                loop.add_future(future, self.update)

    def createAndAddOverlayFromData(self,data, viz=None):
        if not viz == None:
            self = viz
        overlay = self.createOverlay(data=data)
        overlay.id = self.trace.id
        self.addOverlay(overlay)

    def createAndRefreshOverlayFromData(self,data,viz=None):
        if not viz == None:
            self = viz
        overlay = self.createOverlay(data=data)
        overlay.id = self.trace.id
        self.nb_Loaded = str(self.trace.data.shape[0])
        self.refreshOverlay(overlay=overlay)

    def addOverlay(self,newOverlay):
        if self.overlays:
            precedentOverlays = self.overlays
            self.overlays = precedentOverlays * newOverlay
        else:
            self.overlays = self.overlays * newOverlay
        return self.overlays

    def delOverlay(self, overlayToDel):
        list = self.findAllPathStringOverlayWithout(overlayToDel)
        if list:
            return self.filter(list)
        else:
            self.overlays = hv.Overlay()

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

    @param.depends("nb_Loaded")
    def view(self):
        return self.getView()

    #@abstractmethod
    def getView(self):
        pass

    def setOption(self, option):
        options= hv.Options(option)
        return self.opts(options)

    def createOverlay(self,**kwargs):
        data = kwargs["data"]
        return data.hvplot()

    def update(self, future):
        self.refreshAllVizWithSameTrace()

        with pn.io.unlocked():
            self = future.result()
            # update des reference pour le cache
            dataConnector = self.trace.getConnector()
            dataConnector.full_data = self.trace.data

    def createAllVizWithSameTrace(self):
        for viz in VizConstructor.getVizByTraceIdAndSessionId(self, traceId=self.trace.id, sessionId=self._session):
            self.createAndAddOverlayFromData(data=self.trace.data, viz=viz)
            self.initProgressBarForAllVizWithSameTrace(viz=viz)

    def refreshAllVizWithSameTrace(self):
        for viz in VizConstructor.getVizByTraceIdAndSessionId(self, traceId=self.trace.id, sessionId=self._session):
            self.createAndRefreshOverlayFromData(data=self.trace.data, viz=viz)
            self.updateAllProgressBarWithSameTrace(viz=viz)

    def initProgressBarForAllVizWithSameTrace(self,viz=None):
        if not viz == None:
            self = viz

        self.progress = self.trace.progressBar
        self.progression = self.progress.view
        self.progress.completed == 0
        self.progress.num_tasks = self.trace.getNbRequest


    def updateAllProgressBarWithSameTrace(self, viz=None):
        if not viz == None:
            self = viz
        self.progress.completed += 1
        if self.progress.completed == self.progress.num_tasks:
            self.trace.finishConnection()
            self.progress.reset()