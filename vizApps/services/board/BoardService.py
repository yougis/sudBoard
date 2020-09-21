import panel as pn

from vizApps.domain.Board import BoardEntity
from vizApps.domain.Trace import TraceEntity
import vizApps.services.viz.VizInstanceService as VizConstructor

import os


def getApp(doc):
    vizAppList = getVizAppList(doc)[0]
    row = pn.Row()
    for vizAppElement in vizAppList:
        row.append(vizAppElement.view)
    row.server_doc(doc)

def getAppEditMode(doc):
    vizAppList = getVizAppList(doc)[0]
    profileList = getVizAppList(doc)[1]
    row = pn.Row()
    for vizAppElement in vizAppList:
        row.append(pn.Row(vizAppElement.view,pn.Tabs(("Parametres", vizAppElement))))

    for profile in profileList:
        row.append(pn.pane.HTML(profile.html))
    row.server_doc(doc)

def getVizAppList(doc):
    # recherche de l'entité Viz contenant les informations permettant de construire dynamiquement le panel
    os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
    board = getBoard(doc.session_context.request.headers["board-id"])
    session = doc.session_context.request.headers['bokeh-session-id']

    traceListe = TraceEntity.objects.filter(board=board)

    vizAppList = []
    profileList = []

    for trace in traceListe:
        # on regroupe les traces qui vont sur le meme VizElement ensemble
        vizListe = trace.vizListe.all()


        for viz in vizListe:
            vizAppElement = createVizAppElement(trace=trace, vizEntity=viz, session=session)
            vizAppElement._session = session
            if vizAppElement in vizAppList:
                break
            else:
                vizAppList.append(vizAppElement)

        profileList.append(trace.dataProfileApp())

    return vizAppList, profileList

def getBoard(id):
    board = BoardEntity.objects.get(id=id)
    return board

def createVizAppElement(trace, vizEntity, session):
    vizAppElement = vizEntity.getVizApp
    vizAppElement.connectTraceToViz(trace)
    VizConstructor.setVizAppInstancesSessionfromId(id(vizAppElement), session)
    return vizAppElement

def save():
    return "ok"

def clearCache():
    VizConstructor.clearInstances()
    return "Cleaned"