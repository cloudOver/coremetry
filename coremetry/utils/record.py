"""
Copyright (C) 2014-2017 cloudover.io ltd.
This file is part of the CloudOver.org project

Licensee holding a valid commercial license for this software may
use it in accordance with the terms of the license agreement
between cloudover.io ltd. and the licensee.

Alternatively you may use this software under following terms of
GNU Affero GPL v3 license:

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version. For details contact
with the cloudover.io company: https://cloudover.io/


This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.


You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""


from coremetry.models.coremetry import ResourceType, Resource, Record

def store(resource_type_name, resource_id, value, owner=None):
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
    record.value = float(value)
    record.resource = res
    record.save()