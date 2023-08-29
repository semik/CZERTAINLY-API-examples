# Python script to create discoveries from FQDNs stored in a file

# importing libraries
import requests
import socket
import time
import argparse

parser = argparse.ArgumentParser(description='Create Discoveries in CZERTAINT via API from FQDNs')
parser.add_argument('--czertainly',
                    dest='base',
                    default="https://czertainly.local/",
                    help='URL to where CZERTAINLY is running')
parser.add_argument('--cert',
                    dest='cert',
                    default='admin.crt',
                    help='Certificate of admin for authorize to API. PEM format. Default name admin.crt')
parser.add_argument('--key',
                    dest='key',
                    default='admin.key',
                    help='Private key of admin for authorize to API. PEM format. Default name admin.key')
parser.add_argument('--hosts_file',
                    dest='hosts_file',
                    help='File in format <IPv4>: <hostname>',
                    required=True)
parser.add_argument('--accept-norr',
                    dest='accept_norr',
                    default=False,
                    action='store_true',
                    help='Accept hosts without Reverse Record')
parser.add_argument('--sleep',
                    dest='sleep',
                    default=10,
                    help="Sleep between discovery creation")
args = parser.parse_args()

api_base_url = args.base+"/api/v1"
connectors_api_url = api_base_url + "/connectors"
discoveries_api_url = api_base_url + "/discoveries"

get_headers = {'Accept': 'application/json'}
post_headers = get_headers 
post_headers['Content-Type'] = 'application/json'

cert_file = args.cert
key_file = args.key

hosts_file = args.hosts_file

discovery_provider_name = 'Network-Discovery-Provider'

# Check whether the FQDN has IP address assigned
def get_ip_address(host_name):
  try:
      result=socket.gethostbyname(host_name)
      return result.strip()
  except socket.gaierror:
      return "UNKNOWN"

# Function to get array of connectors 
def get_connectors():
    res = requests.get(connectors_api_url, headers=get_headers, cert=(cert_file, key_file))
    r_json = res.json()
    return(r_json)

# Function to get attributes of connector
def get_connector_attributes(uuid,name,kind):
    res = requests.get(connectors_api_url + "/" + uuid + "/attributes/" + name + "/" + kind, headers=get_headers, cert=(cert_file, key_file))
    r_json = res.json()
    return(r_json)

def create_discovery(discovery_name, hosts, ip_attribute_uuid, connector_uuid, port_attribute_uuid, allports_attribute_uuid):
    # Prepare data for new discovery
    iphostname = { "name": "ip", "content": [ { "data": hosts } ] }
    port = { "name": "port", "content": [ { "data": 443 } ] }
    allports = { "name": "allPorts", "content": [ { "data": False } ] }
    name = discovery_name
    attributes = [ iphostname, port, allports ]
    kind = "IP-Hostname"
    data = {"name": name, "attributes": attributes, "connectorUuid": connector_uuid, "kind": kind}    

    # Send POST request
    res = requests.post(discoveries_api_url, headers=post_headers, cert=(cert_file, key_file), json = data)

    # read and return response
    r_json = res.json()
    
    return(r_json)

#### Main

## Go through the array of discoveries and get uuid and kind of Network-Discovery-Provider.
connectors = get_connectors()
for connector in connectors:
    if connector['name'] == discovery_provider_name:
        connector_uuid = connector['uuid']
        function_group = "discoveryProvider"
        function_group_kind = "IP-Hostname"        
        attributes = get_connector_attributes(connector_uuid,function_group,function_group_kind)
        for attribute in attributes:
            if attribute['name'] == 'ip': ip_uuid = attribute['uuid']
            if attribute['name'] == 'port': port_uuid = attribute['uuid']
            if attribute['name'] == 'allPorts': allports_uuid = attribute['uuid']

hostFile = open(hosts_file)

discovery_num = 1
discovery_prefix = "cznet-"
batch_num = 0
batch_array = [[]]

for line in hostFile.readlines():
    hostip = line.rstrip().split(':')
    hostName = hostip[1].strip()
    ipAddress = hostip[0].strip()
    if (hostName != "UNKNOWN") or args.accept_norr:
        if (hostName == "UNKNOWN"):
            batch_array[batch_num].append(ipAddress)
        else:
            batch_array[batch_num].append(hostName)

        if len(batch_array[batch_num]) >= 10:
            batch_num += 1
            batch_array.append([])

for batch in batch_array:
    if len(batch) == 0:
        break

    discovery_hosts = ', '
    discovery_hosts = discovery_hosts.join(batch)
    discovery_name = discovery_prefix + str(time.time())
    print(discovery_name, discovery_hosts)

    discovery = create_discovery(discovery_name, discovery_hosts, ip_uuid, connector_uuid, port_uuid, allports_uuid)
    print("UUID of the new discovery for " + discovery_name + " is " + discovery['uuid'] + ".")

    time.sleep(args.sleep)