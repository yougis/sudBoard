from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
import datetime
from sudBoard.settings import JOSSO_ENV,BASE_URL, ENV, BASE_URL_DIC
from suds.client import Client
import os

WSDL_DIR = os.path.join(os.path.dirname(__file__), 'wsdl')

import urllib

class PsudJossoAuthMiddleware(MiddlewareMixin):
    base_url = BASE_URL_DIC[ENV]
    josso_env = BASE_URL_DIC[JOSSO_ENV]
    base_josso_url = '{env}/josso'.format(env=josso_env)

    def process_response(self,request, response):
        josso_session_id = request.COOKIES.get("JOSSO_SESSIONID")
        usernameLoginJOSSO = request.COOKIES.get("usernameLoginJOSSO")
        if josso_session_id and usernameLoginJOSSO:
            max_age = 1 * 24 * 60 * 60  #
            expires = datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age)
            response.set_cookie("JOSSO_SESSIONID", josso_session_id, expires=expires.utctimetuple(),
                                max_age=max_age)
            response.set_cookie('usernameLoginJOSSO', usernameLoginJOSSO, expires=expires.utctimetuple(), max_age=max_age)
        else:
            response.delete_cookie("JOSSO_SESSIONID")
        return response

    def process_request(self,request):

        parametersList = {**request.GET}


        if request.COOKIES.get('JOSSO_SESSIONID'):
            session_id = request.COOKIES.get('JOSSO_SESSIONID')
            # check if valid
            ident_manager_session_client = Client(
                url=self.get_wsdl_url('SSOSessionManager.xml'),
                location='{0}/services/SSOSessionManagerSoap?wsdl'.format(self.base_josso_url)
            )
            try:
                josso_session = ident_manager_session_client.service.getSession('requester',session_id)
            except :
                josso_session=type('obj', (object,), {'valid':False})
                print('no session : ', session_id)
            if not josso_session.valid:
                request.COOKIES["JOSSO_SESSIONID"] = ''
                request.COOKIES["usernameLoginJOSSO"] = ''
                redirect_uri = self.get_redirect_check_uri(request,parametersList)
                return redirect(self.getlogOutUrl(redirect_uri))
            return None
        if request.GET.get('josso_assertion_id'):
            assertion_id = request.GET.get('josso_assertion_id')
            josso_data = self.auth_complete(assertion_id)
            if josso_data['session_id'] and josso_data['username'] :
                request.COOKIES["JOSSO_SESSIONID"] = josso_data['session_id']
                request.COOKIES['usernameLoginJOSSO'] = josso_data['username']
                return None
            else:
                redirect_uri = self.get_redirect_check_uri(request, parametersList)
                formulaireJossoUrl = self.getAuthFormUrl(redirect_uri)
                return redirect(formulaireJossoUrl)

        else:
            redirect_uri = self.get_redirect_check_uri(request,parametersList)
            formulaireJossoUrl = self.getAuthFormUrl(redirect_uri)
            return redirect(formulaireJossoUrl)

    def get_redirect_check_uri(self,request,parametersList):
        params = '&'.join(['{}={}'.format(k,','.join(v)) for k,v in  parametersList.items()])

        redirect_uri = "{domain}{path}?{params}".format(domain=self.base_url, path=request.path,params=params)
        return redirect_uri

    def get_base_url(self):
        return self.base_url

    def getAuthFormUrl(self,redirect_uri):
        return '{0}/signon/login.do?{1}'.format(
            self.base_josso_url, urllib.parse.urlencode({'josso_back_to': redirect_uri})
        )

    def getlogOutUrl(self, redirect_uri):
        return '{0}/signon/logout.do?{1}'.format(
            self.base_josso_url, urllib.parse.urlencode({'josso_back_to': redirect_uri})
        )


    def get_wsdl_url(self, name):
        return 'file:{0}'.format(os.path.join(WSDL_DIR, name))

    def auth_complete(self, *args, **kwargs):
        ident_provider_client = Client(
            url=self.get_wsdl_url('SSOIdentityProvider.xml'),
            location='{0}/services/SSOIdentityProviderSoap?wsdl'.format(self.base_josso_url)
        )
        ident_manager_user_client = Client(
            url=self.get_wsdl_url('SSOIdentityManager.xml'),
            location='{0}/services/SSOIdentityManagerSoap?wsdl'.format(self.base_josso_url)
        )

        assertion_id = args[0]
        try:
            josso_session_id = str(ident_provider_client.service.resolveAuthenticationAssertion(assertion_id))
            josso_user_info = ident_manager_user_client.service.findUserInSession(josso_session_id)
        except:
            print('error assertion ID : ',assertion_id)
            josso_session_id =''
            josso_user_info=type('obj', (object,), {'name':'','properties':''})

        data = {
            'username': josso_user_info.name,
            'session_id': josso_session_id
        }
        data.update({str(p._name): str(p._value) for p in josso_user_info.properties})
        response = kwargs.get('response') or {}
        response.update(data)
        #kwargs.update({'response': response, 'backend': self})
        return response
