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

from corenetwork.network_mixin import NetworkMixin
from corenetwork.os_mixin import OsMixin
from corenetwork.api_mixin import ApiMixin
from corenetwork.hook_interface import HookInterface
from corenetwork.utils.logger import log
from corecluster import settings
import importlib


class Hook(NetworkMixin, OsMixin, ApiMixin, HookInterface):
    task = None

    def cron(self, interval):
        for app_name in settings.APPS:
            app = importlib.import_module(app_name).MODULE
            if 'coremetry' in app:
                for coremetry_module in app['coremetry']:
                    try:
                        log(msg='Monitoring ' + coremetry_module)
                        module = importlib.import_module(coremetry_module)
                        module.monitor()
                    except Exception as e:
                        log(msg='Failed to call coremetry module %s' % coremetry_module, exception=e,
                            tags=('error', 'critical'))
                        print('Failed to call coremetry module %s from %s: %s' % (coremetry_module, app_name, str(e)))
