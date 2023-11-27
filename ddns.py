import requests
import json
import os
import subprocess

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
    default_iface = os.popen("ip -6 route | grep default | awk '{print $5}'").read().strip()
    if not default_iface:
        return None  # No default interface found
    ipv6_address = os.popen(f"ip -6 addr show {default_iface} | grep 'mngtmpaddr' | grep -oP '(?<=inet6\s)[\da-f:]+'").read().strip()
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
    records = data['result']
    return records[0]['id'] if records else None

def create_record(zone_id, ipv6_address):
    url = f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records'
    data = {
        'type': 'AAAA',
        'name': RECORD_NAME,
        'content': ipv6_address,
        'ttl': 120
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    return json.loads(response.text)['success']

def update_record(zone_id, record_id, ipv6_address):
    url = f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}'
    data = {
        'type': 'AAAA',
        'name': RECORD_NAME,
        'content': ipv6_address,
        'ttl': 120
    }
    response = requests.put(url, headers=headers, data=json.dumps(data))
    return json.loads(response.text)['success']

ipv6_address = get_ipv6_address()
zone_id = get_zone_id()
record_id = get_record_id(zone_id)

if record_id:
    success = update_record(zone_id, record_id, ipv6_address)
else:
    success = create_record(zone_id, ipv6_address)

if success:
    action = "updated" if record_id else "created"
    print(f'Successfully {action} {RECORD_NAME} with {ipv6_address}')
else:
    print('Failed to update or create record')
