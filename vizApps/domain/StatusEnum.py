from enum import Enum
from django.db import models
from django.utils.translation import gettext_lazy as _
class StatusEnum(Enum):
#ennumeration Publication
    DRAFT = 'Brouillon'
    PUBLISH = 'Publié'
