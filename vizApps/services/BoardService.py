import panel as pn

from vizApps.domain.Board import BoardEntity
from vizApps.domain.Trace import TraceEntity
import vizApps.services.VizConstructorService as VizConstructor

import os

class bokehSession():
    def __init__(self, **params):
        self.id = params['id']
        self.initial = True


sessionsInstances=[]

def getApp(doc):
    # recherche de l'entité Viz contenant les informations permettant de construire dynamiquement le panel
    os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
    board = getBoard(doc.session_context.request.headers["board-id"])
    bokehSessionId = doc.session_context.request.headers['bokeh-session-id']

    traceListe = TraceEntity.objects.filter(board=board)

    vizAppList = []

    initSession = True

    for trace in traceListe:
        #on regroupe les traces qui vont sur le meme VizElement ensemble
        vizListe = trace.vizListe.all()

        for viz in vizListe:
            vizApp = createVizAppElement(trace=trace, vizEntity=viz,initSession=initSession)

            if vizApp in vizAppList:
                break
            else:
                vizAppList.append(vizApp)

            initSession = False
    VizConstructor.vizInstancesList.clear()
    row = pn.Row()

    for vizElement in vizAppList:
        row.append(pn.Tabs((str(vizElement.id),vizElement.view()),("parametres",vizElement)))


    row.server_doc(doc)

def getBoard(id):
    board = BoardEntity.objects.get(id=id)
    return board

def createVizAppElement(trace, vizEntity, initSession):
    VizAppElement = vizEntity.createVizFromJsonParameters(initSession)

    VizAppElement.connectTraceToViz(trace)

    return VizAppElement