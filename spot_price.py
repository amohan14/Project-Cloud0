import boto3
import json


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
    client = boto3.client('pricing', region_name='us-east-1')
    sp=boto3.client('ec2',region_name=region_code)

    spot_prices=sp.describe_spot_price_history(
        InstanceTypes=[instance_typ], # c4.xlarge
        MaxResults=15,
        ProductDescriptions=['Linux/UNIX (Amazon VPC)']
    )

    sp_dict = {}
    az_list = []
    sp_list = []


    for i in range(len(spot_prices['SpotPriceHistory'])):
        az = spot_prices['SpotPriceHistory'][i]['AvailabilityZone'] # string
        sp = float(spot_prices['SpotPriceHistory'][i]['SpotPrice'])
        az_list.append(az)
        sp_list.append(sp)
        
    for i in range(len(az_list)):
        sp_dict[az_list[i]] = sp_list[i]
    

    # updating the dictionary with the latest entry of each availability zone
    
    for az, sp in sp_dict.items():
        if az not in sp_dict.keys():
            sp_dict[az] = sp

    # finding the cheapest availability zone
    
    minval = min(sp_dict.values())
    
    # to print the first az that satisfy the if condition use another boolean variable
     
    for az, sp in sp_dict.items():
        if sp == minval:
            return [az, sp]

if __name__ == '__main__':
    region_code = 'us-east-1'
    instance_typ = 't2.micro'
    spot = get_spot_price(region_code, instance_typ)
    print(spot[1])