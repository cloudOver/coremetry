from corecluster.models.common_models import CoreModel
from django.db import models


class ResourceType(CoreModel):
    name = models.CharField(max_length=100, db_index=True)
