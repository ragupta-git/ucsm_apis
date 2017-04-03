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

def _vlan_parent_get(vlan_type, fabric, caller="_vlan_parent_dn_get"):
    if vlan_type != "lan" and vlan_type != "appliance":
        raise UcsOperationError(caller,
                                "Vlan Type %s does not exist" % vlan_type)

    dn = _lan_dn if vlan_type == "lan" else _appliance_dn
    mo = handle.query_dn(dn)
    if mo is None:
        raise UcsOperationError(caller,
                                "Fabric %s '%s' does not exist."
                                % (vlan_type, dn))
    if fabric is None:
        return mo

    dn = dn + fabric
    mo = handle.query_dn(dn)
    if mo is None:
        raise UcsOperationError(caller,
                                "Fabric %s '%s' does not exist."
                                % (fabric, dn))
    return mo


def vlan_create(handle, name, id, vlan_type="lan", fabric=None,
                sharing="none", compression_type="included", default_net="no",
                policy_owner="local", mcast_policy_name=None, pub_nw_name=None,
                **kwargs):
    """
    Creates VLAN

    Args:
        handle (UcsHandle)
        name (string) : VLAN Name
        id (string): VLAN ID
        vlan_type (string) : Type of Vlan ["lan", "appliance"]
        fabric (string): "A" or "B"
        sharing (string) : Vlan sharing
                           ["community", "isolated", "none", "primary"]
        compression_type (string) : ["excluded", "included"]
        default_net (string) : ["false", "no", "true", "yes"]
        policy_owner (string): policy_owner
        mcast_policy_name (string) : Multicast policy name
        pub_nw_name (string) : Name of primary vlan, applicable for isolated
                               or community vlan
        **kwargs: Any additional key-value pair of managed object(MO)'s
                  property and value, which are not part of regular args.
                  This should be used for future version compatibility.
    Returns:
        FabricVlan: Managed Object

    Example:
        vlan_create(handle, "none", "vlan-lab", "123",  "sample_mcast_policy",
                    "included")
    """
    from ucsmsdk.mometa.fabric.FabricVlan import FabricVlan

    obj = _vlan_parent_get(vlan_type, fabric, caller="vlan_create")
    mo = FabricVlan(parent_mo_or_dn=obj,
                      name=name,
                      id=id,
                      sharing=sharing,
                      compression_type=compression_type,
                      default_net=default_net,
                      policy_owner=policy_owner,
                      mcast_policy_name=mcast_policy_name,
                      pub_nw_name=pub_nw_name,
                      )

    mo.set_prop_multiple(**kwargs)
    handle.add_mo(mo, modify_present=True)
    handle.commit()
    return mo


def vlan_get(handle, name, vlan_type="lan", fabric=None, caller="vlan_get"):
    """
    Gets the VLAN
    Args:
        handle (UcsHandle)
        name (string) : VLAN Name
        vlan_type (string) : Type of Vlan ["lan", "appliance"]
        domain_group (string) : Full domain group name

    Returns:
        FabricVlan: Managed Object OR None
    Example:
        bool_var = vlan_exists(handle, "none", "vlan-lab", "123",
                        "sample_mcast_policy", "included")
    """
    if vlan_type != "lan" and vlan_type != "appliance":
        raise UcsOperationError("vlan_get",
                                 "Vlan Type %s does not exist" % vlan_type)

    dn = _lan_dn if vlan_type == "lan" else _appliance_dn
    dn += "/" + fabric if fabric else ""
    dn += "/net-" + name
    mo = handle.query_dn(dn)
    if mo is None:
        raise UcsOperationError(caller, "Vlan '%s' does not exist" % dn)
    return mo


