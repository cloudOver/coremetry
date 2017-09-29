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
from corecluster.models.core import VM, Node, Image, Storage
from coremetry.models.coremetry import ResourceType, Resource, Record

from xml.etree import ElementTree
import libvirt


class Hook(NetworkMixin, OsMixin, ApiMixin, HookInterface):
    task = None
    def _store(self, resource_type_name, resource_id, value):
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
            res.save()

        record = Record()
        record.value = value
        record.resource = res

    def _monitor_node(self, node, conn):
        mem_stats = conn.getMemoryStats(libvirt.VIR_NODE_MEMORY_STATS_ALL_CELLS)

        self._store('node_memory_available', node.id, mem_stats['total'] - mem_stats['buffers'] - mem_stats['cached'])
        self._store('node_memory_free', node.id, mem_stats['free'])
        self._store('node_memory_total', node.id, mem_stats['total'])

        arch, mem_total_mb, cpus, cpu_freq_mhz, numa_nodes, sockets_per_node, cores_per_socket, threads_per_core = conn.getCPUInfo()

        idle = 0
        iowait = 0
        kernel = 0
        user = 0
        for core in xrange(numa_nodes * sockets_per_node * cores_per_socket * threads_per_core):
            cpu_stats = conn.getCPUInfo(core)
            idle += cpu_stats['idle']
            iowait += cpu_stats['iowait']
            kernel += cpu_stats['kernel']
            user += cpu_stats['user']

        self._store('node_cpu_idle', node.id, idle)
        self._store('node_cpu_iowait', node.id, iowait)
        self._store('node_cpu_kernel', node.id, kernel)
        self._store('node_cpu_user', node.id, user)

        self._store('node_vms_defined', node.id, node.vm_set.count())
        self._store('node_vms_running', node.id, node.vm_set.filter(state='running').count())
        self._store('node_vms_real', node.id, conn.listDomainsID())

        storage = conn.storagePoolLookupByName('images')
        storage.refresh()
        self._store('node_images_pool_allocated', node.id, storage.info()[2])
        self._store('node_images_pool_free', node.id, storage.info()[3])
        self._store('node_images_volumes_real', node.id, len(storage.listAllVolumes()))
        self._store('node_images_volumes_defined', node.id, node.vm_set.exclude(base_image=None).count())

    def _monitor_vm(self, vm, conn):
        dom = conn.lookupByName(vm.libvirt_name)

        cpu_stats = dom.getCPUStats(True)
        self._store('vm_memory_used', vm.id, dom.memoryStats()['rss'])
        self._store('vm_cpu_time', vm.id, cpu_stats['cpu_time'])
        self._store('vm_system_time', vm.id, cpu_stats['system_time'])
        self._store('vm_user_time', vm.id, cpu_stats['user_time'])
        self._store('vm_cpu_time', vm.id, dom.info()[4])

        tree = ElementTree.fromstring(dom.XMLDesc())
        for interface in tree.findall('devices/interface'):
            dev_name = interface.find('target').get('dev')
            dev_stats = dom.interfaceStats(dev_name)

            network_name = interface.find('source').get('network').split('-')[1]
            self._store('vm_net_in_bytes_' + network_name, vm.id, dev_stats[0])
            self._store('vm_net_in_packets_' + network_name, vm.id, dev_stats[1])
            self._store('vm_net_out_bytes_' + network_name, vm.id, dev_stats[4])
            self._store('vm_net_out_packets_' + network_name, vm.id, dev_stats[5])

        for disk in tree.findall('devices/disk'):
            dev_name = disk.find('target').get('dev')
            dev_stats = dom.blockStats(dev_name)

            self._store('vm_disk_read_bytes_' + dev_name, vm.id, dev_stats[1])
            self._store('vm_disk_write_bytes_' + dev_name, vm.id, dev_stats[3])

    def _monitor_storage(self, storage, conn):
        st = conn.storagePoolLookupByName(storage.name)
        st.refresh()

        self._store('storage_allocation', storage.id, st.info()[2])
        self._store('storage_available', storage.id, st.info()[3])

    def _monitor_system(self, conn):
        hostname = conn.getHostname()
        for interface in conn.listInterfaces():
            rx = int(open('/sys/class/net/' + interface + '/statistics/rx_bytes'))
            rx_bytes = rx.read(10240)
            rx.close()

            rx = int(open('/sys/class/net/' + interface + '/statistics/rx_packets'))
            rx_packets = rx.read(10240)
            rx.close()

            tx = int(open('/sys/class/net/' + interface + '/statistics/tx_bytes'))
            tx_bytes = rx.read(10240)
            tx.close()

            tx = int(open('/sys/class/net/' + interface + '/statistics/tx_packets'))
            tx_packets = rx.read(10240)
            tx.close()

            self._store('system_net_' + interface + '_rx_bytes', hostname, rx_bytes)
            self._store('system_net_' + interface + '_rx_packets', hostname, rx_packets)
            self._store('system_net_' + interface + '_tx_bytes', hostname, tx_bytes)
            self._store('system_net_' + interface + '_tx_packets', hostname, tx_packets)

        mem_stats = conn.getMemoryStats(libvirt.VIR_NODE_MEMORY_STATS_ALL_CELLS)

        self._store('node_memory_available', hostname, mem_stats['total'] - mem_stats['buffers'] - mem_stats['cached'])
        self._store('node_memory_free', hostname, mem_stats['free'])
        self._store('system_memory_total', hostname, mem_stats['total'])

    def cron(self, interval):
        for node in Node.objects.filter(state='ok'):
            conn = node.libvirt_conn()
            self._monitor_node(node, conn)
            for vm in node.vm_set.filter(state='running'):
                self._monitor_vm(vm, conn)

            conn.close()

        conn = libvirt.open('qemu:///system')
        for storage in Storage.objects.filter(state='ok'):
            self._monitor_storage(storage, conn)

        self._monitor_system(conn)
        conn.close()
