import param


class StudioApp(param.Parameterized):
    def __init__(self, **params):
        super(StudioApp, self).__init__(**params)
