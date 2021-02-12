import urllib.request

import param
import panel as pn

import yaml
from vizApps.services.lumen.util import SpecYamlCreator
from lumen.dashboard import Dashboard  # noqa
from lumen.filters import Filter, ConstantFilter, WidgetFilter, FacetFilter
#from vizApps.domain.lumen.target import TargetEntity
from vizApps.domain.lumen.filter import FilterEntity

filterTypeSupported = [ConstantFilter, WidgetFilter, FacetFilter]

widgetsDic = {
    # filters
    'facet': [pn.widgets.Select(name='field')],
    'widget': [pn.widgets.Select(name='field'),
               pn.widgets.Toggle(name='multi'),
               pn.widgets.Toggle(name='empty_select'),
               ],
    'constant': [pn.widgets.Select(name='field')],

}

# liste des prop à valeur dynamique
widgetPropertiesToUpdate = {
    "facet": ['field'],
    "widget": ['field', 'default'],
    "constant": ['field']
}


def updateWidgets(type, panelWidgets, schema):
    if type:
        # initialisation des widgets
        # ajuster les options des widgets à partir des données sources
        # on initialise la valeur des param avec la valeur des widgets
        # on affecte les valeurs  / options par défaut aux widgets

        [widgetUpdater(w, {**dicMapping(w.name, schema)}) for w in panelWidgets if
         w.name in widgetPropertiesToUpdate[type]]

    else:
        return pn.Column()


def dicMapping(widgetName, schema):
    dic = {
        'field': {
            'value': list([str(i) for i in schema.keys()])[0],
            'options': list([str(i) for i in schema.keys()])},
        'default': {
            'value': list([str(i) for i in schema.keys()])[0],
            'options': list([str(i) for i in schema.keys()])},
    }
    return dic[widgetName]


def dynamicParameters(paramObj, newWidgets):
    for w in newWidgets:
        if len([i for i in paramObj if i == str(w.name).lower()]) == 0:
            paramObj._add_parameter(param_name=str(w.name).lower(), param_obj=param.Parameter())
            paramObj.set_default(str(w.name).lower(), w.value)
    return newWidgets


def widgetUpdater(w, dictValues):
    w.param.set_param(**dictValues)


class ChoiceTarget(param.Parameterized):
    liste = param.ObjectSelector(label='Moniteur')
    sourceListe= param.ObjectSelector(label='Donnée source')

    def __init__(self, **params):

        self.init = True
        for k, v in params.items():
            if k in self.param:
                if hasattr(self.param[k], "objects"):
                    self.param[k].objects = v
                    self.param[k].default = self.param[k].objects[0]
                else:
                    setattr(self, k, v)
        super(ChoiceTarget, self).__init__()

    @param.depends('liste')
    def view(self):

        if self.liste:
            layout = pn.Column(sizing_mode='stretch_width')
            layout.append(pn.pane.Markdown(f'## {self.liste}', sizing_mode='stretch_width'))
            if len(self.liste.filters)>0:
                layout.append(pn.pane.Markdown(f'Ce moniteur dispose déjà de {len(self.liste.filters)}', sizing_mode='stretch_width'))
                layout.append([pn.pane.Markdown(f'- {filter}',sizing_mode='stretch_width') for filter in self.liste.filters])

            return layout

    @param.depends('liste')
    def subView(self):
        if self.liste:
            layout = pn.Column(sizing_mode='stretch_width')
            self.param['sourceListe'].objects = list(self.liste.source.cat)
            self.sourceListe = list(self.liste.source.cat)[0]
            layout.append(self.param['sourceListe'])

            return layout


    @param.output(target=param.Parameter(), schema=param.Dict())
    def output(self):
        schema = self.liste.schema[self.sourceListe]
        return self.liste, schema

    def panel(self):
        return pn.Column(
            pn.Param(
                self.param,
                parameters=['liste'],
                expand_button=False, expand=False,
                show_name=False,
                sizing_mode='stretch_width'
            ),
            self.view,
            self.subView,
            css_classes=['panel-widget-box'],
            sizing_mode='stretch_width')


