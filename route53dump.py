#!/usr/bin/env python3
import boto3 
import csv
from netaddr import IPAddress

csvfile="route53_aRecords_publicIP.csv"

# truncate the file
def truncate():
    with open(csvfile, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Record', 'IP'])

def zonedump():
    truncate()
    prod = boto3.session.Session(profile_name='prod')
    client = prod.client('route53')
    zone_response = client.list_hosted_zones()
    
    for zone in zone_response['HostedZones']:
        zoneid = zone['Id']
        # print(f'Running against zone: {zoneid}')
        paginator = client.get_paginator('list_resource_record_sets')

        try:
            source_zone_records = paginator.paginate(HostedZoneId=zoneid)
            for record_set in source_zone_records:
                    for resource in record_set['ResourceRecordSets']:
                        if 'ResourceRecords' in resource:
                            if resource['Type'] == 'A':
                                name=resource['Name']
                                records = resource['ResourceRecords'][0]
                                value = records['Value']
                                # print(f'{resource}')
                                if IPAddress(value).is_private() is False:
                                    with open(csvfile, 'a', newline='') as file:
                                        writer = csv.writer(file)
                                        writer.writerow([name, value])
                                    print(f'{name},{value}')
        except Exception as error:
            print('An error occurred getting source zone records:')
            print(str(error))
            raise

if __name__ == '__main__':
    zonedump()
