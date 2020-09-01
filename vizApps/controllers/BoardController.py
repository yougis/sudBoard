# Create your views here.
from bokeh.embed import server_session
from bokeh.util import token
from django.shortcuts import render
from vizApps.domain.Board import BoardEntity
from vizApps.domain.Viz import VizEntity



def getBoardFromSlug(request, slug):

    # on récupère l'url de l'application du Board du serveur Bokeh
    bokeh_server_url = "%s" % (request.build_absolute_uri(location='/')) + 'board/' +  slug

    # on cherche l'identifiant de l'objet BoardEntity à partir du Slug
    board = BoardEntity.objects.get(slug=slug)
    headers = request.headers
    headers = dict(headers) if headers else {}

    # on ajoute dans le header l'id du board (il sera utiliser par la suite dans le service de création du document Bokeh)
    headers['board-id'] = board.id

    # génération du script
    server_script = server_session(None, session_id=token.generate_session_id(), url=bokeh_server_url,
                                   headers=headers)

    # On regarde si on est en mode edit
    edit = request.GET.get('edit')


    # Création du context pour le template Jinja
    context = {
               "script": server_script,
               "vizName": board.name,
               }
    template = None
    if (edit=='True'):
        template = render(request, 'board/board_edit.html', context)
    else:
        template = render(request, 'board/board_view.html', context)
    return template

def getBoardVizElementFromSlug(request, boardSlug, vizSlug):
    bokeh_server_url = "%s" % (request.build_absolute_uri(location='/')) + 'board/' +  boardSlug + '/vizentity/' +  vizSlug

    vizElement = VizEntity.objects.get(slug=vizSlug)
    headers = request.headers
    headers = dict(headers) if headers else {}
    headers['viz-element-id'] = vizElement.id

    server_script = server_session(None, session_id=token.generate_session_id(), url=bokeh_server_url,
                                   headers=headers)
    context = {
        "script": server_script,
        "vizName": vizElement.title,
    }
    return render(request, 'board/board_edit.html', context)


