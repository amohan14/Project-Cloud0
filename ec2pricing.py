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
    
    # Printing dictionary with "InstanceType" as key and "od_price" as values
    for index in range(len(instance_type_list)):
        dic[instance_type_list[index]] = od_price_list[index]
    return region_code, instance_typ, dic[instance_typ]

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


# Fetchiing ImageId
def imageID():
    client=boto3.client('ec2', region_name=region_code)
    image=client.describe_images(
        Filters=[
            {'Name': 'owner-id','Values': ['137112412989']}, 
            {'Name': 'description','Values': ['Amazon Linux 2 AMI 2.0.20200917.0 x86_64 HVM gp2']} 
        ]
    )
    image_id= (image['Images'][0]['ImageId'])
    return image_id

# Fetching the keyPair
def KeyPairName():
    client=boto3.client('ec2',region_name=region_code)
    keypairs = client.describe_key_pairs()
    KeyName= keypairs['KeyPairs'][1]['KeyName']
    return KeyName

# Fetching Security Group Id
def securityGroup():
    client=boto3.client('ec2',region_name=region_code)
    sg = client.describe_security_groups(
        Filters= [{ 'Name':'group-name', 'Values' : ['ansible-node']}]
    )
    sgID = sg['SecurityGroups'][0]['GroupId']
    return sgID

# Requesting ec2 spot instance for cheapest Availability Zone
def request_spot_instance(spot,image_id, key_name, instance_typ, sgID):
    ec2_client = boto3.client('ec2',region_name=region_code)
    response = ec2_client.request_spot_instances(
        SpotPrice = str(spot[1]),
        # ClientToken='string1',
        InstanceCount=1,
        Type='one-time',
        LaunchSpecification = {
            'ImageId': image_id,
            'KeyName': key_name,
            'InstanceType':instance_typ,
            'Placement':{
                'AvailabilityZone': spot[0],
            },
            'SecurityGroupIds':[
                sgID
            ]
        }
    )
    return response


# Function to print out the outputs
def outputs(region_code, instance_typ, op_sys):
    # Get current on-demand price for a given instance, region and os
    on_demand = get_ondemand_price(get_region_name(region_code), op_sys, instance_typ)
    print(list(on_demand))
    # Get current spot prices for a given instance, region and os 
    spot = get_spot_price(region_code, instance_typ)
    image_id = imageID()
    key_name = KeyPairName()
    sgID = securityGroup()
    spot_request= request_spot_instance(spot,image_id, key_name, instance_typ, sgID)

if __name__ == '__main__':
    region_code = 'us-east-1'
    instance_typ = 't2.micro'
    op_sys = 'Linux'
    outputs(region_code, instance_typ, op_sys)


    
    
    

















# print(spot_prices['SpotPriceHistory'][x]['SpotPrice'], spot_prices['SpotPriceHistory'][x]['AvailabilityZone'], spot_prices['SpotPriceHistory'][x]['InstanceType'])

# printing values to csv files
# def csv_printer(od_val, sp_val):
#     # write header to csv file
#     with open('ec2pricing.csv', 'w', encoding='utf-8', newline='') as csvfile:
#             writer = csv.writer(csvfile, delimiter='|')
#             headers = ['Region', 'InstanceType', 'OnDemandPrice', 'SpotPrice AZ 1', 'SpotPrice AZ 2', 'SpotPrice AZ 3', 'SpotPrice AZ 4', 'SpotPrice AZ 5','SpotPrice AZ 6', 'lowest price AZ']
#             writer.writerow(headers)
#     with open('ec2pricing.csv', 'a', encoding='utf-8', newline='') as csvfile:
#             writer = csv.writer(csvfile, delimiter='|')
#             price_list = 
#             writer.writerow(od_val.append(sp_val))
# pricer_dict(on_demand)
# Printing to csv
# csv_printer(on_demand, spot)

