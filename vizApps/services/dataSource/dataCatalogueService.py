from vizApps.services.JossoSessionService import JossoSession
import requests
import json

excludeApps = []

class DataCatalogueService():

    def __init__(self, connector):
        self.connector = connector
        self.catalogue = []
        self.jossoSession = JossoSession()


    def getListFromGeocat(self):
        self.catalogue.append(('name','url'))
        return self.catalogue

    def getListFromPsudUserProfile(self):

        url = "/sipbar/sipbar/SipUser"

        result = requests.get(self.jossoSession.baseUrl + url + "?_responseMode=json" ,
                              cookies=self.jossoSession.cookies, headers=self.jossoSession.headers)

        if result.status_code == 200:
            jsonResult = json.loads(result.text)

        apps = [app for app in jsonResult['data']['listeApplication']]

        for app in apps:
            icoUrl = '/gud/gud/Application/{}/icon?'.format(app['id'])
            icoReq = requests.get(self.jossoSession.baseUrl + icoUrl,
                         cookies=self.jossoSession.cookies, headers=self.jossoSession.headers)

            self.catalogue.append((app['code'],app['url'],icoReq.content))

        return self.catalogue

