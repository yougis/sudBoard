import panel as pn
from vizApps.services.dataSource.pipelineDataLoader.stages import ChoiceSource, ChoiceConnector, ReadData
from intake import open_catalog


def getAppDataLoader(doc):
    pipeline = pn.pipeline.Pipeline(debug=True)
    choiceSource = ChoiceSource()
    pipeline.add_stage("Source de donnée", choiceSource)
    layout = pn.Column(
           pn.Row(pipeline.title, pn.layout.HSpacer(), pipeline.buttons),
           pipeline.stage
       )
    layout.server_doc(doc)

#def getAppDataLoader(doc):
#    # todo if dev/qualif = debug true
#    pipeline = pn.pipeline.Pipeline(debug=True)
#    choiceConnector = ChoiceConnector()
#    pipeline.add_stage("Connecteur", choiceConnector)
#    pipeline.add_stage("", ReadData(connector=choiceConnector.createConnector()))
#
#
#    layout = pn.Column(
#        pn.Row(pipeline.title, pn.layout.HSpacer(), pipeline.buttons),
#        pipeline.network,
#        pipeline.stage
#    )
#
#
#    layout.server_doc(doc)