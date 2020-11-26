import panel as pn
import param
from vizApps.domain.Board import BoardEntity
from vizApps.domain.Trace import TraceEntity
import vizApps.services.viz.VizInstanceService as VizConstructor
from vizApps.services.DataConnectorSevice import ConnectorInterface, SAMPLE, FULL
import os

def getApp(doc):
    vizAppList = getVizAppList(doc)
    layout = pn.Column()
    for vizAppElement in vizAppList:
        layout.append(pn.Row(vizAppElement.view))
        for trace in vizAppElement.tracesParam:
            traceParam = trace[1]
            layout.append(pn.Row(traceParam.view))
    layout.server_doc(doc)

def tabSelectioncallback(target,event):
    target.object = event


def getAppEditMode(doc):
    vizAppList = getVizAppList(doc)
    profileList = []
    layout = pn.Column()
    tabs = None

    for vizAppElement in vizAppList:
        #profileList.append(vizAppElement.trace.dataProfileApp())
        tabs = pn.Tabs((vizAppElement.title, vizAppElement.view ))
        for trace in vizAppElement.traces:
            traceParam = vizAppElement.getTraceParamByTrace(trace)
            tabs.append((trace.name, pn.Row(pn.Column(traceParam.viewProgress,traceParam.view), traceParam.panel)))
            #tabs.link(vizAppElement.traceSelector, callbacks={'value': tabSelectioncallback})

        tabs.append(('Config Viz', vizAppElement.getConfigVizPanel))

        tabs.append(('Debug Viz', vizAppElement.getDebugPanel))

        row = pn.Row(
            tabs
        )
        layout.append(row)


    for profile in profileList:
        pass

    layout.server_doc(doc)

def getVizAppList(doc):
    # recherche de l'entité Viz contenant les informations permettant de construire dynamiquement le panel
    os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
    boardId= doc.session_context.request.headers["board-id"]
    board = getBoard(boardId)
    session = doc.session_context.request.headers['bokeh-session-id'] + boardId

    #init de la liste des viz configurées que nous renvoyons
    vizAppList = []

    # on va chercher toutes les traces qui doivent être affichés sur les différentes viz
    traceListe = TraceEntity.objects.filter(board=board)

    # on stock toutes les différentes viz dans une liste à partir de laquelle nous allons charger les données des traces
    distinctVizListe = []
    # on regroupe les traces qui vont sur le meme VizElement ensemble
    vizListe = []

    for trace in traceListe:
        # on ajoute des proprietés aux traces pour l'assync loading
        trace.initializeLoading()

        for viz in trace.vizListe.all():
            vizListe.append(viz)

        for viz in vizListe:
            if viz in distinctVizListe:
                # on nettoie les instances de viz de la session en mémoire
                #VizConstructor.clearInstancesForSession(session)
                continue
            else:
                distinctVizListe.append(viz)

    # on créer toutes les instances de viz nécéssaire (sans doublons)
    for viz in distinctVizListe:
        vizAppElement = VizConstructor.getVizAppInstancesByVizEntityAndSessionId(viz.id,session)
        if not vizAppElement:
            if not viz.getVizApp:
                # on initialize la viz à partir des parametres Json stockés en base
                viz._vizApp = viz.createVizAppFromJsonParameters(initSession=True,session=session)
            #vizAppElement = viz.getVizApp

    for viz in distinctVizListe:
        # on cherche à nouveau l'instance construite
        vizAppElement = VizConstructor.getVizAppInstancesByVizEntityAndSessionId(viz.id, session)

        # on cherche toutes les traces associés à la viz du même board
        traceEntityListeViz = viz.traceentity_set.filter(board=board)

        for trace in traceEntityListeViz :
            # on récupère l'instance exacte  de la trace commune au board
            for t in traceListe:
                if t == trace:
                    trace = t
                    print(trace,"   ",id(t),  'data Ready: ' ,trace.dataReady)

            vizAppElement.addTrace(trace)

            vizAppElement.param.traceSelector.objects = vizAppElement.getAllTraceParam()
            vizAppListForTrace = []
            vizAppListForTrace.append(vizAppElement)
            if vizAppElement in vizAppList:
                break
            else:
                vizAppList.append(vizAppElement)

        # lors de l'initialisation on charge dans un premier temps les données sample pour un affichage rapide des compossants coté client
        # surtout utile lorsqu'une Trace est chargée dans plusieurs Viz
        #for vizApp in vizAppListForTrace:
        #    for trace in vizApp.traces:
        #        print("vizapp : ", vizApp , "trace: ", trace, '  ', id(trace), 'data Ready: ' ,trace.dataReady)
        #        if trace.dataLoading == True:
        #            while trace.getSample_data.empty:
        #                pass
        #        elif trace.dataReady == True:
        #            pass
        #        else:
        #            vizApp.tracesLoader(assyncLoading=False)

    return vizAppList

def getBoard(id):
    board = BoardEntity.objects.get(id=id)
    return board

def save():
    return "ok"

def clearCache():
    VizConstructor.clearInstances()
    ConnectorInterface.instances.clear()

    return "Cleaned"