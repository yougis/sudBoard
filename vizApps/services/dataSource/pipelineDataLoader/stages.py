import urllib.request

import param
import panel as pn

import pandas as pd

import hvplot.pandas
import geoviews as gv
from cartopy import crs
from holoviews.plotting.links import DataLink
from holoviews import opts
from bokeh.models import WheelZoomTool

from vizApps.Utils.geomUtils import GeomUtil
from vizApps.services.viz.baseMapAppService import BaseMapApp
from vizApps.domain.Viz import VizEntity

from vizApps.services.trace.traceParam import TraceParam
import holoviews as hv
from numpy import random, nan
import yaml
from vizApps.services.lumen.util import SpecYamlCreator
from lumen.util import get_dataframe_schema

from lumen.dashboard import Dashboard # noqa
from lumen.views import View, IndicatorView, StringView,  hvPlotView, Table, Download# noqa
from hvplot.plotting.core import hvPlot

from vizApps.services.DataConnectorSevice import ConnectorInterface, CONNECTOR_LIST, REST_API, DATABASE, FILE,  SAMPLE, FULL

import os
from intake import open_catalog
from sudBoard.settings import BASE_DIR

from vizApps.domain.lumen.target import TargetEntity
from vizApps.domain.lumen.view import ViewEntity
from vizApps.domain.lumen.filter import FilterEntity

path = BASE_DIR + '/vizApps/services/intake/'

viewTypeSupported = [StringView,IndicatorView,hvPlotView]

widgetsDic = {
    "string" : [pn.widgets.TextInput(name='text'), pn.widgets.Select(name='field')],
    "indicator" : [pn.widgets.Select(name='indicator',options=['string','number','progress','gauge','dial'],label='nulisime'),
                   pn.widgets.TextInput(name='label',value="this is label",placeholder='indiquer un titre pour le widget'),
                   pn.widgets.Select(name='field', value="choix du field", options=['choix du field'])],
    "hvplot" : [
        pn.widgets.Select(name='kind',options=hvPlot.__all__),
        pn.widgets.Select(name='x'),
        pn.widgets.Select(name='y'),
        pn.widgets.TextInput(name='title',placeholder='indiquer un titre pour le graphique'),
    ],
    "table" :[pn.widgets.TextInput(name='Tabulator')],
    "download" : [pn.widgets.TextInput(name='téléchargement')]
}

# liste des prop à valeur variable
widgetPropertiesToUpdate = {
    'string': ['field'],
    'indicator': ['field','indicator'],
    'hvplot': ['x', 'y'],
    'table': [''],
    'download': ['']
}

class UrlInput(param.String):
    '''IPv4 address as a string (dotted decimal notation)'''
    def __init__(self, default="", regex=None, **params):
        ip_regex = '^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        default= "192.168.1.1"

        super(UrlInput, self).__init__(default=default,regex=ip_regex)
        self._validate(self.default)


    def _validate(self, val):
        super()._validate(val)


class ChoiceInList():
    liste = param.ObjectSelector()
    def __init__(self, **params):
        #super(ChoiceTarget, self).__init__(**params)
        self.init = True
        for k, v in params.items():
            if k in self.param:
                self.param[k].objects = v
            self.param[k].default = self.param[k].objects[0]

class ChoiceSource(param.Parameterized):
    liste_des_sources = param.ObjectSelector(label='source')

    def __init__(self, **params):

        self.init = True
        source_liste = []
        for k, v in params.items():
            self.catalogs = v
            for cat in v:
                for s in list(cat):
                    source_liste.append(cat[s])
            if k in self.param:
                self.param[k].objects = source_liste
                self.param[k].default = self.param[k].objects[1]
        super(ChoiceSource, self).__init__()

    @param.depends('liste_des_sources')
    def view(self):
        if self.liste_des_sources:
            layout = pn.Column(pn.pane.HTML(f'{self.liste_des_sources}'), sizing_mode='stretch_width')
            plot = None
            if self.liste_des_sources.hvplot() != None:
                plot = self.liste_des_sources.hvplot()
                layout.append(pn.Row(plot))
            return layout

    @param.output(src=param.ObjectSelector(),schema=param.Dict())
    def output(self):
        schema = get_dataframe_schema(self.liste_des_sources._dataframe)['items']['properties']
        return self.liste_des_sources,schema

    def panel(self):
        self.layout = pn.Column(
            pn.Param(
                self.param,
                expand_button=False, expand=False,
                show_name = False,
            ),
            self.view,

            css_classes=['panel-widget-box'],
            sizing_mode='stretch_width')
        return self.layout

