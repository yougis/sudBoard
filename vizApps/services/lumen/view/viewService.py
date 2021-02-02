import panel as pn
import param
from vizApps.services.dataSource.pipelineDataLoader.stages import ChoiceTarget, ChoiceSource, StepTransform, StepConfiguration, StepSaveView
from vizApps.services.board.BoardService import getLumenDashBoard
from lumen.monitor import Monitor

def getAppViewCreator(doc):
    # todo if dev/qualif = debug true
    pipeline = pn.pipeline.Pipeline(debug=True)
    lumenDashboard = getLumenDashBoard(doc)
    monitors = lumenDashboard.dashBoard._targets
    target_list =  [monitor for monitor in monitors]
    sources_list = getUniqueSourcesFromMonitors(target_list)
    choiceSource = ChoiceSource(liste_des_sources = sources_list)
    stepTransform = StepTransform(lumenDashboard=lumenDashboard)

    #choiceTarget = ChoiceTarget(liste=[t.name for t in target_list])
    pipeline.add_stage("Séléction d'une source de donnée", choiceSource)
    pipeline.add_stage("Transformer la donnée", stepTransform)
    pipeline.add_stage("Configuration du graphique", StepConfiguration(lumenDashboard=lumenDashboard))
   # newTarget = Monitor(name='Nouveau moniteur')
#
   # target_list.append(newTarget)
    pipeline.add_stage("Terminer", StepSaveView(lumenDashboard=lumenDashboard, targets=[t for t in target_list], url=doc.session_context.request.headers['referer']))
    #pipeline.add_stage("Choix du conteneur", choiceTarget)
    layout = pn.Column(
        pn.Row(pipeline.title, pn.layout.HSpacer(), pipeline.buttons),
        pipeline.stage
    )
    layout.server_doc(doc)

def getUniqueSourcesFromMonitors(monitors):
    sources_list = [m.source.cat for m in monitors]
    unique_sources_list = []
    [unique_sources_list.append(cat) for cat in sources_list if cat not in unique_sources_list]

    return unique_sources_list






