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

ipFile = open('/home/moravek/czip.csv')


for ipranges in ipFile.readlines():
    startend = ipranges.split(',')
    iplist = ips(startend[0], startend[1].strip())
    for ipaddr in iplist:
        print( ipaddr + ": " + get_domain_name(ipaddr))