class StepFilter(param.Parameterized):
    target = param.Parameter()

    schema = param.Dict()

    transforms = param.Parameter()

    filterTypeSelector = param.ObjectSelector(allow_None=True)

    spec = param.Parameter(precedence=-1)

    error_message = param.String(doc="Message d'erreur")

    filterTypeParameters, dashboard = None, None

    lumenDashboard = param.Parameter()

    config = param.Parameter()

    def __init__(self, **params):
        super(StepFilter, self).__init__(**params)
        self.filter_type = self.previousFilterType = None
        self.param['filterTypeSelector'].objects = [view for view in param.concrete_descendents(Filter).values() if
                                                    view in filterTypeSupported]
        self.param['filterTypeSelector'].default = self.param['filterTypeSelector'].objects[0]
        self.dashboard = Dashboard(specification=r'specYamlFile/default/nouveau_dashboard_default_config.yml')
        self.filterTypeParametersDynamicWidgetsSelector = None

    ## CALLBACKS

    # callback de modification des widgets spécifiques d'une view
    def callback(self, *events):
        if [e for e in events if e.type == "changed"]:
            self.spec = self.specUpdate()

    def multiCallback(self,*events):
        if [e for e in events if e.type == "changed" and e.new]:
            ...



    @param.depends('spec')
    def filterControl(self):
        self.error_message = ''
        if self.spec:
            with open(r'specYamlFile/temp/spec_tmp_file_{}.yml'.format(self.name), 'w') as file:
                yaml.dump(self.spec.get_dic(), file)

            try:
                self.dashboard.specification = file.name
                self.dashboard._load_config(from_file=True)
                self.dashboard._reload()
            except ValueError as v:
                print(v)
                self.error_message = str(v)
                return pn.Column(self.error_message, sizing_mode='stretch_width')
            except Exception as e:
                print(e)

        return pn.Column(
            self.dashboard._targets[0].filter_panel,
            show_name=False,
            sizing_mode='stretch_width')

    def view(self):

        if not self.filterTypeSelector:
            self.filterTypeSelector = self.param['filterTypeSelector'].default

        if self.filterTypeSelector and self.filterTypeSelector.filter_type != self.previousFilterType:
            self.previousFilterType = self.filterTypeSelector.filter_type
            self.filter_type = self.filterTypeSelector.filter_type
            widgets = widgetsDic[self.filter_type]

            if not self.filterTypeParametersDynamicWidgetsSelector:
                widgetsToCreate = widgets
            else:
                widgetsAlreadyCreated = [wid[1] for wid in
                                         self.filterTypeParametersDynamicWidgetsSelector.widgets.items()
                                         if wid[0] in [w.name for w in widgets]]
                widgetsToCreate = [w for w in widgets if w.name not in widgetsAlreadyCreated]

            self.panelWidgets = dynamicParameters(self.param, widgets)

            # on map les param du viewType avec des widgets Panel
            self.filterTypeParametersDynamicWidgetsSelector = pn.Param(
                self.param,
                parameters=[str(panelWidget.name).lower() for panelWidget in self.panelWidgets],
                widgets={panelWidget.name: panelWidget for panelWidget in self.panelWidgets},
                sizing_mode='stretch_width',
                show_name=False,
                expand_button=False,
                expand=False,
            )
            # on ajoute des watchers pour certains widgets
            self.param.watch(self.multiCallback, [str(panelWidget.name).lower() for panelWidget in widgetsToCreate if
                                                  panelWidget.name == 'multi'])

            # on ajoute un watcher sur chaque nouveau param/widget dynamique pour reloader la viz suite d'un choix dans l'IHM
            self.param.watch(self.callback, [str(panelWidget.name).lower() for panelWidget in widgetsToCreate])



            updateWidgets(self.filter_type, self.panelWidgets, self.schema)

        return pn.Column(self.filterTypeParametersDynamicWidgetsSelector, sizing_mode='stretch_width')

    def specUpdate(self):
        filter_type = self.filterTypeSelector.filter_type
        self.filterTypeParameters = {p.name: getattr(self, p.name) for p in self.panelWidgets}

       #if self.filterTypeParameters.get('multi'):
       #    self.filterTypeParameters['default']=[]
        self.filterTypeParameters['type'] = filter_type

        self.config = {
            'title': self.lumenDashboard.title,
            'layout': self.lumenDashboard.layout,
            'ncols': self.lumenDashboard.ncols,
            'template': self.lumenDashboard.template,
            'theme': self.lumenDashboard.theme}

        target_param = [t for t in self.lumenDashboard.dashBoard._spec['targets'] if t['name'] == self.target.name][0]

        target_param['filters'] = [{**self.filterTypeParameters}]


        return SpecYamlCreator(config=self.config, targets=[target_param])

    def panel(self):
        layout = pn.Column(
            pn.Column(
                pn.Param(
                    self.param,
                    parameters=['filterTypeSelector'],
                    widgets={'filterTypeSelector': pn.widgets.RadioButtonGroup},
                    expand_button=False,
                    expand=False,
                    sizing_mode='stretch_width',
                    show_name=False
                ),
                self.view,
                css_classes=['panel-widget-box'],
                sizing_mode='stretch_width'
            ),
            pn.Row(
            self.filterControl,
            css_classes=['panel-widget-box'],
            sizing_mode='stretch_width')
        ,sizing_mode='stretch_width')

        return layout

    @param.output(specification=param.Dict())
    def output(self):
        spec = self.spec.get_dic()
        return spec


