import yaml, json, panel as pn

CENTER_TYPE = {'master': pn.Spacer(max_width=50,sizing_mode='stretch_width'),
               'equal': pn.Spacer(sizing_mode='stretch_width'),
               'minus': pn.Spacer(min_width=400,sizing_mode='stretch_width')}

class SpecYamlCreator():

    def __init__(self,**kwargs):
        for k,v in kwargs.items():
            self.__setattr__(k, v)

    def to_json(self):
        return json.dumps(self.__dict__)

    def to_yaml(self):
        return yaml.dump(self.__dict__)

    def get_dic(self):
        return self.__dict__


    def spec_constructor(loader, node):
        spec = loader.construct_scalar(node)
        return spec

    def __repr__(self):
        keyVals = ", ".join(["{}={}".format(i[0], i[1]) for i in [v for v  in vars(self).items()]])
        return "%s(%s)" % ( self.__class__.__name__,keyVals)

    def spec_representer(dumper, data):
        return dumper.represent_scalar(u'!SpecYamlCreator', u'%s' % data)




def centerContentGrid(content):
    gspec = pn.GridSpec(sizing_mode="stretch_width")
    gspec[:, 0] = pn.Spacer()
    gspec[:, 1:4] = content
    gspec[:, 4] = pn.Spacer()
    return gspec

def centerContent(content, type='equal'):
    #r = CENTER_TYPE.get(type)
    r = pn.Spacer(sizing_mode='stretch_width')
    layout = pn.Row(r, content, r)
    return layout

def centerContentWidget(content):
    css = """
            .bk.light-bk {
                background: #ececec;
            }
        """
    pn.config.raw_css.append(css)

    css_class = ['panel-widget-box', 'light-bk']

    r = pn.Spacer(sizing_mode='stretch_width')
    box = pn.WidgetBox(content,sizing_mode='stretch_width', css_classes=css_class)
    layout= pn.Row(r,box,r)
    return layout