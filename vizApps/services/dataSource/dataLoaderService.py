import panel as pn
import param
from vizApps.services.dataSource.dataLoaderApp import DataLoaderPipeline
from vizApps.services.dataSource.pipelineDataLoader.stages import ChoiceConnector, ReadData

def getAppDataLoader(doc):
    pipeline = pn.pipeline.Pipeline(debug=True)
    choiceConnector = ChoiceConnector()
    pipeline.add_stage("Connecteur", choiceConnector)
    pipeline.add_stage("", ReadData(connector=choiceConnector.createConnector()))


    layout = pn.Column(
        pn.Row(pipeline.title, pn.layout.HSpacer(), pipeline.buttons),
        pipeline.network,
        pipeline.stage
    )


    layout.server_doc(doc)