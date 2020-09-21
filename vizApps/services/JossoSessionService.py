import urllib , base64
from sudBoard.settings import BASE_URL



class JossoSession():
    # parametre pour se connecter à une application en dev
    dev = 'false'
    baseUrlDev = 'http://localhost'
    loginDev = "a"
    passwordDev = ""

    # parametres  pour se connecter à une application en prod
    baseUrl = BASE_URL.__getitem__(1)[1]
    login = "hugo.roussaffa"
    login = login + '@province-sud.nc'
    password = "MCot9a9.u"
    jossoEndpoint = '/josso/signon/login.do'

    cookies = {}
    headers = {}
    headers['User-Agent'] = 'SudBoard'
    headers['Content-Type'] = 'application/json'

    def __init__(self):
        if self.dev == 'true':  # connection en basic auth
            login = self.loginDev
            password = self.passwordDev
            baseUrl = self.baseUrlDev
            post_url = baseUrl
            concatenated = login + ":" + password
            data = base64.b64encode(concatenated.encode('ascii'))
            headerData = "Basic " + data.decode('ascii')
            self.headers["Authorization"] = headerData.encode('ascii')

        else:  # connection avec Josso
            baseUrl = self.baseUrl
            post_url = baseUrl + self.jossoEndpoint
            post_data = urllib.parse.urlencode({
                'josso_username': self.login,
                'josso_password': self.password,
                'josso_cmd': 'login'
            }).encode('ascii')
            post_response = urllib.request.urlopen(url=post_url, data=post_data)

            # on récupère le cookie JOSSO_SESSION_ID
            jsessionId = post_response.getheader('Set-Cookie').split(',')[0].split(';')[0].strip()
            josso_sessionId = post_response.getheader('Set-Cookie').split(',')[1].split(';')[0].strip()

            self.cookies.update([(josso_sessionId.split('=')[0], josso_sessionId.split('=')[1])])
            self.cookies.update([(jsessionId.split('=')[0], jsessionId.split('=')[1])])
            self.cookies.update([('usernameLoginJOSSO', self.login)])

    def connectJosso(self):
        pass