def vlan_exists(handle, name, vlan_type="lan", fabric=None, **kwargs):
    """
    Checks if the given VLAN already exists with the same params
    Args:
        handle (UcsHandle)
        name (string) : VLAN Name
        vlan_type (string) : Type of Vlan ["lan", "appliance"]
        domain_group (string) : Full domain group name
        **kwargs: key-value pair of managed object(MO) property and value, Use
                  'print(ucsccoreutils.get_meta_info(<classid>).config_props)'
                  to get all configurable properties of class
    Returns:
        (True/False, MO/None)
    Example:
        bool_var = vlan_exists(handle, "none", "vlan-lab", "123",
                        "sample_mcast_policy", "included")
    """
    try:
        mo = vlan_get(handle, name, vlan_type, fabric, caller="vlan_exists")
    except UcsOperationError:
        return (False, None)
    mo_exists = mo.check_prop_match(**kwargs)
    return (mo_exists, mo if mo_exists else None)


def vlan_modify(handle, name, vlan_type="lan", fabric=None, **kwargs):
    mo = vlan_get(handle, name, vlan_type, fabric, caller="vlan_modify")
    mo.set_prop_multiple(**kwargs)
    handle.set_mo(mo)
    handle.commit()
    return mo


def vlan_delete(handle, name, vlan_type="lan", fabric=None):
    """
    Deletes a VLAN
    Args:
        handle (UcsHandle)
        name (string) : VLAN Name
        vlan_type (string) : Type of Vlan ["lan", "appliance"]
        domain_group (string) : Full domain group name
    Returns:
        None
    Example:
        vlan_delete(handle, "lab-vlan")
    """
    mo = vlan_get(handle, name, vlan_type, fabric, caller="vlan_delete")
    handle.remove_mo(mo)
    handle.commit()


def lan_pin_group_create(handle, name, policy_owner="local", descr=None,
                         **kwargs):
    mo = FabricLanPinGroup(parent_mo_or_dn=_lan_dn,
                           name=name,
                           policy_owner=policy_owner,
                           descr=descr)
    mo.set_prop_multiple(**kwargs)
    handle.add_mo(mo, True)
    handle.commit()
    return mo


def lan_pin_group_get(handle, name, caller="lan_pin_group_get"):
    dn = _lan_dn + "/lan-pin-group-" + name
    mo = handle.query_dn(dn)
    if mo is None:
        raise UcsOperationError(caller,
                                "LAN Pin Group '%s' does not exist" % dn)
    return mo


def lan_pin_group_exists(handle, name, **kwargs):
    try:
        lan_pin_group_get(handle, name, caller="lan_pin_group_exists")
    except UcsOperationError:
        return (False, None)
    mo_exists = mo.check_prop_match(**kwargs)
    return (mo_exists, mo if mo_exists else None)


def lan_pin_group_modify(handle, name, **kwargs):
    mo = lan_pin_group_get(handle, name, caller="lan_ping_group_modify")
    mo.set_prop_multiple(**kwargs)
    handle.set_mo(mo)
    handle.commit()
    return mo


def lan_pin_group_delete(handle, name):
    mo = lan_pin_group_get(handle, name, "lan_ping_group_delete")
    handle.remove_mo(mo)
    handle.commit()


def lan_pin_group_target_add(handle, lan_pin_group_name, fabric_id,
                             slot_id="0", port_id="0", aggr_port_id="0",
                             ep_dn=None, **kwargs):

    lan_pin_group = lan_pin_group_get(handle, lan_pin_group_name,
                                      caller="lan_pin_group_target_add")

    mo = FabricLanPinTarget(parent_mo_or_dn=lan_pin_group,
                            fabric_id=fabric_id,
                            slot_id=slot_id,
                            port_id=port_id,
                            aggr_port_id=aggr_port_id,
                            ep_dn=ep_dn)

    mo.set_prop_multiple(**kwargs)
    handle.add_mo(mo, True)
    handle.commit()
    return mo


def lan_pin_group_target_get(handle, lan_pin_group_name, fabric_id,
                             caller="lan_pin_group_target_get"):
    lan_pin_group_dn = _lan_dn + "/lan-pin-group-" + lan_pin_group_name
    dn = lan_pin_group_dn + "/target-" + fabric_id
    mo = handle.query_dn(dn)
    if mo is None:
        raise UcsOperationError(
            caller, "Lan Pin Group Target '%s' does not exist" % dn)
    return mo


