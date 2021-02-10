import os
import yaml
import panel as pn
import param
from lumen.dashboard import Dashboard
from lumen.filters import ConstantFilter, Filter, WidgetFilter  # noqa
from lumen.monitor import Monitor  # noqa
from lumen.sources import Source, RESTSource  # noqa
from lumen.transforms import Transform  # noqa
from lumen.views import View  # noqa

from sudBoard.settings import BASE_DIR
from vizApps.domain.Board import BoardEntity

from vizApps.services.lumen.util import SpecYamlCreator
intakeSourceName = 'sql_auto'

instancesList = []


class LumenDashboard(param.Parameterized):

    title = param.String(label="Titre")
    layout = param.ObjectSelector(label="Mise en page", objects=['grid','tabs','column'],default='grid')
    ncols = param.Integer(label='Nombre de colonne', default=2)
    theme = param.ObjectSelector(label="Theme", objects=['default','dark'], default='default')
    template = param.String(default="material",precedence=-1)
    logo = param.FileSelector(precedence=-1)
    specfile = param.FileSelector()
    specDoc = param.Parameter(precedence=-1)

    def __init__(self, **kwargs):
        super(LumenDashboard, self).__init__(**kwargs)
        boardId=kwargs['board']
        self.initialized = False

        self.board = BoardEntity.objects.get(id=boardId)
        self._session = kwargs.get('sessionId')+ str(boardId)
        self.specDoc = self.createSpecFromData()

        instancesList.append(self)

    @param.depends('specDoc', watch=True)
    def updateSpec(self):
        if hasattr(self, 'dashBoard'):
            self.dashBoard.specification = self.specDoc.name
            self.dashBoard._load_config(from_file=True)
            try:
                self.dashBoard._reload()
            except(Exception) as e:
                print(e)
        else:
            self.dashBoard = Dashboard(specification=self.specDoc.name)

    def createSpecFromData(self):

        if self.board.config:
            specification = self.board.config
            with open(r'specYamlFile/temp/dashboard_{}.yml'.format(self._session), 'w') as file:
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

        with open(r'specYamlFile/default/nouveau_dashboard_default_config.yml', 'w') as file:
            yaml.dump(specification, file)
            return file

    @param.depends('specfile', watch=True)
    def uploadSpecFile(self):
        if self.specfile:
            with open(r'specYamlFile/upload/dashboard_{}.yml'.format(self._session), 'w') as file:
                spec = yaml.load(self.specfile)
                yaml.dump(spec, file)
            self.specDoc = file

    def view(self):
        if not self.initialized:
            config = yaml.load(self.dashBoard._yaml)['config']
            self.title = config.get("title")
            self.layout = config.get("layout")
            self.ncols = config.get("ncols")
            self.theme = config.get("theme")
            self.template = config.get("template")
            self.logo = config.get("logo")
            self.initialized = True

    def panel(self):
        layout = pn.Column(
            pn.Param(
                self.param,
                #parameters=[],
                widgets={
                    #'title': pn.widgets.TextInput(placeholder="Indiquer le titre du DashBoard"),
                    'logo': pn.widgets.FileInput(accept='.jpg,.png,.ico,.gif',name="Logo"),
                    'specfile': pn.widgets.FileInput(accept='.yaml,.yml', name="Specification File")},
                show_name=False,
                expand_button=False,
                expand=False,
                sizing_mode = "stretch_width"
            ),
            self.view,
            margin=10,
            css_classes=['panel-widget-box'],
            sizing_mode='stretch_width'
        )

        return layout

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

    @classmethod
    def clearInstances(cls):
        instancesList.clear()
