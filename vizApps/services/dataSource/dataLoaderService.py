import panel as pn
from vizApps.services.dataSource.pipelineDataLoader.stages import ConnectSource
from intake import open_catalog


def getAppDataLoader(doc):
    pipeline = pn.pipeline.Pipeline(debug=True)
    connectSource = ConnectSource()
    pipeline.add_stage("Connecter une source de donnée", connectSource)
    layout = pn.Column(
           pn.Row(pipeline.title, pn.layout.HSpacer(), pipeline.buttons),
           pipeline.stage
       )
    layout.server_doc(doc)