def lan_pin_group_target_exists(handle, lan_pin_group_name, fabric_id,
                                **kwargs):
    try:
        lan_pin_group_target_get(handle, lan_pin_group_name, fabric_id,
                                 caller="lan_pin_group_target_exists")
    except UcsOperationError:
        return (False, None)
    mo_exists = mo.check_prop_match(**kwargs)
    return (mo_exists, mo if mo_exists else None)


def lan_pin_group_target_modify(handle, lan_pin_group_name, fabric_id,
                                **kwargs):
    lan_pin_group_target_get(handle, lan_pin_group_name, fabric_id,
                             caller="lan_pin_group_target_modify")
    mo.set_prop_multiple(**kwargs)
    handle.set_mo(mo)
    handle.commit()
    return mo


def lan_pin_group_target_remove(handle, lan_pin_group_name, fabric_id):
    lan_pin_group_target_get(handle, lan_pin_group_name, fabric_id,
                             caller="lan_pin_group_target_remove")
    handle.remove_mo(mo)
    handle.commit()


def vlan_group_create(handle, name, policy_owner="local", type="mgmt",
                      descr=None, native_net=None,  **kwargs):
    mo = FabricNetGroup(parent_mo_or_dn=_lan_dn,
                        name=name,
                        policy_owner=policy_owner,
                        type=type,
                        descr=descr,
                        native_net=native_net)

    mo.set_prop_multiple(**kwargs)
    handle.add_mo(mo, True)
    handle.commit()
    return mo


def vlan_group_get(handle, name, caller="vlan_group_get"):
    dn = _lan_dn + "/net-group-" + name
    mo = handle.query_dn(dn)
    if mo is None:
        raise UcsOperationError(caller,
                                "VLAN Group '%s' does not exist" % dn)
    return mo


def vlan_group_exists(handle, name, **kwargs):
    try:
        vlan_group_get(handle, name, caller="vlan_group_exists")
    except UcsOperationError:
        return (False, None)
    mo_exists = mo.check_prop_match(**kwargs)
    return (mo_exists, mo if mo_exists else None)


def vlan_group_modify(handle, name, **kwargs):
    mo = vlan_group_get(handle, name, caller="vlan_group_modify")
    mo.set_prop_multiple(**kwargs)
    handle.set_mo(mo)
    handle.commit()
    return mo


def vlan_group_delete(handle, name):
    mo = vlan_group_get(handle, name, caller="vlan_group_delete")
    handle.remove_mo(mo)
    handle.commit()


def vlan_group_vlan_add(handle, vlan_group_name, name, **kwargs):

    vlan = vlan_get(handle, name, caller="vlan_group_vlan_add")

    vlan_group = vlan_group_get(handle, vlan_group_name,
                                caller="vlan_group_vlan_add")

    mo = FabricPooledVlan(parent_mo_or_dn=vlan_group,
                          name=name)
    mo.set_prop_multiple(**kwargs)
    handle.add_mo(mo, True)
    handle.commit()
    return mo


def vlan_group_vlan_get(handle, vlan_group_name, name,
                        caller="vlan_group_vlan_get"):
    vlan_group_dn = _lan_dn + "/net-group-" + vlan_group_name
    dn = vlan_group_dn + "/net-" + name
    mo = handle.query_dn(dn)
    if mo is None:
        raise UcsOperationError(
            caller, "vlan member '%s' does not exist" % dn)
    return mo


def vlan_group_vlan_exists(handle, vlan_group_name, name,
                           **kwargs):
    try:
        vlan_group_vlan_get(handle, vlan_group_name, name,
                            caller="vlan_group_vlan_exists")
    except UcsOperationError:
        return (False, None)
    mo_exists = mo.check_prop_match(**kwargs)
    return (mo_exists, mo if mo_exists else None)


