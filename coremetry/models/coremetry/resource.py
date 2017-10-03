from coremetry.models.coremetry.resource_type import ResourceType
from django.db import models
from corecluster.models.common_models import CoreModel, UserMixin


class Resource(CoreModel, UserMixin):
    resource_type = models.ForeignKey(ResourceType)
    object_id = models.CharField(max_length=100, db_index=True)
