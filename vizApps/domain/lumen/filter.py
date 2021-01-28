from django.db import models
from vizApps.domain.lumen.target import TargetEntity
from yamlfield.fields import YAMLField
from vizApps.services.lumen.util import SpecYamlCreator

class FilterEntity(models.Model):
    name = models.CharField(max_length=30)
    specYaml = YAMLField(blank=True)
    target = models.ForeignKey(TargetEntity, on_delete=models.CASCADE)

    def get_spec(self):
        filters = None
        return {'filters': filters}

    def save(self, *args, **kwargs):
        self.saveSpec()
        super().save(*args, **kwargs)
        self.target.save()

    def saveSpec(self):
        filters = self.get_spec()['filters']

        if filters == None and self.target.name=='demo':
            filters = {
                'field': 'Etat administratif',
                'type': 'widget',
                'multi': True,
                'empty_select': True
            }

        self.specYaml = filters