class ChoiceTarget(param.Parameterized):
    liste = param.ObjectSelector(label='title')
    src = param.ObjectSelector()

    def __init__(self, **params):

        self.init = True
        for k, v in params.items():
            if k in self.param:
                if hasattr(self.param[k], "objects"):
                    self.param[k].objects = v
                    self.param[k].default = self.param[k].objects[0]
                else:
                    setattr(self,k, v)
        super(ChoiceTarget, self).__init__()

    #@param.depends('liste', 'source')
    @param.depends('liste')
    def view(self):

        if self.liste:
            title = pn.Column(pn.pane.Markdown('## {}'.format(self.liste)), sizing_mode='stretch_width')
            #panels = self.liste.panels
            #layout = title + panels
            return title

    @param.output(target_select=param.String(),source_select=param.ObjectSelector())
    def output(self):
        return self.liste, self.src

    def panel(self):
        expand_layout = pn.Column()
        return pn.Column(
            pn.Param(
                self.param,
                expand_button=False, expand=False,
                show_name = False,
            ),
            self.view,

            css_classes=['panel-widget-box'],
            sizing_mode='stretch_width')


class StepConfiguration(param.Parameterized):

    src = param.ObjectSelector()
    schema = param.Dict()

    spec = param.Parameter(precedence=-1)

    error_message = param.String()



    viewTypeSelector = param.ObjectSelector(allow_None=True)
    viewTypeParameters, dashboard = None, None


    def __init__(self, **params):
        self.view_type, self.previousViewType = None, None
        self.param['viewTypeSelector'].objects = [view for view in param.concrete_descendents(View).values() if view in viewTypeSupported]
        self.param['viewTypeSelector'].default = self.param['viewTypeSelector'].objects[0]
        self.dashboard = Dashboard(specification=r'specYamlFile/nouveau_dashboard_default_config.yml')
        self.widgetsParams = param.Parameter(precedence=-1)
        self.viewTypeParametersDynamicWidgetsSelector = None
        super(StepConfiguration, self).__init__(**params)

    # callback de modification des widgets spécifiques d'une view
    def callback(self,*events):
        if [e for e in events if e.type == "changed"]:
            self.spec = self.specUpdate()

    @param.depends('spec')
    def dashviz(self):
        self.error_message = ''
        if self.spec:
            with open(r'specYamlFile/spec_tmp_file_{}.yml'.format(self.name), 'w') as file:
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

        return pn.Column(self.dashboard._targets[0]._cards[0], sizing_mode='stretch_width')

    def updateWidgets(self):

        if self.viewTypeSelector:
            self.view_type = self.viewTypeSelector.view_type

            # initialisation des widgets
            # ajuster les options des widgets à partir des données sources

            dicMapping = {
                '*': {},
                'indicator' : {'value' : 'string'},
                'field': {
                    'value': list([str(i) for i in self.schema.keys()])[0],
                    'options': list([str(i) for i in self.schema.keys()])},
                'x': {'options': list([str(i) for i in self.schema.keys()])},
                'y': {'value': list([str(i) for i in self.schema.keys()])[0],
                      'options': list([str(i) for i in self.schema.keys()])}
            }
            # on initialise la valeur des param avec la valeur des widgets
            # on affecte les valeurs  / options par défaut aux widgets

            [self.widgetUpdater(w, {**dicMapping[w.name],**dicMapping['*']}) for w in self.panelWidgets if w.name in widgetPropertiesToUpdate[self.view_type]]

        else:
            return pn.Column() #on reset le layout

    def widgets(self):

        if self.viewTypeSelector and self.viewTypeSelector.view_type != self.previousViewType:
            self.previousViewType = self.viewTypeSelector.view_type
            self.view_type = self.viewTypeSelector.view_type
            widgets = widgetsDic[self.view_type]

            if not self.viewTypeParametersDynamicWidgetsSelector:
                widgetsToCreate = widgets
            else:
                widgetsAlreadyCreated = [wid[1] for wid in self.viewTypeParametersDynamicWidgetsSelector.widgets.items()
                                   if wid[0] in [w.name for w in widgets] ]
                widgetsToCreate = [w for w  in widgets if w.name not in widgetsAlreadyCreated]

            self.panelWidgets = self.widgetWrapper(self.view_type, widgets)

            # on map les param du viewType avec des widgets Panel
            self.viewTypeParametersDynamicWidgetsSelector = pn.Param(
                self.param,
                parameters=[str(panelWidget.name).lower() for panelWidget in self.panelWidgets],
                widgets={panelWidget.name: panelWidget for panelWidget in self.panelWidgets},
                sizing_mode='stretch_width'
            )
            # on ajoute un watcher sur chaque nouveau param/widget dynamique pour reloader la viz suite d'un choix dans l'IHM
            self.param.watch(self.callback, [str(panelWidget.name).lower() for panelWidget in widgetsToCreate])
            self.updateWidgets()

        return pn.Column(pn.pane.Markdown('## {}'.format(self.view_type)),
                                       self.viewTypeParametersDynamicWidgetsSelector,
                                       sizing_mode='stretch_width')

    def specUpdate(self):
        view_type = self.viewTypeSelector.view_type
        self.viewTypeParameters = {p.name: getattr(self, p.name) for p in self.panelWidgets}

        config = {'title': "Nouveau DashBoard", 'layout': "grid", 'ncols': 2, 'template': 'material',
                  'theme': 'dark'}

        if self.viewTypeParameters:
            viewParameters = {
                'type': view_type,
                'table': self.src.name,
                **self.viewTypeParameters
            }

            target_param = [{
                'title': 'Nouveau',
                "source": {'type': 'intake',
                           'uri': self.src.cat.path},
                'views': [viewParameters],
                'filters': [
                ]
            }]

        return SpecYamlCreator(config=config, targets=target_param)

    def panel(self):
        layout = pn.Column(
            pn.Param(
                self.param,
                parameters=['viewTypeSelector'],
                widgets={'viewTypeSelector': pn.widgets.RadioButtonGroup},
                expand_button=False,
                expand=False
                ),
            self.widgets,
            self.dashviz,
            css_classes=['panel-widget-box'],
            sizing_mode='stretch_width')

        return layout

    def dynamicParameters(self,newWidgets):
        for w in newWidgets:
            if len([i for i in self.param if i==str(w.name).lower()])==0:
                self._add_parameter(param_name=str(w.name).lower(),param_obj=param.Parameter())
                self.set_default(str(w.name).lower(),w.value)
        return newWidgets

    def widgetWrapper(self, viewType, widgets):



        dicWrapper = {
            'string': self.dynamicParameters,
            'indicator': self.dynamicParameters,
            'hvplot': self.dynamicParameters,
            'table': self.dynamicParameters,
            'download':self.dynamicParameters
        }

        return dicWrapper[viewType](widgets)

    def widgetUpdater(self,w,dictValues):
        w.param.set_param(**dictValues)

    @param.output(specification=param.Dict())
    def output(self):
        spec = self.spec.get_dic()
        return spec

