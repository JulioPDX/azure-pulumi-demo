VM_DATA = {
    "testvm1": {
        "nic_name": "testvm1-nic",
        "nic_vnet": "CoreServicesVnet",
        "nic_subnet": "DatabaseSubnet",
        "location": "westus",
    },
    "testvm2": {
        "nic_name": "testvm2-nic",
        "nic_vnet": "CoreServicesVnet",
        "nic_subnet": "DatabaseSubnet",
        "location": "westus",
    },
    "testvm3": {
        "nic_name": "testvm3-nic",
        "nic_vnet": "ResearchVnet",
        "nic_subnet": "ResearchSystemSubnet",
        "location": "westindia",
    },
}

VM_DATA_NO_PIP = {
    "testvm4": {
        "nic_name": "testvm4-nic",
        "nic_vnet": "ManufacturingVnet",
        "nic_subnet": "ManufacturingSystemSubnet",
        "location": "northeurope",
    },
    "testvm5": {
        "nic_name": "testvm5-nic",
        "nic_vnet": "",
        "nic_subnet": "ManufacturingSystemSubnet",
        "location": "northeurope",
    },
}