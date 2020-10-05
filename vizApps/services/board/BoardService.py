import panel as pn
from vizApps.domain.Board import BoardEntity
from vizApps.domain.Trace import TraceEntity
import vizApps.services.viz.VizInstanceService as VizConstructor
from vizApps.services.DataConnectorSevice import ConnectorInterface, SAMPLE, FULL
import os

def getApp(doc):
    vizAppList = getVizAppList(doc)
    layout = pn.Column()
    for vizAppElement in vizAppList:
        vizAppElement.dataLoader()
        layout.append(pn.Row(pn.Column(vizAppElement.view, vizAppElement.progression)))
    layout.server_doc(doc)

def getAppEditMode(doc):
    vizAppList = getVizAppList(doc)
    profileList = []
    layout = pn.Column()

    for vizAppElement in vizAppList:

        #profileList.append(vizAppElement.trace.dataProfileApp())
        # on reboucle pour effectuer la chargement des viz qui ont été intialiser avec les traces
        #vizAppElement.dataLoader()
        layout.append(pn.Row(pn.Column(vizAppElement.view, vizAppElement.progression), pn.Tabs(("Parametres", vizAppElement))))

    for profile in profileList:
        pass
        #layout.append(pn.Row(pn.pane.HTML(profile.html)))
    layout.server_doc(doc)


def getVizAppList(doc):
    # recherche de l'entité Viz contenant les informations permettant de construire dynamiquement le panel
    os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
    board = getBoard(doc.session_context.request.headers["board-id"])
    session = doc.session_context.request.headers['bokeh-session-id']

    traceListe = TraceEntity.objects.filter(board=board)

    vizAppList = []


    for trace in traceListe:
        # on regroupe les traces qui vont sur le meme VizElement ensemble
        vizListe = trace.vizListe.all()

        trace.manual_init()

        vizAppListForTrace = []

        for viz in vizListe:

            vizAppElement = createVizAppElement(trace=trace, vizEntity=viz, session=session)
            vizAppElement._session = session
            vizAppListForTrace.append(vizAppElement)
            if vizAppElement in vizAppList:
                break
            else:
                vizAppList.append(vizAppElement)

        for vizApp in vizAppListForTrace:
            if vizApp.trace.dataLoading == True:
                while trace.getSample_data.empty:
                    pass
            else:
                vizApp.dataLoader()

    return vizAppList

def getBoard(id):
    board = BoardEntity.objects.get(id=id)
    return board

def createVizAppElement(trace, vizEntity, session):
    vizAppElement = vizEntity.getVizApp
    vizAppElement.addTrace(trace)
    VizConstructor.setVizAppInstancesSessionfromId(id(vizAppElement), session)
    return vizAppElement

def save():
    return "ok"

def clearCache():
    VizConstructor.clearInstances()
    ConnectorInterface.instances.clear()

    return "Cleaned"