class StepSaveView(param.Parameterized):

    specification = param.Dict()

    url = param.String()

    boutonSaveFinish = param.Action(label="Sauvegarder et terminer")
    boutonCancelFinish = param.Action(label="Annuler et terminer")

    dashboard = param.Parameter()
    toExistingTarget = param.Boolean(label="Intégrer la représentation dans un moniteur existant")
    targets = param.ObjectSelector()

    def __init__(self,**params):
        params["boutonSaveFinish"] = self._boutonSaveFinish
        params["boutonCancelFinish"] = self._boutonCancelFinish

        for k, v in params.items():
            if k in self.param:
                if hasattr(self.param[k], "objects"):
                    self.param[k].objects = v
                    self.param[k].default = self.param[k].objects[0]
                else:
                    setattr(self,k, v)
        super(StepSaveView, self).__init__()


    def _boutonSaveFinish(self, event=None):
        # persite spec data to django model
        yamlTargets = self.specification['targets'][0] if len(self.specification['targets'])>0 else None
        yamlViews = yamlTargets['views'][0]  if len(yamlTargets['views'])>0 else None
        yamlFilters = yamlTargets['filters'][0] if len(yamlTargets['filters'])>0 else None

        # board
        board = self.dashboard.board

        # Target

        if self.toExistingTarget:
            targetEntity = next(t for t in board.targetentity_set.all() if t.name == self.targets.name)
        else:
            if yamlTargets:
                targetEntity = TargetEntity(board=board,name="Nouveau",specYaml=yamlTargets)

        # View
        if yamlViews:
            viewEntity = ViewEntity(target=targetEntity,name='Nouvelle Vue',specYaml=yamlViews)

        # Transforms

        # Filters
        if yamlFilters:
            filterEntity = FilterEntity(target=targetEntity, name='Nouveau filtre', specYaml=yamlFilters)

        targetEntity.save()
        viewEntity.save()


        with open(r'specYamlFile/dashboard_{}.yml'.format(self.dashboard._session), 'w') as file:
            yaml.dump(yaml.load(board.config), file)

        # return to dashboard
        return #urllib.request.urlopen(self.url)



    def _boutonCancelFinish(self, event=None):
        #return to dashboard
        pass

    @param.depends('toExistingTarget')
    def view(self):
        if self.toExistingTarget:
            return pn.Column(pn.Param(self.param.targets,
                                      show_labels=False,
                                      show_name=False,
                                      expand_button=False,
                                      expand=False
                                      ))
        else:
            return pn.Column()

    def panel(self):
        return pn.Column(
            pn.Param(
                self.param,
                parameters=['toExistingTarget','boutonSaveFinish','boutonCancelFinish'],
                widgets={
                    "boutonSaveFinish": {"button_type": "success", "width": 150, "sizing_mode": "fixed"},
                    "boutonCancelFinish": {"button_type": "primary", "width": 150, "sizing_mode": "fixed"}
                },
                show_name=False,
                expand_button=False,
                expand=False,
            ),
            self.view,
            css_classes=['panel-widget-box'],
            sizing_mode='stretch_width')

