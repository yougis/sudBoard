import os
import yaml
import panel as pn
import param, time
from lumen.dashboard import Dashboard
from lumen.filters import ConstantFilter, Filter, WidgetFilter  # noqa
from lumen.sources import Source, RESTSource  # noqa
from lumen import  config

from sudBoard.settings import BASE_DIR
from vizApps.domain.Board import BoardEntity

from vizApps.services.lumen.util import SpecYamlCreator, centerContent

instancesList = []

class LumenDashboard(param.Parameterized):

    specfile = param.FileSelector()
    reloader = pn.widgets.Button(name='=', width=10)
    config = param.Parameter(precedence=-1)
    specDoc = param.Parameter(precedence=-1)
    dashBoard = param.Parameter(precedence=-1)
    sentinelHackCounter = 0
    loading = False
    indicator = centerContent(pn.indicators.LoadingSpinner(value=True))


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

    def __init__(self, **kwargs):

        super(LumenDashboard, self).__init__(**kwargs)
        boardId=kwargs['board']
        self.board = BoardEntity.objects.get(id=boardId)
        self._session = kwargs.get('sessionId')+ str(boardId)
        self.josso_session_cookies = {'JOSSO_SESSIONID' : kwargs.get('JOSSO_SESSIONID')}
        self.specDoc = self.createSpecFromData()


        instancesList.append(self)

    def initializerCallback(self):
        print(f"call initializerCallback; dashboard {self.dashBoard}")

        if not self.dashBoard and not self.loading :
            self.sentinelHackCounter += 1
            print(f"sentinel UP : {self.sentinelHackCounter}")
            # premier lancement avec affichage d'un spinner car le server renvoi  le document d'un seul tenant,
            # du coup le panel ne s'affiche pas tant que le Dashboard n'est pas totalement chargé!
            self.loading = True
            pn.state.add_periodic_callback(self.update, 700,count=1)

    def update(self):
        print(f"call update; dashboard {self.dashBoard}; sentinel {self.sentinelHackCounter}")

        tic = time.clock()
        if not self.dashBoard:
            try:
                self.dashBoard = Dashboard(specification=self.specDoc.name)
                toc = time.clock()
                print(f"Time to create the dashboard {self.dashBoard.name} :  {toc - tic}")
            except(Exception) as e:
                self.dashBoard = pn.pane.HTML(object=f"<p>Erreur dans la préparation du dashboard : {e}</p>")
                print(e)
        else:
            self.dashBoard._yaml_file = self.specDoc.name
            self.dashBoard._load_specification(from_file=True)
            try:
                self.dashBoard._reload()
            except(Exception) as e:
                self.dashBoard = pn.pane.HTML(object=f"<p>Erreur dans la préparation du dashboard : {e}</p>")

        self.loading = False

    def createSpecFromData(self):

        if self.board.config:
            tic = time.clock()
            specification = self.board.config
            with open(r'specYamlFile/temp/dashboard_{}.yml'.format(self._session), 'w') as file:
                yaml.dump(specification, file)
            toc = time.clock()
            print(f"Time to create yaml {file.name} :  {toc - tic}")
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

    @param.depends('specfile', watch=True)
    def uploadSpecFile(self):
        if self.specfile:
            with open(r'specYamlFile/upload/dashboard_{}.yml'.format(self._session), 'w') as file:
                spec = yaml.load(self.specfile)
                for i in [v for source, v in spec.get('sources').items() if
                          v.get('type') == 'json']:
                    i['kwargs']['cookies'] = self.josso_session_cookies
                    break  # no need to iterate further
                yaml.dump(spec, file)
            self.specDoc = file
            self.dashBoard = None



    def updateConfig(self):
        print(f"call updateConfig; dashboard {self.dashBoard}")

        if self.specDoc.name is not None:
            with open(self.specDoc.name, 'r') as f:
                _yaml = yaml.load(f.read())
                _yaml['config'] = self.configMapping()

            with open(r'specYamlFile/temp/new_dashboard_{}.yml'.format(self._session), 'w') as f:
                yaml.dump(_yaml,f)
                self.specDoc = f

    def configMapping(self):
        config = {
            'title': self.config.title,
            'layout': self.config.layout.name,
            'ncols': self.config.ncols,
            'template': self.config.template.name,
            'theme': self.config.theme.name
         }
        return config

    @param.depends('config')
    def panel(self):
        layout = pn.Card(
            sizing_mode = 'stretch_width',
            title = "Parametres",
            collapsed = True)
        layout.append(
            pn.Param(
                self.param,

                widgets={
                    # 'logo': pn.widgets.FileInput(accept='.jpg,.png,.ico,.gif',name="Logo"),
                    'specfile': pn.widgets.FileInput(accept='.yaml,.yml', name="Specification File")},
                show_name=False,
                expand_button=False,
                expand=False,
                sizing_mode="stretch_width"
            ),

        )
        if self.config:
            layout.append(pn.Param(
                self.config.param,
                show_name=False,
                expand_button=False,
                expand=False,
                sizing_mode="stretch_width",
            ))
        return layout

    @param.depends('dashBoard')
    def main(self):
        print(f"call main; dashboard {self.dashBoard}, sentinel {self.sentinelHackCounter}")
        if isinstance(self.dashBoard, Dashboard):
            self.config = self.dashBoard.config
            layout = pn.Column(
                self.dashBoard._main,
                sizing_mode = 'stretch_both',
                margin = 10,
                width_policy = 'max',
                height_policy = 'max'

            )
            return layout
        elif self.dashBoard:
            return self.dashBoard
        else:
            return self.indicator

    @param.depends('dashBoard')
    def header(self):
        if isinstance(self.dashBoard, Dashboard):
            header= self.dashBoard._header
            return header

    @param.depends('dashBoard')
    def sidebar(self):
        if isinstance(self.dashBoard, Dashboard):
            sidebar= self.dashBoard._sidebar
            return sidebar

    @param.depends('dashBoard')
    def modal(self):
        if isinstance(self.dashBoard, Dashboard):
            modal= self.dashBoard._modal
            return modal

    @param.depends('dashBoard')
    def busyIndicator(self):
        spinner = pn.indicators.LoadingSpinner(width=40, height=40)
        pn.state.sync_busy(spinner)
        bi = pn.Row(spinner)
        return bi

