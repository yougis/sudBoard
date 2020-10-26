import param
import panel as pn
import pandas as pd
import hvplot.pandas
import geoviews as gv
from cartopy import crs
from holoviews.plotting.links import DataLink
from holoviews import opts

from vizApps.Utils.geomUtils import GeomUtil
import holoviews as hv
from numpy import random, nan


from vizApps.services.DataConnectorSevice import ConnectorInterface, CONNECTOR_LIST, REST_API, DATABASE, FILE,  SAMPLE, FULL
from vizApps.services.dataSource.dataCatalogueService import DataCatalogueService



class UrlInput(param.String):
    '''IPv4 address as a string (dotted decimal notation)'''
    def __init__(self, default="", regex=None, **params):
        ip_regex = '^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        default= "192.168.1.1"

        super(UrlInput, self).__init__(default=default,regex=ip_regex)
        self._validate(self.default)


    def _validate(self, val):
        super()._validate(val)


class ChoiceConnector(param.Parameterized):
    liste_connecteur = param.Selector(objects=[i for i, k in CONNECTOR_LIST[:]])
    #widget_url_connector = UrlInput()
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
            tableDf = pd.DataFrame(dataTable.drop(['geometry'],axis=1))
            table = hv.Table(tableDf)
            map = gv.Polygons(dataTable, crs=crs.GOOGLE_MERCATOR)
            #table = hv.Table(map)
            DataLink(map,table)
            return  ( map + table).opts(opts.Polygons(tools=['hover', 'tap']))
        else:
            return pn.Column(hv.Table(dataTable))

    def panel(self):
        return pn.Row(self.view)

class CreateData(param.Parameterized):

    ready = param.Boolean(default=False, precedence=-1)

    def __init__(self, **params):
        super(CreateData, self).__init__(**params)