class ChoiceConnector(param.Parameterized):
    liste_connecteur = param.Selector(objects=[i for i, k in CONNECTOR_LIST[:]])
    widget_connector = param.String(precedence=0)
    dataConnectorParam = param.Dict(precedence=-1)
    ready = param.Boolean(default=False, precedence=-1)

    def __init__(self, **params):
        self.init = True
        super(ChoiceConnector, self).__init__(**params)


    def getInfoConnector(self):
        libelle = [k for i, k in CONNECTOR_LIST[:] if i == self.liste_connecteur][0]
        return self.liste_connecteur, libelle


    @param.output(connector=param.Dict())
    def output(self):
        return self.dataConnectorParam

    @param.depends('widget_connector', watch=True)
    def createConnector(self):
        if self.widget_connector:
            self.dataConnectorParam = {"url": self.widget_connector, "connector": self.liste_connecteur, "extraParams": {"cac": "a", "tat": "dd"}, "connector-id": str(random.randint(0,10000000))}

    @param.depends('liste_connecteur')
    def view(self):
        layout = pn.pane.Markdown('')
        if self.liste_connecteur :
            sourceList = []
            connecteur, libelle = self.getInfoConnector()

            # catalogue = DataCatalogueService(connecteur)

            widgetConnector = None

            if connecteur == REST_API:
                panelWidgetConnector = pn.widgets.TextInput(value= '/odk/odk/Formulaire/8a818603737f086101738d5bcef70005/listeObservation', placeholder='indiquer l\'url d\'une ressource au format JSON')

                panelWidgetConnector.jscallback(args={'textArea': panelWidgetConnector, 'css_class': 'psud_input'},
                    value="""
                    textArea.css_classes.push(css_class)
                    inputHTML = document.getElementsByClassName(css_class)
                    inputHTML.classList.add("bk-input-error")
                    """)
                widgetConnector = pn.Param(
                    self.param,
                    parameters=['widget_connector'],
                    widgets={'widget_connector': panelWidgetConnector },
                    sizing_mode='stretch_width',
                    precedence=1
                )


                # for i in catalogue.getListFromPsudUserProfile():
                #    sourceList.append('{ico} {name} \n' .format(ico="",name=i[0]))
                #widgetConnector = pn.widgets.CheckBoxGroup(name=self.liste_connecteur[1], options=sourceList, inline=False)
            elif connecteur == DATABASE:
                panelWidgetConnector = pn.widgets.TextInput(placeholder='indiquer le nom de la base de donnée', css_classes=['psud_input'])
                panelWidgetConnector.jscallback(args={'textArea': panelWidgetConnector, 'css_class': 'psud_input'},
                                                value="""
                                   textArea.css_classes.push(css_class)
                                   inputHTML = document.getElementsByClassName(css_class)
                                   inputHTML.classList.add("bk-input-error")
                                   """)

                widgetConnector = pn.Param(
                    self.param,
                    parameters=['widget_connector'],
                    widgets={'widget_connector': panelWidgetConnector},
                    sizing_mode='stretch_width',
                    precedence=0
                )
                pass
            elif connecteur == FILE:
                widgetConnector = pn.Param(
                    self.param,
                    parameters=['widget_connector'],
                    widgets={'widget_connector': pn.widgets.FileInput(
                        accept='.csv,.json,.zip,.gpx'
                    )},
                    sizing_mode='stretch_width',
                    precedence=0
                )
                pass

            layout = pn.Column(pn.pane.Markdown('## {}'.format(libelle)),widgetConnector, sizing_mode='stretch_width')

        return layout


    def panel(self):
        return pn.Column(
            pn.Param(
                self.param,
                parameters=['liste_connecteur'],
                widgets={'liste_connecteur': pn.widgets.RadioButtonGroup}),
            self.view,
            css_classes=['panel-widget-box'],
            sizing_mode='stretch_width')

