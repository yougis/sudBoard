# Create your views here.
from bokeh.embed import server_session
from bokeh.util import token
from django.shortcuts import render
from vizApps.domain.Board import BoardEntity
from vizApps.domain.Viz import VizEntity
from vizApps.services.board import BoardService
import vizApps.services.viz.VizInstanceService as VizConstructor


class BoardController():

    def routeAction(request,slug):
        # On regarde si c'est un POST ou un GET
        if(request.method=="POST"):
            # on récuère la liste des vizApps de la seesion pour récupéré les VizEntity qui y sont attachées en mémoire
            # on persiste les parametres des vizApp dans la VizEntity
            # on fais ça pour toutes les VizEntity de la BoardEntity

            vizAppListe = VizConstructor.getVizAppInstancesBySessionId(request.COOKIES.get('session_id'))

            for vizApp in vizAppListe:
                viz = vizApp.viz_instance
                viz.updateVizApp(vizApp)
                viz.save()
                editMode=True

        elif(request.method=="GET"):
            editMode=request.GET.get('edit')

        return BoardController.getBoardAppFromBoardSlug(request, slug, editMode)

    def getBoardAppFromBoardSlug(request, slug, editMode=False):
        endPoint='board/'+slug
        if(editMode):
            endPoint = 'studio/board/' + slug

        # on récupère l'url de l'application du Board du serveur Bokeh
        bokeh_server_url = "%s" % (request.build_absolute_uri(location='/')) + endPoint

        # on cherche l'identifiant de l'objet BoardEntity à partir du Slug
        board = BoardEntity.objects.get(slug=slug)
        headers = request.headers
        headers = dict(headers) if headers else {}

        # on ajoute dans le header l'id du board (il sera utiliser par la suite dans le service de création du document Bokeh)
        headers['board-id'] = board.id

        session_id = request.COOKIES.get('session_id')
        if session_id== None:
            session_id = token.generate_session_id()

        headers['session'] = request.COOKIES.get('crsftoken')


        # On regarde si on est en mode edition
        #todo faire le controle des droits
        edit = request.GET.get('edit')

        # génération du script
        server_script = server_session(None, session_id=session_id, url=bokeh_server_url,
                                       headers=headers)

        # Création du context pour le template Jinja
        context = {
            "script": server_script,
            "boardName": board.name,
            "boardSlug": board.slug,
            "board": board,
            "extraParams": request.GET
        }
        template = None


        if (edit == 'True'):
            template = render(request, 'board/board_edit.html', context)
        else:
            template = render(request, 'board/board_view.html', context)

        response = template

        response.set_cookie('session_id', session_id)

        return response

    def getBoardVizElementFromSlug(request, boardSlug, vizSlug):
        bokeh_server_url = "%s" % (
            request.build_absolute_uri(location='/')) + 'board/' + boardSlug + '/vizentity/' + vizSlug

        vizElement = VizEntity.objects.get(slug=vizSlug)
        headers = request.headers
        headers = dict(headers) if headers else {}
        headers['viz-element-id'] = vizElement.id
        session_id = token.generate_session_id()

        server_script = server_session(None, session_id=session_id, url=bokeh_server_url,
                                       headers=headers)
        context = {
            "script": server_script,
            "vizName": vizElement.title,
        }

        response = render(request, 'board/board_edit.html', context)
        response.set_cookie('session_id',session_id)
        return response

    def boardList(request):
        pass

    def create(request):
        pass

    def save(request):
        board = BoardService.getBoard(request.boardId)
        params = request.parameters
        BoardService.save(board, params)
        return