class StepSave(param.Parameterized):
    specification = param.Dict()

    url = param.String()

    boutonSave = param.Action(label="Sauvegarder", precedence=2)
    boutonFinish = param.Action(label="Terminer", precedence=3)

    lumenDashboard = param.Parameter()

    html_pane = pn.pane.HTML(" ", precedence=1)

    def __init__(self, **params):
        params["boutonSave"] = self._boutonSave
        params["boutonFinish"] = self._boutonFinish

        for k, v in params.items():
            if k in self.param:
                if hasattr(self.param[k], "objects"):
                    if isinstance(v, list):
                        if len(v) > 0:
                            self.param[k].objects = [m.name for m in v]
                            self.param[k].default = self.param[k].objects[0]

                else:
                    setattr(self, k, v)
        super(StepSave, self).__init__()

    def _boutonSave(self, event=None):
        redirect = f"""<script>
                window.location.href="{self.url}"</script>
                """
        self.html_pane.object = redirect
        # board
        board = self.lumenDashboard.board

        # persite spec data to django model
        yamlConf = self.specification['config'] if self.specification['config'] else None
        yamlTargets = self.specification['targets'][0] if len(self.specification['targets']) > 0 else None
        yamlViews = yamlTargets['views'][0] if len(yamlTargets['views']) > 0 else None
        yamlTransforms = yamlViews['transforms'][0] if len(yamlViews['transforms']) > 0 else None
        yamlFilters = yamlTargets['filters'][0] if len(yamlTargets['filters']) > 0 else None

        # Target

        targetEntity = next(t for t in board.targetentity_set.all() if t.name == self.targets)


        # Filters
        if yamlFilters:
            filterEntity = FilterEntity(target=targetEntity, specYaml=yamlFilters)

        filterEntity.save()
        targetEntity.save()

        board.save(conf=yamlConf)

        with open(r'specYamlFile/temp/dashboard_{}.yml'.format(self.lumenDashboard._session), 'w') as file:
            yaml.dump(yaml.load(board.config), file)

        self.lumenDashboard.specDoc = file

        # return to dashboard

        self.html_pane.param.trigger('object')
        self.html_pane.object = " "

    def _boutonFinish(self, event=None):
        pass

    @param.depends('toExistingTarget')
    def view(self):
        if self.toExistingTarget:
            return pn.Column(pn.Param(self.param.targets,
                                      show_labels=False,
                                      show_name=False,
                                      expand_button=False,
                                      expand=False,
                                      sizing_mode='stretch_width'
                                      ), sizing_mode='stretch_width')
        else:
            return pn.Column(sizing_mode='stretch_width')

    def panel(self):

        redirect = f""" window.location.href="{self.url}"
        """

        boutonSave = pn.widgets.Button(name=self.param.boutonSave.label, button_type="success")
        boutonFinish = pn.widgets.Button(name=self.param.boutonFinish.label, button_type="primary")

        boutonFinish.js_on_click(code=redirect)

        return pn.Column(
            pn.Param(
                self.param,
                parameters=['targetName', 'toExistingTarget', 'boutonSave', 'boutonFinish'],
                widgets={
                    "toExistingTarget": pn.widgets.button.Toggle(
                        name="Intégrer la représentation à un moniteur existant"),
                    "boutonSave": boutonSave,
                    "boutonFinish": boutonFinish
                },
                show_name=False,
                expand_button=False,
                expand=False,
                sizing_mode='stretch_width'
            ),
            self.view,
            self.html_pane,
            css_classes=['panel-widget-box'],
            sizing_mode='stretch_width')


