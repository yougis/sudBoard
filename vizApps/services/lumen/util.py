import yaml
import json

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