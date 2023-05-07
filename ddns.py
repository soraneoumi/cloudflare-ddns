import requests
import json
import re
import os

# Fill with your CF account details 
CF_API_KEY = '0000000000000000000000'
CF_EMAIL = '0000000000000000000000'

# Fill with your domain details
DOMAIN = 'example.com'
RECORD_NAME = 'sub.example.com'

headers = {
    'X-Auth-Email': CF_EMAIL,
    'X-Auth-Key': CF_API_KEY,
    'Content-Type': 'application/json'
}

def get_ipv6_address():
    # Get the public IPv6 address
    ipv6_address = os.popen("ip -6 addr show eth0 | grep -oP '(?<=inet6\s)[\da-f:]+' | grep -v '^fe80' | sed -n 2p").read().strip()
    return ipv6_address

def get_zone_id():
    url = f'https://api.cloudflare.com/client/v4/zones?name={DOMAIN}'
    response = requests.get(url, headers=headers)
    data = json.loads(response.text)
    zone_id = data['result'][0]['id']
    return zone_id

def get_record_id(zone_id):
    url = f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records?name={RECORD_NAME}'
    response = requests.get(url, headers=headers)
    data = json.loads(response.text)
    record_id = data['result'][0]['id']
    return record_id

def update_record(zone_id, record_id, ipv6_address):
    url = f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}'
    data = {
        'type': 'AAAA',
        'name': RECORD_NAME,
        'content': ipv6_address,
        'ttl': 120
    }
    response = requests.put(url, headers=headers, data=json.dumps(data))
    data = json.loads(response.text)
    success = data['success']
    return success

ipv6_address = get_ipv6_address()
zone_id = get_zone_id()
record_id = get_record_id(zone_id)
success = update_record(zone_id, record_id, ipv6_address)

if success:
    print(f'Successfully updated {RECORD_NAME} to {ipv6_address}')
else:
    print('Failed to update record')
