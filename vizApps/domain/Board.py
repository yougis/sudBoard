from django.db import models
from django.utils.text import slugify
from vizApps.domain.StatusEnum import StatusEnum
from vizApps.domain.TypeBoardEnum import TypeBoardEnum

class BoardEntity(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, unique=True)

    status = models.CharField(
        max_length=15,
        choices=[(status.name, status.value ) for status in StatusEnum],
        default=StatusEnum.DRAFT
    )

    type = models.CharField(
        max_length=15,
        choices=[(typeBoard.name, typeBoard.value) for typeBoard in TypeBoardEnum],
        default = TypeBoardEnum.DASHBOARD
    )

    def __str__(self):
        return self.name

    def _get_unique_slug(self):
        '''
        In this method a unique slug is created
        '''
        slug = slugify(self.name)
        unique_slug = slug
        num = 1
        while BoardEntity.objects.filter(slug=unique_slug).exists():
            unique_slug = '{}-{}'.format(slug, num)
            num += 1
        return unique_slug

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._get_unique_slug()
        super().save(*args, **kwargs)
