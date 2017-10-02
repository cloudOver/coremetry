from coremetry.models.coremetry import ResourceType, Resource, Record

def store(self, resource_type_name, resource_id, value, owner=None):
    try:
        res_type = ResourceType.objects.get(name=resource_type_name)
    except:
        res_type = ResourceType(name=resource_type_name)
        res_type.save()

    try:
        res = res_type.resource_set.get(object_id=resource_id)
    except:
        res = Resource()
        res.resource_type = res_type
        res.object_id = resource_id
        res.user = owner
        res.save()

    record = Record()
    record.value = value
    record.resource = res