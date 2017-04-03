# Copyright 2017 Cisco Systems, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This module performs the Vlan related operation
"""
from ucsmsdk.ucsexception import UcsOperationError

_lan_dn = "fabric/lan"
_appliance_dn = "fabric/eth-estc"

def lan_port_channel_create(handle, fabric, port_id,
                            flow_ctrl_policy="default",
                            lacp_policy_name="default",
                            admin_speed="10gbps", oper_speed="10gbps",
                            auto_negotiate="yes", admin_state="enabled",
                            **kwargs):
    parent_dn = _lan_dn + "/" + fabric
    mo = FabricEthLanPc(parent_mo_or_dn=parent_dn,
                        port_id=port_id,
                        flow_ctrl_policy=flow_ctrl_policy,
                        lacp_policy_name=lacp_policy_name,
                        admin_speed=admin_speed,
                        oper_speed=oper_speed,
                        auto_negotiate=auto_negotiate,
                        admin_state=admin_state)

    mo.set_prop_multiple(**kwargs)
    handle.add_mo(mo, modify_present=True)
    handle.commit()
    return mo


def lan_port_channel_get(handle, fabric, port_id,
                         caller="lan_port_channel_get"):
    dn = _lan_dn + "/" + fabric + "/pc-" + port_id
    mo = handle.query_dn(dn)
    if mo is None:
        raise UcsOperationError(caller,
                                "Port Channel '%s' does not exist" % dn)
    return mo


def lan_port_channel_exists(handle, fabric, port_id, **kwargs):
    try:
        mo = lan_port_channel_get(handle, fabric, port_id,
                                  caller="lan_port_channel_exists")
    except UcsOperationError:
        return (False, None)
    mo_exists = mo.check_prop_match(**kwargs)
    return (mo_exists, mo if mo_exists else None)


def lan_port_channel_modify(handle, fabric, port_id, **kwargs):
    mo = lan_port_channel_get(handle, fabric, port_id,
                              caller="lan_port_channel_modify")
    mo.set_prop_multiple(**kwargs)
    handle.set_mo(mo)
    handle.commit()
    return mo


def lan_port_channel_delete(handle, fabric, port_id):
    mo = lan_port_channel_get(handle, fabric, port_id,
                              caller="lan_port_channel_delete")
    handle.remove_mo(mo)
    handle.commit()
    return mo


def lan_port_channel_port_add(handle):
    pass


def lan_port_channel_port_get(handle):
    pass


def lan_port_channel_port_exists(handle):
    pass


def lan_port_channel_port_modify(handle):
    pass


def lan_port_channel_port_remove(handle):
    pass

