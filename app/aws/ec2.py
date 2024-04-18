import boto3
import json
import os
from utils.files import save_yaml, read_yaml
from collections import defaultdict


def get_aws_regions(session):
    ec2_client = session.client("ec2")
    response = ec2_client.describe_regions()
    regions = [region["RegionName"] for region in response["Regions"]]
    return regions


def get_aws_regions_full():
    return [
        "US East (N. Virginia)",
        "Europe (Stockholm)",
        "US East (Ohio)",
        "US West (N. California)",
        "US West (Oregon)",
        "Africa (Cape Town)",
        "Asia Pacific (Hong Kong)",
        "Asia Pacific (Mumbai)",
        "Asia Pacific (Osaka-Local)",
        "Asia Pacific (Seoul)",
        "Asia Pacific (Singapore)",
        "Asia Pacific (Sydney)",
        "Asia Pacific (Tokyo)",
        "Canada (Central)",
        "Europe (Frankfurt)",
        "Europe (Ireland)",
        "Europe (London)",
        "Europe (Milan)",
        "Europe (Paris)",
        "Europe (Stockholm)",
        "Middle East (Bahrain)",
        "South America (Sao Paulo)",
    ]


def is_float(element: any) -> bool:
    # If you expect None to be passed:
    if element is None:
        return False
    try:
        float(element)
        return True
    except ValueError:
        return False


def prepare_bandwitch(value):
    v = value.replace("Gigabit", "").replace("Up to", "").replace(" ", "")
    if is_float(v):
        return int(float(v) * 1000000000)
    elif v == "High":
        return 1000000000
    elif v == "Moderate":
        return 351968000
    elif v == "Low":
        return 28398933

    return None


def get_instances(session, region_name, dc_region):
    pricing_client = session.client("pricing")
    tenancy = "Shared"
    os = "Linux"
    preinstalled_software = "NA"
    byol = False

    filters = [
        {"Type": "TERM_MATCH", "Field": "termType", "Value": "OnDemand"},
        {
            "Type": "TERM_MATCH",
            "Field": "capacitystatus",
            "Value": "AllocatedHost" if tenancy == "Host" else "Used",
        },
        {"Type": "TERM_MATCH", "Field": "location", "Value": region_name},
        {"Type": "TERM_MATCH", "Field": "tenancy", "Value": tenancy},
        {"Type": "TERM_MATCH", "Field": "operatingSystem", "Value": os},
        {
            "Type": "TERM_MATCH",
            "Field": "preInstalledSw",
            "Value": preinstalled_software,
        },
        {
            "Type": "TERM_MATCH",
            "Field": "licenseModel",
            "Value": "Bring your own license" if byol else "No License required",
        },
    ]
    responses = pricing_client.get_products(ServiceCode="AmazonEC2", Filters=filters)
    for response in responses["PriceList"]:
        price = json.loads(response)
        ecu = -1
        if is_float(price["product"]["attributes"].get("ecu")):
            ecu = float(price["product"]["attributes"]["ecu"])
            dcc = {}
            dcc["clockSpeed"] = float(
                price["product"]["attributes"].get("clockSpeed", "0").replace(" GHz", "").replace("Up to ", "")
            )
            dcc["vcpu"] = int(price["product"]["attributes"]["vcpu"])
            dcc["memory"] = int(float(price["product"]["attributes"]["memory"].replace(" GiB", "")) * 1024)
            dcc["regionCode"] = price["product"]["attributes"]["regionCode"]
            dcc["ecu"] = ecu
            dcc["flop"] = str(int(ecu * 4.4)) + "e9flops"
            dcc["networkPerformance"] = prepare_bandwitch(price["product"]["attributes"]["networkPerformance"])
            onde = price["terms"]["OnDemand"]

            for on_demand in onde.values():
                for price_dimensions in on_demand["priceDimensions"].values():
                    dcc["pricePerUnit"] = float(price_dimensions["pricePerUnit"]["USD"])

            dcc["price_per_ecu"] = dcc["pricePerUnit"] / ecu
            dc_region_list = dc_region.get(dcc["regionCode"], {})
            dcc["name"] = price["product"]["attributes"]["instanceType"]
            dc_region_list[price["product"]["attributes"]["instanceType"]] = dcc
            dc_region[dcc["regionCode"]] = dc_region_list


def generate_aws_dict(regions, eager):
    if eager or not os.path.isfile("aws_data.yml"):
        session = boto3.Session(
            aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
            region_name=os.environ["AWS_DEFAULT_REGION"],
        )

        if session:
            print(
                "acess data",
                os.environ["AWS_ACCESS_KEY_ID"],
                os.environ["AWS_SECRET_ACCESS_KEY"],
                os.environ["AWS_DEFAULT_REGION"],
            )

        dccv = {}
        for region in regions:
            print(region)
            get_instances(session, region, dccv)

        for region, val in dccv.items():
            sorted_data = sorted(val.items(), key=lambda item: item[1]["pricePerUnit"])
            for new_id, (_, item) in enumerate(sorted_data, start=1):
                item["id"] = new_id
            dccv[region] = dict(sorted_data)

        save_yaml(dccv, "aws_data.yml")

    else:
        dccv = read_yaml("aws_data.yml")

    regions = list(dccv.keys())

    return dccv, regions


def get_data_transfer_prices(session):
    client = session.client("pricing")

    paginator = client.get_paginator("get_products")
    response_iterator = paginator.paginate(
        ServiceCode="AmazonEC2",
        Filters=[
            {
                "Type": "TERM_MATCH",
                "Field": "productFamily",
                "Value": "Data Transfer",
            }
        ],
        PaginationConfig={"MaxItems": 10000},  # Adjust this if you expect more results
    )

    prices = []
    for page in response_iterator:
        for product in page["PriceList"]:
            b = eval(product)
            # Corrected the attribute name to extract the region
            prices.append(
                {
                    "from": b["product"]["attributes"]["fromRegionCode"],
                    "to": b["product"]["attributes"]["toRegionCode"],
                    "price": list(list(b["terms"]["OnDemand"].values())[0]["priceDimensions"].values())[0][
                        "pricePerUnit"
                    ]["USD"],
                }
            )

    return prices


def generate_data_transfer_dict(eager):
    if eager or not os.path.isfile("aws_trasfer.yml"):
        session = boto3.Session(
            aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
            region_name=os.environ["AWS_DEFAULT_REGION"],
        )

        if session:
            print(
                "acess data",
                os.environ["AWS_ACCESS_KEY_ID"],
                os.environ["AWS_SECRET_ACCESS_KEY"],
                os.environ["AWS_DEFAULT_REGION"],
            )

        data_transfer_prices = get_data_transfer_prices(session)
        data = defaultdict(dict)
        for item in data_transfer_prices:
            if item["from"] and item["to"]:
                data[item["from"]][item["from"]] = 0
                data[item["from"]][item["to"]] = float(item["price"])
            # print(f"Region: {item['from']}, Price per GB: ${item['price']}")

        save_yaml(dict(data), "aws_trasfer.yml")

    else:
        data = read_yaml("aws_trasfer.yml")

    return data
