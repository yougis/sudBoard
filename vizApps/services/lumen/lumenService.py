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
    specfile = param.FileSelector()
    config = param.Parameter(precedence=-1)
    specDoc = param.Parameter(precedence=-1)

    def __init__(self, **kwargs):
        super(LumenDashboard, self).__init__(**kwargs)
        boardId=kwargs['board']
        self.board = BoardEntity.objects.get(id=boardId)
        self._session = kwargs.get('sessionId')+ str(boardId)
        self.specDoc = self.createSpecFromData()
        self.config = yaml.load(self.dashBoard._yaml)['config']
        self.title = self.config.get("title")
        self.layout = self.config.get("layout")
        self.ncols = self.config.get("ncols")
        self.theme = self.config.get("theme")
        self.template = self.config.get("template")

        instancesList.append(self)

    @param.depends('specDoc', watch=True)
    def updateSpec(self):
        spinner = pn.indicators.LoadingSpinner(width=40, height=40)
        pn.state.sync_busy(spinner)
        if hasattr(self, 'dashBoard'):
            self.dashBoard.specification = self.specDoc.name
            self.dashBoard._load_config(from_file=True)
            try:
                self.dashBoard = Dashboard(specification=self.specDoc.name)
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
        self.config = {'title':self.title,
                       'layout':self.layout,
                       'ncols':self.ncols,
                       'theme':self.theme,
                       'template':self.template}

    @param.depends('config', watch=True)
    def updateConfig(self):
        if self.specDoc.name is not None:
            with open(self.specDoc.name, 'r') as f:
                _yaml = yaml.load(f.read())
                _yaml['config'] = self.config

            with open(r'specYamlFile/temp/new_dashboard_{}.yml'.format(self._session), 'w') as f:
                yaml.dump(_yaml,f)
                self.specDoc = f

    def panel(self):
        layout = pn.Column(
            pn.Param(
                self.param,
                widgets={
                    #'logo': pn.widgets.FileInput(accept='.jpg,.png,.ico,.gif',name="Logo"),
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