class ReadData(param.Parameterized):

    connector = param.Dict()
    dataframe = param.DataFrame()
    select_column = param.Parameter()
    select_all = param.Boolean(False)
    layout = pn.Column()


    ready = param.Boolean(default=False, precedence=-1)

    def __init__(self, **params):
        super(ReadData, self).__init__(**params)


    @param.depends('connector')
    def view(self):


        #dci = Data Connection Interface
        try:
            dci =  ConnectorInterface.get(self.connector)
        except:
            self.layout = pn.pane.Markdown('## Un problème d\'accès aux connecteur est intervenu')

            return self.layout

        dci.configureConnector(SAMPLE)

        if dci.isDataInCache():
            dci.lookCachedData()
        else:
            print("Les données SAMPLE ne sont pas en cache")
            # sinon on charge les données sample
            try:
                self.dataframe = dci.getData()

            except:
                self.layout = pn.pane.Markdown('## Un problème d\'accès aux données est survenu')
                dci.disconnect()

                return self.layout

        if self.dataframe is not None :

            widgetColumnSelector = self.settingWidgetSelectColumn()

            self.layout = pn.Column(widgetColumnSelector, pn.pane.Markdown('## Prévisualisation des données'),self.dataPanel)
            #layout = hv.Table(self.dataframe)

            #html = data.to_html(classes=['example', 'panel-df'])
            #layout = pn.pane.HTML(html + script, sizing_mode='stretch_width')
            print(self.dataframe.head())
        else:
            self.layout = pn.pane.Markdown('## Un problème est survenu: \n - {} \n - {}'.format(dci.message, dci.connector.message))

        dci.disconnect()

        return self.layout

    def settingWidgetSelectColumn(self):
        columnList = list(self.dataframe)
        unSelectColList = ['class', 'version', '.Appli', 'createUser', 'updateUser', 'updateDate']
        self.select_column = [el for el in columnList if not list(filter(el.endswith, unSelectColList)) ]

        panelWidgetSelectCol = pn.widgets.CheckButtonGroup(name="Sélection des champs", value=self.select_column,
                                                           options=columnList)

        widgetColumnSelector = pn.Param(self.param, parameters=['select_column'],
                                        widgets={'select_column': panelWidgetSelectCol},
                                        sizing_mode='stretch_width')
        return widgetColumnSelector

    def dataPanel(self):

        script = """
                <script>
                if (document.readyState === "complete") {
                  $('.example').DataTable();
                } else {
                  $(document).ready(function () {
                    $('.example').DataTable();
                  })
                }
                </script>
                """


        if len([el for el in self.select_column if el not in list(self.dataframe)])>0 :
            # redefinition des valeurs du widget lorsque le dataframe change mais que view n'est pas rappelé suite à un aller retour dans la pipeline
            self.settingWidgetSelectColumn()
        #html = self.dataframe[self.select_column].to_html(classes=['example', 'panel-df'])
        #layout = pn.pane.HTML(html + script, sizing_mode='stretch_width')

        for c in self.select_column:
            if isinstance(self.dataframe[c].iloc[0],list) :
                self.dataframe[c] = self.dataframe[c].apply(lambda x: nan if len(x) == 0 else x)

        dataTable = self.dataframe[self.select_column]

        if GeomUtil.getIsGeo(self, dataTable):
            wheel_zoom = WheelZoomTool(zoom_on_axis=False)
            tableDf = pd.DataFrame(dataTable.drop(['geometry'],axis=1))
            table = hv.Table(tableDf)

            element = GeomUtil.getGeoElementFromData(self, data=dataTable)
            map = gv.Overlay([element]).options(
            active_tools=['wheel_zoom'])
            DataLink(element,table)
            return  ( map * table).options(toolbar='above').opts( width=800, height=600)
        else:
            return pn.Column(hv.Table(dataTable))

    def panel(self):
        return pn.Row(self.view)

class CreateData(param.Parameterized):

    ready = param.Boolean(default=False, precedence=-1)

    def __init__(self, **params):
        super(CreateData, self).__init__(**params)