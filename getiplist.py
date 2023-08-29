import sys

def ips(start, end):
    import socket, struct
    start = struct.unpack('>I', socket.inet_aton(start))[0]
    end = struct.unpack('>I', socket.inet_aton(end))[0]
    return [socket.inet_ntoa(struct.pack('>I', i)) for i in range(start, end)]

def get_domain_name(ip_address):
  import socket
  try:
      result=socket.gethostbyaddr(ip_address)
      return list(result)[0]
  except socket.herror:
      return "UNKNOWN"

if len(sys.argv)<2:
    print("Usage:", sys.argv[0], "<file-with-IP-ranges>\n\n" +
          "file should contain comma separated list of IP adreses\n")
    sys.exit(1)

try:
    ipFile = open(sys.argv[1])
except Exception as e:
    print(f"An error occurred: {str(e)}")
    sys.exit(1)

for ipranges in ipFile.readlines():
    startend = ipranges.split(',')
    iplist = ips(startend[0], startend[1].strip())
    for ipaddr in iplist:
        print( ipaddr + ": " + get_domain_name(ipaddr))