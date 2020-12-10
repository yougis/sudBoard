import yaml
from vizApps.domain.Board import BoardEntity
from vizApps.domain.Trace import TraceEntity

from lumen.filters import ConstantFilter, Filter, WidgetFilter # noqa
from lumen.monitor import Monitor # noqa
from lumen.sources import Source, RESTSource # noqa
from lumen.transforms import Transform # noqa
from lumen.views import View # noqa
from lumen.dashboard import Dashboard


instancesList = []

class LumenDashboard():
    def __init__(self, *args,**kwargs):
        self.board = BoardEntity.objects.get(id=kwargs['board'])
        self.traceListe = TraceEntity.objects.filter(board=kwargs['board'])
        specDoc = self.createSpecYamlFromData()
        self.dashBoard = Dashboard(specification=specDoc.name)
        self._session = kwargs.get('sessionId')
        instancesList.append(self)

    def createSpecYamlFromData(self):
        config = {'config':{'title':"Test DashBoard",'layout': "grid",'ncols':1, 'template':'material'}}
        targets = {'targets':[
            { 'title': '"southern_rockies"',
              "source": {'type': 'intake',
                         'filename': '/home/yogis/Apps/psud/sudBoard/vizApps/services/lumen/catalog.yml'},
              'views': [{'table': 'southern_rockies', 'type': 'hvplot', 'kind': 'scatter','x': 'pop','y': 'sup', 'by': 'island'}]},
            #{'source': 'gere', 'title': '"1"',
            # 'views': [{'field': 'geom', 'table': 'gere', 'type': 'hvplot', 'kind': 'scatter'}]}
#
        ]}
        sources={}
        #sources = {'sources':{'population':{'files': ['population.csv'], 'type': 'file'}}}
        #sources = {
        #    'sources':
        #        {
        #            'population1': {'files': ['population.csv'], 'type': 'file'},
        #        }
        #}
        specification = {**config,**targets,**sources}

        with open(r'specYamlFile/dashboard.yml', 'w') as file:
            yaml.dump(specification, file)
            return file

    @classmethod
    def getinstancesBySessionId(cls,sessionId):
        instances = [inst for inst in instancesList if inst._session == sessionId]
        if len(instances)>=1:
            return instances
        return None

    @classmethod
    def clearInstancesForSession(cls,sessionId):
        instances = [inst for inst in instancesList if inst._session == sessionId]
        for i in instances:
            instancesList.remove(i)
