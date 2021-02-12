from . import *
from vizApps.services.board.BoardService import getLumenDashBoard

def getAppViewCreator(doc):
    # todo if dev/qualif = debug true
    pipeline = pn.pipeline.Pipeline(debug=True)
    lumenDashboard = getLumenDashBoard(doc)
    monitors = lumenDashboard.dashBoard._targets
    target_list =  [monitor for monitor in monitors]
    sources_list = getUniqueSourcesFromMonitors(target_list)
    choiceSource = ChoiceSource(liste_des_sources = sources_list)
    stepTransform = StepTransform(lumenDashboard=lumenDashboard)

    pipeline.add_stage("Séléction d'une source de donnée", choiceSource)
    pipeline.add_stage("Transformer la donnée", stepTransform)
    pipeline.add_stage("Configuration du graphique", StepConfiguration(lumenDashboard=lumenDashboard))

    pipeline.add_stage("Terminer", StepSaveView(lumenDashboard=lumenDashboard, targets=[t for t in target_list], url=doc.session_context.request.headers['referer']))
    layout = pn.Column(
        pn.Row(pipeline._stage, pn.layout.HSpacer(), pipeline.buttons),
        pipeline.stage,
        sizing_mode='stretch_width',
        width_policy='max'
    )
    layout.server_doc(doc)

def getUniqueSourcesFromMonitors(monitors):
    sources_list = [m.source for m in monitors]
    unique_sources_list = []
    [unique_sources_list.append(source) for source in sources_list if source not in unique_sources_list]

    return sources_list






