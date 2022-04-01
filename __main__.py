"""An Azure RM Python Pulumi program"""

import pulumi
from pulumi import Output
from pulumi_azure_native import resources, network, compute
from infra.vnets import VNETS
from infra.vms import VM_DATA, VM_DATA_NO_PIP

config = pulumi.Config()
RG_NAME = config.require("rg_name")
password = config.require("passwd")

# Create an Azure Resource Group
resource_group = resources.ResourceGroup(RG_NAME, resource_group_name=RG_NAME)


### NAT Gateway Practice ###
pip_prefix = network.PublicIPPrefix(
    "publicIPPrefix",
    location="northeurope",
    prefix_length=31,
    public_ip_address_version="IPv4",
    public_ip_prefix_name="test-ip-prefix",
    resource_group_name=resource_group.name,
    sku=network.PublicIPPrefixSkuArgs(
        name="Standard",
        tier="Regional",
    ),
)

nat_gateway = network.NatGateway(
    "natGateway",
    location="northeurope",
    nat_gateway_name="natgateway",
    public_ip_prefixes=[
        network.SubResourceArgs(
            id=pip_prefix.id,
        )
    ],
    resource_group_name=resource_group.name,
    sku=network.NatGatewaySkuArgs(
        name="Standard",
    ),
)

local_vnets = {}
subs = {}

# Create VNETs
for vnet, values in VNETS.items():
    net = network.VirtualNetwork(
        vnet,
        address_space=network.AddressSpaceArgs(
            address_prefixes=[values["vnet_address"]]
        ),
        virtual_network_name=vnet,
        resource_group_name=resource_group.name,
        location=values["region"],
    )
    local_vnets[vnet] = Output.concat(net.id)

    # Create subnets under each VNET
    for subnet in values["subnets"]:
        # Attaching NAT Gateway to specific subnet
        if subnet["name"] == "ManufacturingSystemSubnet":
            sub = network.Subnet(
                subnet["name"],
                address_prefix=subnet["subnet"],
                resource_group_name=resource_group.name,
                subnet_name=subnet["name"],
                virtual_network_name=net.name,
                nat_gateway=network.SubResourceArgs(id=nat_gateway.id),
            )
        else:
            sub = network.Subnet(
                subnet["name"],
                address_prefix=subnet["subnet"],
                resource_group_name=resource_group.name,
                subnet_name=subnet["name"],
                virtual_network_name=net.name,
            )
        # Neat trick to grab the subnet IDs and add them to dict
        subs[subnet["name"]] = Output.concat(sub.id)


# VNET peering, fairly static
vnet_peering = network.VirtualNetworkPeering(
    "Test-VNET-peer1",
    resource_group_name=resource_group.name,
    virtual_network_name="CoreServicesVnet",
    remote_virtual_network=network.SubResourceArgs(id=local_vnets["ManufacturingVnet"]),
    virtual_network_peering_name="peer",
)

second_vnet_peering = network.VirtualNetworkPeering(
    "Test-VNET-peer2",
    resource_group_name=resource_group.name,
    virtual_network_name="ManufacturingVnet",
    remote_virtual_network=network.SubResourceArgs(id=local_vnets["CoreServicesVnet"]),
    virtual_network_peering_name="peer",
)


# Create all the things for VM
for k, v in VM_DATA.items():
    pip = network.PublicIPAddress(
        f"{k}-pip",
        location=v["location"],
        public_ip_address_name=f"{k}-pip",
        resource_group_name=resource_group.name,
    )
    nic = network.NetworkInterface(
        f"{k}-nic",
        enable_accelerated_networking=True,
        ip_configurations=[
            network.NetworkInterfaceIPConfigurationArgs(
                name="ipconfig1",
                public_ip_address=network.PublicIPAddressArgs(id=pip.id),
                subnet=network.SubnetArgs(
                    id=subs[v["nic_subnet"]],
                ),
            )
        ],
        location=v["location"],
        network_interface_name=v["nic_name"],
        resource_group_name=resource_group.name,
    )
    virtual_machine = compute.VirtualMachine(
        f"{k} build",
        hardware_profile=compute.HardwareProfileArgs(
            vm_size="Standard_D1_v2",
        ),
        location=v["location"],
        network_profile=compute.NetworkProfileArgs(
            network_interfaces=[
                compute.NetworkInterfaceReferenceArgs(
                    id=nic.id,
                    primary=True,
                )
            ],
        ),
        os_profile=compute.OSProfileArgs(
            admin_password=password,
            admin_username="juliopdx",
            computer_name=k,
            linux_configuration=compute.LinuxConfigurationArgs(
                patch_settings=compute.LinuxPatchSettingsArgs(
                    assessment_mode="ImageDefault",
                ),
                provision_vm_agent=True,
            ),
        ),
        resource_group_name=resource_group.name,
        storage_profile=compute.StorageProfileArgs(
            image_reference=compute.ImageReferenceArgs(
                offer="UbuntuServer",
                publisher="Canonical",
                sku="18.04-LTS",
                version="latest",
            ),
            os_disk=compute.OSDiskArgs(
                caching="ReadWrite",
                create_option="FromImage",
                delete_option="Delete",
                managed_disk=compute.ManagedDiskParametersArgs(
                    storage_account_type="Standard_LRS",
                ),
                name=f"{k}osdisk1",
            ),
        ),
        vm_name=k,
    )


### Add two VMs with no public IP and test access
for k, v in VM_DATA_NO_PIP.items():
    nic = network.NetworkInterface(
        f"{k}-nic",
        enable_accelerated_networking=True,
        ip_configurations=[
            network.NetworkInterfaceIPConfigurationArgs(
                name="ipconfig1",
                subnet=network.SubnetArgs(
                    id=subs[v["nic_subnet"]],
                ),
            )
        ],
        location=v["location"],
        network_interface_name=v["nic_name"],
        resource_group_name=resource_group.name,
    )
    virtual_machine = compute.VirtualMachine(
        f"{k} build",
        hardware_profile=compute.HardwareProfileArgs(
            vm_size="Standard_D1_v2",
        ),
        location=v["location"],
        network_profile=compute.NetworkProfileArgs(
            network_interfaces=[
                compute.NetworkInterfaceReferenceArgs(
                    id=nic.id,
                    primary=True,
                )
            ],
        ),
        os_profile=compute.OSProfileArgs(
            admin_password=password,
            admin_username="juliopdx",
            computer_name=k,
            linux_configuration=compute.LinuxConfigurationArgs(
                patch_settings=compute.LinuxPatchSettingsArgs(
                    assessment_mode="ImageDefault",
                ),
                provision_vm_agent=True,
            ),
        ),
        resource_group_name=resource_group.name,
        storage_profile=compute.StorageProfileArgs(
            image_reference=compute.ImageReferenceArgs(
                offer="UbuntuServer",
                publisher="Canonical",
                sku="18.04-LTS",
                version="latest",
            ),
            os_disk=compute.OSDiskArgs(
                caching="ReadWrite",
                create_option="FromImage",
                delete_option="Delete",
                managed_disk=compute.ManagedDiskParametersArgs(
                    storage_account_type="Standard_LRS",
                ),
                name=f"{k}osdisk1",
            ),
        ),
        vm_name=k,
    )