def vlan_group_vlan_remove(handle, vlan_group_name, name):
    vlan_group_vlan_get(handle, vlan_group_name, name,
                        caller="vlan_group_vlan_remove")
    handle.remove_mo(mo)
    handle.commit()


def vlan_group_org_add(handle, vlan_group_name, org_dn="org-root", **kwargs):

    org = handle.query_dn(org_dn)
    if org is None:
        raise UcsOperationError("vlan_group_org_add",
                                "Org '%s' does not exist" % org_dn)

    vlan_group = vlan_group_get(handle, vlan_group_name,
                                caller="vlan_group_org_add")

    mo = FabricVlanGroupReq(parent_mo_or_dn=org,
                            name=name)
    mo.set_prop_multiple(**kwargs)
    handle.add_mo(mo, True)
    handle.commit()
    return mo


def vlan_group_org_get(handle, vlan_group_name, org_dn="org-root",
                       caller="vlan_group_org_get"):
    dn = org_dn + "/vlan-group-req-" + vlan_group_name
    mo = handle.query_dn(dn)
    if mo is None:
        raise UcsOperationError(
            caller, "vlan group org '%s' does not exist" % dn)
    return mo


def vlan_group_org_exists(handle, vlan_group_name, org_dn="org-root",
                           **kwargs):
    try:
        vlan_group_org_get(handle, vlan_group_name, org_dn,
                           caller="vlan_group_org_exists")
    except UcsOperationError:
        return (False, None)
    mo_exists = mo.check_prop_match(**kwargs)
    return (mo_exists, mo if mo_exists else None)


def vlan_group_org_remove(handle, vlan_group_name, org_dn="org-root"):
    vlan_group_org_get(handle, vlan_group_name, org_dn,
                       caller="vlan_group_org_remove")
    handle.remove_mo(mo)
    handle.commit()


def vlan_group_uplink_port_add(handle, vlan_group_name,
                               switch_id, slot_id, port_id,
                               is_native="no", auto_negotiate="yes",
                               admin_state="enabled", name=None, **kwargs):
    vlan_group = vlan_group_get(handle, vlan_group_name,
                                caller="vlan_group_uplink_port_add")

    mo = FabricEthVlanPortEp(parent_mo_or_dn=vlan_group,
                             switch_id=switch_id,
                             slot_id=slot_id,
                             port_id=port_id,
                             is_native=is_native,
                             auto_negotiate=auto_negotiate,
                             admin_state=admin_state,
                             name=name)

    mo.set_prop_multiple(**kwargs)
    handle.add_mo(mo, True)
    handle.commit()
    return mo


def vlan_group_uplink_port_get(handle, vlan_group_name,
                               switch_id, slot_id, port_id,
                               caller="vlan_group_uplink_port_get"):
    vlan_group_dn = _lan_dn + "/net-group-" + vlan_group_name
    dn = vlan_group_dn + "/phys-switch-" + switch_id + "-slot-" + slot_id + \
        "-port-" + port_id
    mo = handle.query_dn(dn)
    if mo is None:
        raise UcsOperationError(
            caller, "vlan group member '%s' does not exist" % dn)
    return mo


def vlan_group_uplink_port_exists(handle, vlan_group_name,
                                  switch_id, slot_id, port_id,
                                  **kwargs):
    try:
        vlan_group_uplink_port_get(handle, vlan_group_name,
                                   switch_id, slot_id, port_id,
                                   caller="vlan_group_uplink_port_exists")
    except UcsOperationError:
        return (False, None)
    mo_exists = mo.check_prop_match(**kwargs)
    return (mo_exists, mo if mo_exists else None)


def vlan_group_uplink_port_remove(handle, vlan_group_name,
                                  switch_id, slot_id, port_id):
    vlan_group_uplink_port_get(handle, vlan_group_name,
                               switch_id, slot_id, port_id,
                               caller="vlan_group_uplink_port_remove")
    handle.remove_mo(mo)
    handle.commit()

