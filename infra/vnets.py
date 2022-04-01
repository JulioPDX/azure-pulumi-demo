VNETS = {
    "CoreServicesVnet": {
        "region": "westus",
        "vnet_address": "10.20.0.0/16",
        "subnets": [
            {"name": "GatewaySubnet", "subnet": "10.20.0.0/27"},
            {"name": "SharedServicesSubnet", "subnet": "10.20.10.0/24"},
            {"name": "DatabaseSubnet", "subnet": "10.20.20.0/24"},
            {"name": "PublicWebServiceSubnet", "subnet": "10.20.30.0/24"},
        ],
    },
    "ManufacturingVnet": {
        "region": "northeurope",
        "vnet_address": "10.30.0.0/16",
        "subnets": [
            {"name": "ManufacturingSystemSubnet", "subnet": "10.30.10.0/24"},
            {"name": "SensorSubnet1", "subnet": "10.30.20.0/24"},
            {"name": "SensorSubnet2", "subnet": "10.30.21.0/24"},
            {"name": "SensorSubnet3", "subnet": "10.30.22.0/24"},
        ],
    },
    "ResearchVnet": {
        "region": "westindia",
        "vnet_address": "10.40.0.0/16",
        "subnets": [
            {"name": "ResearchSystemSubnet", "subnet": "10.40.0.0/24"},
        ],
    },
}