# Create your views here.
from bokeh.embed import server_session
from bokeh.util import token
from django.http import HttpResponse
from django.shortcuts import render
from vizApps.domain.Board import BoardEntity
from vizApps.domain.Viz import VizEntity
from vizApps.services.board import BoardService
from vizApps.domain.Trace import TraceEntity

from vizApps.services.lumen.lumenService import LumenDashboard

import vizApps.services.viz.VizInstanceService as VizConstructor


class BoardController():

    def getBokehModelByTag(root, name):
        return [n for n in root if n.tags[0] == name]

    def endPointConstructor(self, params, slug, scriptName, base_uri):

        if (params['editMode']):
            if (params['lumenMode']):
                endPoint = 'studio-lumen/board/' + scriptName +'/' + slug
            else:
                endPoint = 'studio/board/' + slug
        elif (params['lumenMode']):
            endPoint = 'lumen/board/' + scriptName +'/' + slug
        else:
            endPoint = 'board/'+ slug
        return base_uri + endPoint

    def createBokehScript(model, session_id, headers, endPoint):

        return server_session(model=model, session_id=session_id, url=endPoint,
                                       headers=headers)


    def routeAction(request,slug):
        message = None
        params = {}
        # On regarde si c'est un POST ou un GET
        if(request.method=="POST"):
            editMode = True

            if 'addData' in request.POST:
                return BoardController.getDataLoaderModule(request)
            elif 'save' in request.POST:
                # on récuère la liste des vizApps de la seesion pour récupéré les VizEntity qui y sont attachées en mémoire
                # on persiste les parametres des vizApp dans la VizEntity
                # on fais ça pour toutes les VizEntity de la BoardEntity

                vizAppListe = VizConstructor.getVizAppInstancesBySessionId(request.COOKIES.get('session_id')+ request.COOKIES.get('board_id'))

                if vizAppListe :
                    for vizApp in vizAppListe:
                        viz = vizApp.viz_instance
                        viz.updateVizApp(vizApp)
                        viz.save()
                else:
                    message = "Aucune Viz à mettre à jour"

        elif(request.method=="GET"):

            params['editMode']=request.GET.get('edit')
            params['lumenMode'] = request.GET.get('lumen')



        return BoardController.getBoardAppFromBoardSlug(request=request, slug=slug, message=message, params=params)

    def getDataLoaderModule(request, editMode=True):
        template = None
        endPoint = 'studio/dataloader/'
        # on récupère l'url de l'application du Board du serveur Bokeh
        bokeh_server_url = "%s" % (request.build_absolute_uri(location='/')) + endPoint

        session_id = request.COOKIES.get('session_id')
        if session_id == None:
            session_id = token.generate_session_id()

        headers = request.headers
        headers = dict(headers) if headers else {}

        headers['session'] = request.COOKIES.get('crsftoken')

        server_script = server_session(None, session_id=session_id, url=bokeh_server_url,
                                       headers=headers)

        # Création du context pour le template Jinja
        context = {
            "dataloader": server_script
        }

        template = render(request, 'data/data_loader.html', context)
        return template


    def getBoardAppFromBoardSlug(*args,**kwargs ):

        params = kwargs.get('params')
        slug = kwargs.get('slug')
        message = kwargs.get('message')
        request = kwargs.get('request')
        base_uri = request.build_absolute_uri(location='/')

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

        # on récupère les variables du templates pour les injecter dans le template Django
        ## on instancie un lumenDashboard si besoin
        LumenDashboard.clearInstancesForSession(sessionId=session_id)
        lumenDashBord = LumenDashboard.getinstancesBySessionId(sessionId=session_id)

        if lumenDashBord:
            lumenDashBord = lumenDashBord.pop()
        else:
            lumenDashBord = LumenDashboard(board=board.id, sessionId=session_id)

        template = lumenDashBord.dashBoard.template
        doc=template._init_doc()
        template_variables = doc.template_variables

        root = [obj for obj in doc.roots]
        listeOfBokehModel = [obj for obj in root if len(obj.tags) > 0]

        # on va chercher les composants Panels qui ont des tags définis
        nav = BoardController.getBokehModelByTag(listeOfBokehModel,'nav').pop()
        modal = BoardController.getBokehModelByTag(listeOfBokehModel, 'modal').pop()
        header = BoardController.getBokehModelByTag(listeOfBokehModel, 'header').pop()
        main = BoardController.getBokehModelByTag(listeOfBokehModel, 'main').pop()
        listeOfBokehModelWithNoTags = [obj for obj in root if len(obj.tags) == 0]

        # on va chercher les autres composants Panels qui n'ont de tags définis
        js_area = [obj for obj in listeOfBokehModelWithNoTags if obj.name == 'js_area'].pop()
        busy_indicator = [obj for obj in listeOfBokehModelWithNoTags if obj.name == 'busy_indicator'].pop()


        # génération des scripts
        server_script_Dict = {}
        listeScriptToCreate = [('sidebar', nav),('modal',modal),('header',header),('main',main),('js_area',js_area),('busy_indicator',busy_indicator)]


        for scriptName in listeScriptToCreate:
            model = scriptName[1]
            bokeh_server_url = BoardController.endPointConstructor(None, params, slug, scriptName[0], base_uri)

            script = BoardController.createBokehScript(model, session_id, headers, bokeh_server_url)
            server_script_Dict[scriptName[0]] = script


        # Création du context pour le template Jinja
        context = {
            "message": message,
            "boardName": board.name,
            "boardSlug": board.slug,
            "board": board,
            "traces" : TraceEntity.objects.filter(board=board),
            "extraParams": request.GET
        }
        contextWithlumenDashboard = {**context,**template_variables,**server_script_Dict}

        if (edit == 'True'):
            template = render(request, 'board/board_edit.html', contextWithlumenDashboard)
        else:
            template = render(request, 'board/board_view.html', context)

        response = template
        # on set les cookies car on en aura besoin dans le service qui sera exectué par le script bokeh (qui est en passe d'être injecté dans le template)
        response.set_cookie('session_id', session_id)
        response.set_cookie('board_id', board.id)

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
        response.set_cookie('session_id',session_id, 'SameSite','Lax')
        return response

    def cleanCache(self):
        response = BoardService.clearCache()
        return HttpResponse(response)

    def boardList(request):
        pass

    def create(request):
        pass

    def save(request):
        board = BoardService.getBoard(request.boardId)
        params = request.parameters
        BoardService.save(board, params)
        return

    def addData(request):
        #board = BoardService.getBoard(request.boardId)
        #params = request.parameters
        #BoardService.save(board, params)
        return HttpResponse()


