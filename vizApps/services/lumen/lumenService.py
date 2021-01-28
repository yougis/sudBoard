import os
import yaml
from lumen.dashboard import Dashboard
from lumen.filters import ConstantFilter, Filter, WidgetFilter  # noqa
from lumen.monitor import Monitor  # noqa
from lumen.sources import Source, RESTSource  # noqa
from lumen.transforms import Transform  # noqa
from lumen.views import View  # noqa

from sudBoard.settings import BASE_DIR
from vizApps.domain.Board import BoardEntity

from vizApps.services.lumen.util import SpecYamlCreator
from vizApps.domain.lumen.view import ViewEntity
from vizApps.domain.lumen.target import TargetEntity

import vizApps.services.intake

intakeSourceName = 'sql_auto'

instancesList = []


class LumenDashboard:
    def __init__(self, **kwargs):
        boardId=kwargs['board']

        self.board = BoardEntity.objects.get(id=boardId)
        self._session = kwargs.get('sessionId')+ str(boardId)
        self.specDoc = self.createSpecFromData()
        self.dashBoard = Dashboard(specification=self.specDoc.name)
        instancesList.append(self)

    def createSpecFromData(self):

        if self.board.config:
            specification = self.board.config
            with open(r'specYamlFile/dashboard_{}.yml'.format(self._session), 'w') as file:
                yaml.dump(specification, file)
            return file
        else:
            specification = self.createFakeYaml()
            with open(r'specYamlFile/dashboard_fake_{}.yml'.format(self._session), 'w') as file:
                yaml.dump(specification.__dict__, file)
            return file



    def createFakeYaml(self):
        path = BASE_DIR + '/vizApps/services/intake/'
        config = {'title': "Nouveau DashBoard", 'layout': "grid", 'ncols': 2, 'template': 'material',
                  'theme': 'dark'}
        targets = [
            {
            'title': 'Nouvelle Source',
            "source": {'type': 'intake',
                       'filename': os.path.join(path, 'catalog.yml')},
            'views': [
            ],
            'filters': [
            ]
        },
        ]
        specObj = SpecYamlCreator(config=config, targets=targets)
        return specObj


    def createSpecYaml(self):
        path = BASE_DIR + '/vizApps/services/intake/'
        config = {'config': {'title': "Nouveau DashBoard", 'layout': "grid", 'ncols': 2, 'template': 'material','theme': 'dark'},
                  'targets': [
                      {'title': 'Nouvelle source',
                       'source': {'type': 'intake',
                                  'filename': os.path.join(path, 'catalog.yml')}
                       }]
                  }

        targets = {'targets': [
            {'title': '"aloooo"',
             "source": {'type': 'intake',
                        'filename': os.path.join(path, 'catalog.yml')},
             'views': [
                 {
                     'table': intakeSourceName,
                     'type': 'hvplot',
                     'kind': 'bar',
                     'transforms':
                         [
                             {
                                 'type': 'aggregate',
                                 'by':'Etat administratif',
                                 'columns' : ['Débit de prélèvement  maximum autorisé m3/J'],
                                 'method':'sum'
                             }
                         ]

                 },
                 {
                     'table': intakeSourceName,
                     'type': 'hvplot',
                     'kind': 'scatter',


                 }

             ],
             'filters':[
                 {
                     'field': 'Etat administratif',
                     'type': 'widget',
                     'multi': True,
                     'empty_select': True
                 },

                 {
                     'field': 'Débit de prélèvement  maximum autorisé m3/J',
                     'type': 'widget',
                     'multi': True,
                     'empty_select': True
                 }
             ]
             },
            {'title': '"deusee"',
             "source": {'type': 'intake',
                        'filename': os.path.join(path, 'catalog.yml')},
             'views': [
                 {
                     'table': intakeSourceName,
                     'type': 'hvplot',
                     'kind': 'bar',
                     'transforms':
                         [
                             {
                                 'type': 'aggregate',
                                 'by': 'Etat administratif',
                                 'columns': ['Débit de prélèvement  maximum autorisé m3/J'],
                                 'method': 'mean'
                             }
                         ]

                 }

             ],
             'filters': [
                 {
                     'field': 'Etat administratif',
                     'type': 'widget',
                     'multi': True,
                     'empty_select': True
                 },

                 {
                     'field': 'Débit de prélèvement  maximum autorisé m3/J',
                     'type': 'widget',
                     'multi': True,
                     'empty_select': True
                 }
             ]
             },

            {'title': '"troisse"',
             "source": {'type': 'intake',
                        'filename': os.path.join(path, 'catalog.yml')},
             'views': [
                 {
                     'table': intakeSourceName,
                     'type': 'hvplot',
                     'kind': 'bar',
                     'transforms':
                         [
                             {
                                 'type': 'aggregate',
                                 'by': 'Etat administratif',
                                 'columns': ['Débit de prélèvement  maximum autorisé m3/J'],
                                 'method': 'mean'
                             }
                         ]

                 },
                 {
                     'table': intakeSourceName,
                     'type': 'hvplot',
                     'kind': 'scatter',


                 }

             ],
             'filters': [
                 {
                     'field': 'Etat administratif',
                     'type': 'widget',
                     'multi': True,
                     'empty_select': True
                 },

                 {
                     'field': 'Débit de prélèvement  maximum autorisé m3/J',
                     'type': 'widget',
                     'multi': True,
                     'empty_select': True
                 }
             ]
             }
            #
        ]}
        sources = {}
        # sources = {'sources':{'population':{'files': ['population.csv'], 'type': 'file'}}}
        # sources = {
        #    'sources':
        #        {
        #            'population1': {'files': ['population.csv'], 'type': 'file'},
        #        }
        # }

        target_new = {'targets': [
            {'title': 'Nouvelle donnée',
             "source": {'type': 'intake',
                        'filename': os.path.join(path, 'catalog.yml')}
             }]}

        specification = {**config,**targets,**sources}

        transform_ex = [
                             {
                                 'type': 'aggregate',
                                 'by': 'Etat administratif',
                                 'columns': ['Type ouvrage'],
                                 'method': 'mean'
                             }
                         ]



        view = yaml.dump(SpecYamlCreator(table='test', type='hvplot', kind='tt',trasforms=transform_ex))

        with open(r'specYamlFile/nouveau_dashboard_default_config.yml', 'w') as file:
            yaml.dump(specification, file)
            return file

    @classmethod
    def getinstancesBySessionId(cls, sessionId):
        instances = [inst for inst in instancesList if inst._session == sessionId]
        if len(instances) >= 1:
            return instances
        return None

    @classmethod
    def clearInstancesForSession(cls, sessionId):
        instances = [inst for inst in instancesList if inst._session == sessionId]
        for i in instances:
            instancesList.remove(i)
