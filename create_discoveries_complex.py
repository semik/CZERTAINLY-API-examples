# Python script to create discoveries from FQDNs stored in a file

# importing libraries
import requests
import json
import socket
import time
import re

api_base_url = "https://dev.czertainly.online/api/v1"
connectors_api_url = api_base_url + "/connectors"
discoveries_api_url = api_base_url + "/discoveries"

get_headers = {'Accept': 'application/json'}
post_headers = get_headers 
post_headers['Content-Type'] = 'application/json'

cert_file = "client1.crt"
key_file = "client1-nopw.key"

hosts_file = "./ips_with_reverse_records.txt"

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
batch_list = ""

for hostName in hostFile.readlines():
    hostName = hostName.strip()
    ipAddress = get_ip_address(hostName)
    if ipAddress != "UNKNOWN":
        if re.search(r'^[0-9\.]*$', hostName) is None:
            if re.search(r'vybezek-net', hostName) is None:
                print("Host {}: {}".format(hostName, ipAddress))
                batch_list += hostName + ","
                batch_num += 1
                if batch_num == 10:
                    discovery_name = discovery_prefix + str(discovery_num).zfill(5)
                    discovery_hosts = batch_list[:len(batch_list) - 1]
                    discovery = create_discovery(discovery_name, discovery_hosts, ip_uuid, connector_uuid, port_uuid, allports_uuid)
                    print("UUID of the new discovery for " + discovery_name + " is " + discovery['uuid'] + ".")
                    batch_num = 0
                    batch_list = ""
                    discovery_num += 1
                    time.sleep(60)