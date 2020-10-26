import param
import panel as pn
import pandas as pd
import holoviews as hv
from vizApps.services.viz.progressExtModule import ProgressExtMod
from vizApps.domain.TypeVizEnum import TypeVizEnum


from holoviews.plotting.links import DataLink


GEOMPLOT = [TypeVizEnum.CHOROPLETH_MAP,TypeVizEnum.POINT_MAP]

class TraceParam(param.Parameterized):
    select_column = param.Parameter()

    data = param.DataFrame(precedence=-1)

    listeEntier = param.Selector(default=[])
    listeDecimal = param.Selector(default=[])
    listeBooleen = param.Selector(default=[])
    listeTexte = param.Selector(default=[])
    listeDate = param.Selector(default=[])
    listeObjet = param.Selector(default=[])

    x = param.String(default='x', doc="Colonne à afficher sur l'axe X.")
    y = param.String(default='frequence', doc="Colonne à afficher sur l'axe Y.")

    opts = param.Dict(default={}, doc="Options a appliquer sur le graphique.")


    def __init__(self, **params):
        self.progress = ProgressExtMod()
        self.completed = self.progress.completed
        self.viz =  params.get("viz")
        self.trace = params.get("trace")
        self.data = self.getUpdatedData(self.trace.dataFrame)

        super(TraceParam, self).__init__(data=self.data, viz=self.viz)


    @param.depends("progress.completed")
    def viewProgress(self):
        print("TraceParam ", self, " id:", id(self))

        return pn.Column(self.progress.view)

    def view(self):
        widgetSelectColumn = self.settingWidgetSelectColumn()
        table = hv.Table(self.overlay)

        if len(table) == len(self.overlay):
            pass
            #DataLink(table,self.overlay)

        else:
            pass
        return pn.Row(table,widgetSelectColumn)


    def populateListeType(self, dataFrame):

        self.listeEntier = list(dataFrame.select_dtypes('int64').columns)
        self.listeDecimal = list(dataFrame.select_dtypes('float64').columns)
        self.listeObjet = list(dataFrame.select_dtypes('object').columns)
        self.listeTexte = list(dataFrame.select_dtypes('string').columns)

    def attacheOverlay(self, overlay):
        self.overlay = overlay

    def getUpdatedData(self, dataFrame):

        if self.viz.type not in GEOMPLOT:
            return pd.DataFrame(dataFrame).drop(['geometry'],axis=1)
        else:
            return dataFrame


    def settingWidgetSelectColumn(self):
        columnList = list(self.data)

        panelWidgetSelectCol = pn.widgets.Select(name="Sélection d'une colonne",
                                                           options=columnList)

        widgetColumnSelector = pn.Param(self.param, parameters=['select_column'],
                                        widgets={'select_column': panelWidgetSelectCol},
                                        sizing_mode='stretch_width')
        return widgetColumnSelector

    @param.depends('select_column', watch=True)
    def onChangeSelectColumn(self):
        pass


