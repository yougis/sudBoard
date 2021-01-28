import panel as pn
from vizApps.services.dataSource.pipelineDataLoader.stages import ChoiceConnector, ReadData

def getAppSourceConnector(doc):
    # todo if dev/qualif = debug true
    pipeline = pn.pipeline.Pipeline(debug=True)
    # on choisi le type de connecteur (DB, FILE, WEB)
    # on prend la liste des source dans les catalogues Intake
    choiceConnector = ChoiceConnector()
    pipeline.add_stage("Connecteur", choiceConnector)
    pipeline.add_stage("", ReadData(connector=choiceConnector.createConnector()))


    layout = pn.Column(
        pn.Row(pipeline.title, pn.layout.HSpacer(), pipeline.buttons),
        pipeline.network,
        pipeline.stage
    )


    layout.server_doc(doc)