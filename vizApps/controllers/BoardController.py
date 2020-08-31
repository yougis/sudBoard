# Create your views here.
from bokeh.embed import server_session
from bokeh.util import token
from django.shortcuts import render
from vizApps.domain.Board import BoardEntity
from vizApps.domain.Viz import VizEntity



def getBoardFromSlug(request, slug):
    bokeh_server_url = "%s" % (request.build_absolute_uri(location='/')) + 'board/' +  slug

    board = BoardEntity.objects.get(slug=slug)
    headers = request.headers
    headers = dict(headers) if headers else {}
    headers['board-id'] = board.id

    server_script = server_session(None, session_id=token.generate_session_id(), url=bokeh_server_url,
                                   headers=headers)

    context = {
               "script": server_script,
               "vizName": board.name,
               }

    return render(request, 'board/projet_edition.html', context)

def getBoardVizElementFromSlug(request, boardSlug, title):
    bokeh_server_url = "%s" % (request.build_absolute_uri(location='/')) + 'board/' +  boardSlug + '/vizentity/' +  title

    vizElement = VizEntity.objects.get(title=title)
    headers = request.headers
    headers = dict(headers) if headers else {}
    headers['viz-element-id'] = vizElement.id

    server_script = server_session(None, session_id=token.generate_session_id(), url=bokeh_server_url,
                                   headers=headers)
    context = {
        "script": server_script,
        "vizName": vizElement.title,
    }
    return render(request, 'board/projet_edition.html', context)


