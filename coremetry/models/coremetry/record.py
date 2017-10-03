from corecluster.models.common_models import CoreModel
from django.db import models
from coremetry.models.coremetry.resource import Resource


class Record(CoreModel):
    serializable = [
        'created',
        'value'
    ]
    created = models.DateTimeField(auto_now_add=True)
    value = models.DecimalField(max_digits=40, decimal_places=2)
    resource = models.ForeignKey(Resource, db_index=True)