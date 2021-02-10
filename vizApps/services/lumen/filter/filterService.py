from . import *
from vizApps.services.board.BoardService import getLumenDashBoard

def getAppFilter(doc):
    # todo if dev/qualif = debug true
    pipeline = pn.pipeline.Pipeline(debug=True)
    lumenDashboard = getLumenDashBoard(doc)
    monitors = lumenDashboard.dashBoard._targets
    target_list =  [monitor for monitor in monitors]
    choiceTarget = ChoiceTarget(liste=target_list)
    stepFilter = StepFilter(lumenDashboard=lumenDashboard)

    pipeline.add_stage("Séléction de la cible du filtre", choiceTarget)
    pipeline.add_stage("Configuration du filtre", stepFilter)
    pipeline.add_stage("Terminer", StepSave(lumenDashboard=lumenDashboard, targets=[t for t in target_list], url=doc.session_context.request.headers['referer']))
    layout = pn.Column(
        pn.Row(pipeline.title, pn.layout.HSpacer(), pipeline.buttons),
        pipeline.stage
    )
    layout.server_doc(doc)

def getUniqueSourcesFromMonitors(monitors):
    sources_list = [m.source for m in monitors]
    unique_sources_list = []
    [unique_sources_list.append(source) for source in sources_list if source not in unique_sources_list]

    return sources_list






