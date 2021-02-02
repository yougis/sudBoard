from django.db import models
from vizApps.domain.lumen.target import TargetEntity
from yamlfield.fields import YAMLField
from vizApps.services.lumen.util import SpecYamlCreator


class ViewEntity(models.Model):
    name = models.CharField(max_length=30)
    specYaml = YAMLField(blank=True)
    target = models.ForeignKey(TargetEntity, on_delete=models.CASCADE)


    def get_external_spec(self):
        transforms = [transform.specYaml for transform in self.transformentity_set.all()]
        return {'transforms': transforms}

    def save(self, *args, **kwargs):
        self.saveSpec()
        super().save(*args, **kwargs)
        self.target.save()


    def saveSpec(self):
        transforms = self.get_external_spec()['transforms']

        if len(transforms)>0:
            self.specYaml['transforms'] = transforms

    def __repr__(self):
        keyVals = ", ".join(["{}={}".format(i[0], i[1]) for i in [v for v  in vars(self).items()]])
        return "%s(%s)" % ( self.__class__.__name__,keyVals)

    def to_json(self):
        pass

    def to_yaml(self):
        pass