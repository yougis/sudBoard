import panel as pn
from vizApps.domain.Viz import VizEntity
import os


def getApp(doc):

    os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
    baseVizElement = getBaseVizElement(doc.session_context.request.headers["viz-element-id"])
    init = True
    viz = baseVizElement._vizApp
    gspec = pn.GridSpec(sizing_mode='stretch_both', max_height=800)

    gspec[0, :3] = pn.Row(pn.Row(viz.param, parameters=['update']),viz.getView)
    gspec[1, :3] = pn.Row(viz.viewDataFrame)


    gspec.server_doc(doc)

def getBaseVizElement(id):
    viz = VizEntity.objects.get(id=id)

    return viz
