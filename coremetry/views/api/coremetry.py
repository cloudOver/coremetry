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


from corecluster.utils import validation as v
from corecluster.utils.decorators import register
from corecluster.utils.exception import CoreException
import coremetry.models.coremetry


@register(auth='token')
def list_resources(context):
    """
    Get list of monitored resources available for user
    """
    return [r.name for r in coremetry.models.coremetry.ResourceType.objects.all()]



@register(auth='token', validate={'resource_type': v.is_string(),
                                  'object_id': v.is_id()})
def list_records(context, resource_type, object_id):
    """
    Get list of records for given resource type and object id
    """
    try:
        res_type = coremetry.models.coremetry.ResourceType.objects.get(name=resource_type)
    except:
        raise CoreException('resource_type_not_found')

    object_records = res_type.resource_set.filter(user_id=context.user_id).get(object_id=object_id)
    return [r.to_dict for r in object_records.record_set.order_by('created').all()]