from django.db import models
from vizApps.domain.Board import BoardEntity
from yamlfield.fields import YAMLField
from vizApps.services.lumen.util import SpecYamlCreator
import os
from sudBoard.settings import BASE_DIR

path = BASE_DIR + '/vizApps/services/intake/'


class TargetEntity(models.Model):
    name = models.CharField(max_length=30)
    specYaml = YAMLField(blank=True)
    board = models.ForeignKey(BoardEntity, on_delete=models.CASCADE)

    def get_spec(self):
        views = [view.specYaml for view in self.viewentity_set.all()]
        filters = [filter.specYaml for filter in self.filterentity_set.all()]
        source = {'type': 'intake',
                  'uri': os.path.join(path, 'catalog.yml')
                  }

        return {'name':self.name,'title':self.name, 'source':source,'views' : views, 'filters':filters}

    def save(self, *args, **kwargs):
        self.saveSpec()
        super().save(*args, **kwargs)


    def saveSpec(self):
        views = self.get_spec()['views']
        filters = self.get_spec()['filters']
        source = self.get_spec()['source']
        title = self.get_spec()['title']
        name= self.get_spec()['name']
        p = {
            'name': name,
            'title': title ,
            'source':source
        }
        if len(views) > 0:
            if views[0]:
                p['views'] = views
        if len(filters) > 0:
            if filters[0]:
                p['filters'] = filters

        spec = SpecYamlCreator(**p)
        self.specYaml = spec.to_yaml()