from django.db import models
from vizApps.domain.lumen.view import ViewEntity
from yamlfield.fields import YAMLField


class TransformEntity(models.Model):
    name = models.CharField(max_length=30)
    specYaml = YAMLField(blank=True)
    view = models.ForeignKey(ViewEntity, on_delete=models.CASCADE)


    def save(self, *args, **kwargs):
        self.saveSpec()
        super().save(*args, **kwargs)
        self.view.save()

    def saveSpec(self):
        transforms = self.get_spec()['transforms']

        if transforms == None and self.view.name=='demo':
            transforms = {
                                 'type': 'aggregate',
                                 'by':'statut_code',
                                 'columns' : ['nombre'],
                                 'method':'sum'
                             }

        self.specYaml = transforms

    def get_spec(self):
        transform=None

        return {'transforms' : transform}


