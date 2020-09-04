import panel as pn

from vizApps.domain.Board import BoardEntity
from vizApps.domain.Trace import TraceEntity
import vizApps.services.VizConstructorService as VizConstructor

import os


sessionsInstances=[]

def getApp(doc):
    vizAppList = getVizAppList(doc)
    row = pn.Row()
    for vizAppElement in vizAppList:
        row.append(vizAppElement.view)
    row.server_doc(doc)

def getAppEditMode(doc):
    vizAppList = getVizAppList(doc)
    row = pn.Row()
    for vizAppElement in vizAppList:
        row.append(pn.Row(vizAppElement.view,pn.Tabs(("Parametres", vizAppElement))))
    row.server_doc(doc)

def getVizAppList(doc):
    # recherche de l'entité Viz contenant les informations permettant de construire dynamiquement le panel
    os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
    board = getBoard(doc.session_context.request.headers["board-id"])

    traceListe = TraceEntity.objects.filter(board=board)

    vizAppList = []

    initSession = True

    for trace in traceListe:
        # on regroupe les traces qui vont sur le meme VizElement ensemble
        vizListe = trace.vizListe.all()

        for viz in vizListe:
            vizAppElement = createVizAppElement(trace=trace, vizEntity=viz, initSession=initSession)
            viz._viz['vizApp'] = vizAppElement
            if vizAppElement in vizAppList:
                break
            else:
                vizAppList.append(vizAppElement)
            initSession = False
    VizConstructor.vizInstancesList.clear()
    return vizAppList

def getBoard(id):
    board = BoardEntity.objects.get(id=id)
    return board

def createVizAppElement(trace, vizEntity, initSession):
    VizAppElement = vizEntity.createVizFromJsonParameters(initSession)

    VizAppElement.connectTraceToViz(trace)

    return VizAppElement

def save():
    return "ok"