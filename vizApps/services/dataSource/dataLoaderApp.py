import param
import panel as pn
from vizApps.services.dataSource.pipelineDataLoader.stages import ChoiceConnector

class DataLoaderPipeline():


    def __init__(self, **params):
        self.pipeline = pn.pipeline.Pipeline()

    def view(self):
        self.pipeline.add_stage("Connecteur",ChoiceConnector())
        return self.pipeline