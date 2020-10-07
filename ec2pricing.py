import boto3
import json
import pprint
import csv
from pkg_resources import resource_filename

# Use AWS Pricing API at US-East-1
client = boto3.client('pricing', region_name='us-east-1')

# Search product filter
FLT = '[{{"Field": "tenancy", "Value": "shared", "Type": "TERM_MATCH"}},'\
      '{{"Field": "operatingSystem", "Value": "{o}", "Type": "TERM_MATCH"}},'\
      '{{"Field": "instanceType", "Value": "{i}", "Type": "TERM_MATCH"}},'\
      '{{"Field": "preInstalledSw", "Value": "NA", "Type": "TERM_MATCH"}},'\
      '{{"Field": "location", "Value": "{r}", "Type": "TERM_MATCH"}},'\
      '{{"Field": "capacitystatus", "Value": "Used", "Type": "TERM_MATCH"}}]'

# Get current AWS price for an on-demand instance
def get_ondemand_price(region, os, instancet):
    f = FLT.format(r=region, o=os, i=instancet)
    data = client.get_products(ServiceCode='AmazonEC2', Filters=json.loads(f), MaxResults=100)

    # write header to csv file
    # with open('ondemand.csv', 'w', encoding='utf-8', newline='') as csvfile:
    #         writer = csv.writer(csvfile, delimiter='|')
    #         headers = ['InstanceType', 'OnDemandPrice']
    #         writer.writerow(headers)
    dic = {}
    instance_type_list = []
    od_price_list = []
    for index in range(len(data['PriceList'])):
        on_demand = json.loads(data['PriceList'][index])['terms']['OnDemand']
        # print(on_demand1)
        od1 = list(on_demand)[0]
        od2 = list(on_demand[od1]['priceDimensions'])[0]
        instance_type = on_demand[od1]['priceDimensions'][od2]['description']# On Demand Linux m5d.4xlarge Instance Hour
        instance = instance_type.split()[5] # string
        od_price = float(on_demand[od1]['priceDimensions'][od2]['pricePerUnit']['USD']) # string
        instance_type_list.append(instance)
        od_price_list.append(od_price)

        # with open('ondemand.csv', 'a', encoding='utf-8', newline='') as csvfile:
        #     writer = csv.writer(csvfile, delimiter='|')
        #     writer.writerow(dic.values())
    
    # pinting dictionary with "InstanceType" as key and "od_price" as values
    for index in range(len(instance_type_list)):
        dic[instance_type_list[index]] = od_price_list[index]
    print(region_code, instance_typ, dic[instance_typ])

# Translate region code to region name
def get_region_name(region_code):
    default_region = 'US East (N. Virginia)'
    endpoint_file = resource_filename('botocore', 'data/endpoints.json')
    try:
        with open(endpoint_file, 'r') as f:
            data = json.load(f)
        return data['partitions'][0]['regions'][region_code]['description']
    except IOError:
        return default_region


# Finding the spot price history for availability zones
def get_spot_price(region_code, instance_typ):
    sp=boto3.client('ec2',region_name=region_code)

    spot_prices=sp.describe_spot_price_history(
        InstanceTypes=[instance_typ], # c4.xlarge
        MaxResults=15,
        ProductDescriptions=['Linux/UNIX (Amazon VPC)']
        # AvailabilityZone='us-east-1b'
    )

    sp_dict = {}
    az_list = []
    sp_list = []


    for i in range(len(spot_prices['SpotPriceHistory'])):
        az = spot_prices['SpotPriceHistory'][i]['AvailabilityZone'] # string
        sp = float(spot_prices['SpotPriceHistory'][i]['SpotPrice'])
        az_list.append(az)
        sp_list.append(sp)
        # print(spot_prices['SpotPriceHistory'][x]['SpotPrice'], spot_prices['SpotPriceHistory'][x]['AvailabilityZone'], spot_prices['SpotPriceHistory'][x]['InstanceType'])

    for i in range(len(az_list)):
        sp_dict[az_list[i]] = sp_list[i]
    

    # updating the dictionary with the latest entry of each availability zone
    
    for az, sp in sp_dict.items():
        if az not in sp_dict.keys():
            sp_dict[az] = sp
    
    # finding the cheapest availability zone

    minval = min(sp_dict.values())
    
    # to print the first az that satisfy the if condition use another boolean variable
    
    flag = False 
    for az, sp in sp_dict.items():
        if sp == minval and flag == False:
            print(az, sp)
            flag = True


if __name__ == '__main__':
    
    region_code = 'us-east-1'
    instance_typ = 't2.micro'
    op_sys = 'Linux'

    # Get current on-demand price for a given instance, region and os
    get_ondemand_price(get_region_name(region_code), op_sys, instance_typ)
    # print("on-demand: "+ get_region_name('us-east-1'), price)

    # Get current spot prices for a given instance, region and os 
    get_spot_price(region_code, instance_typ)