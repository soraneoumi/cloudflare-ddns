import requests
import json
import os
import subprocess

# Fill with your CF account details 
CF_API_TOKEN = '0000000000000000000000'

# Fill with your domain details
DOMAIN = 'example.com'
RECORD_NAME = 'sub.example.com'

headers = {
    'Authorization': 'Bearer ' + CF_API_TOKEN,
    'Content-Type': 'application/json'
}

def get_ipv4_address():
    # Get the public IPv4 address
    try:
        result = subprocess.run(['curl', 'inet-ip.info'], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        print("Failed to get IPv4 address")
        return None

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

def get_record_id(zone_id, record_type):
    url = f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records?type={record_type}&name={RECORD_NAME}'
    response = requests.get(url, headers=headers)
    data = json.loads(response.text)
    records = data['result']
    return records[0]['id'] if records else None

def create_record(zone_id, ip_address, record_type):
    url = f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records'
    data = {
        'type': record_type,
        'name': RECORD_NAME,
        'content': ip_address,
        'ttl': 120
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    return json.loads(response.text)['success']

def update_record(zone_id, record_id, ip_address, record_type):
    url = f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}'
    data = {
        'type': record_type,
        'name': RECORD_NAME,
        'content': ip_address,
        'ttl': 120
    }
    response = requests.put(url, headers=headers, data=json.dumps(data))
    return json.loads(response.text)['success']

def update_dns(ip_address, record_type):
    zone_id = get_zone_id()
    record_id = get_record_id(zone_id, record_type)

    if record_id:
        success = update_record(zone_id, record_id, ip_address, record_type)
    else:
        success = create_record(zone_id, ip_address, record_type)

    if success:
        action = "updated" if record_id else "created"
        print(f'Successfully {action} {RECORD_NAME} ({record_type}) with {ip_address}')
    else:
        print(f'Failed to update or create {record_type} record')

# Update IPv4
ipv4_address = get_ipv4_address()
if ipv4_address:
    update_dns(ipv4_address, 'A')
else:
    print("Failed to update IPv4 record: No IPv4 address obtained")

# Update IPv6
ipv6_address = get_ipv6_address()
if ipv6_address:
    update_dns(ipv6_address, 'AAAA')
else:
    print("Failed to update IPv6 record: No IPv6 address obtained")
