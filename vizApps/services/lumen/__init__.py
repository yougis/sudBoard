import yaml
from .util import SpecYamlCreator

yaml.add_representer(SpecYamlCreator, SpecYamlCreator.spec_representer)
yaml.add_constructor(u'!SpecYamlCreator', SpecYamlCreator.spec_constructor,Loader=yaml.SafeLoader)