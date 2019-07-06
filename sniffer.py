#!/usr/bin/python3
#
# A traffic monitor daemon container that uses tshark, the CLI component
# of WireShark to monit traffic that is either tapped or mirrored in transit.
# (Note that this requires specialized hardware and careful placement of
# that hardware within your network. For more details on this, see:
#   https://github.com/MegaMosquito/trafficmon/blob/master//README.md
#
# Note that this monitor may not be completely reliable. My naivete about
# tshark may mean that I have not configured my streaming query very well.
# Also, in my own network setup I am using a managed swutch to mirror all
# ingress and egress traffic to the monitor host. I think it is likely that
# traffic bursts at least could overwhelm the monitor, resulting in it
# missing some of the traffic. This is a potential problem in any setup.
#
# Having said all of that, this is still pretty cool, I think. I discovered
# many surprising things about various kinds of network-capablie devices in
# my home network because of this tool. I never would have had visibility
# into these activities without this tool.
#
# Reference info:
#   I found these pages useful:
#      http://yenolam.com/writings/tshark.pdf
#      https://osqa-ask.wireshark.org/questions/27357/how-to-pipe-tshark-output-in-realtime
#
# Written by Glen Darling (mosquito@darlingevil.com), July 2019.
#



import os



# Configure all of these "MY_" environment variables for your situation

MY_SUBNET_CIDR            = os.environ['MY_SUBNET_CIDR']

MY_COUCHDB_ADDRESS        = os.environ['MY_COUCHDB_ADDRESS']
MY_COUCHDB_PORT           = int(os.environ['MY_COUCHDB_PORT'])
MY_COUCHDB_USER           = os.environ['MY_COUCHDB_USER']
MY_COUCHDB_PASSWORD       = os.environ['MY_COUCHDB_PASSWORD']
MY_COUCHDB_TRAFFIC_DB     = os.environ['MY_COUCHDB_TRAFFIC_DB']
MY_COUCHDB_TIME_FORMAT    = os.environ['MY_COUCHDB_TIME_FORMAT']

MY_MIRROR_INTERFACE       = os.environ['MY_MIRROR_INTERFACE']


import json
import subprocess
from traffic import Traffic
from machine import Machine


# Get the DB class
from db import DB



# Instantiate the db object (i.e., connect to CouchDB, and open our DB)
db = DB( \
  MY_COUCHDB_ADDRESS,
  MY_COUCHDB_PORT,
  MY_COUCHDB_USER,
  MY_COUCHDB_PASSWORD,
  MY_COUCHDB_TRAFFIC_DB,
  MY_COUCHDB_TIME_FORMAT)



SUBNET = MY_SUBNET_CIDR[ : 1 + MY_SUBNET_CIDR.rfind('.')]



# Command to start the infinite stream of data from MY_MIRROR_INTERFACE:
COMMAND = "tshark -l -i " + MY_MIRROR_INTERFACE + " -T json -e 'ip.src' -e 'ip.dst' -e 'eth.addr' -e 'ip.len' -e 'tcp.port' -e 'udp.port' -f 'not broadcast and not multicast and port not 53 and not arp' 2>/dev/null"



# Count of tshark data rcords to consume before pushing data to the DB
PUSH_TO_DB_AFTER = 1000



proc = subprocess.Popen(['sh', '-c', COMMAND],stdout=subprocess.PIPE)
MACHINES = {}
n = 0
buffer = ''
# Discard the first line, which contains only, "[".
discard = proc.stdout.readline()
while True:
  line = proc.stdout.readline()
  if not line:
    break
  line = line.strip().decode('utf-8')
  # print(line)
  if ',' != line:
    buffer += line
  else:
    # print(buffer)
    j = json.loads(buffer)
    buffer = ''

    layers = j['_source']['layers']
    src = ''
    if 'ip.src' in layers: src = layers['ip.src'][0]
    dst = ''
    if 'ip.dst' in layers: dst = layers['ip.dst'][0]
    size_str = '0'
    if 'ip.len' in layers: size_str = layers['ip.len'][0]
    size = int(size_str)
    if '' == src or '' == dst or 0 == size:
      # No src, or no dst, or no length, ignore
      continue
    src_mac = layers['eth.addr'][0]
    dst_mac = layers['eth.addr'][1]
    udp_ports = []
    tcp_ports = []
    if 'udp.port' in layers and None != layers['udp.port']:
      udp_ports = layers['udp.port']
    elif 'tcp.port' in layers and None != layers['tcp.port']:
      tcp_ports = layers['tcp.port']
    else:
      # Not TCP or UDP, ignore
      continue
    traffic = Traffic.new(src, src_mac, dst, dst_mac, udp_ports, tcp_ports, size)
    # Which end(s), src or dst or both, is/are inside the LAN?
    if src.startswith(SUBNET):
      if not (src in MACHINES):
        MACHINES[src] = Machine.new(src, src_mac)
      Machine.add_traffic_out(MACHINES[src], traffic)
    if dst.startswith(SUBNET):
      if not (dst in MACHINES):
        MACHINES[dst] = Machine.new(dst, dst_mac)
      Machine.add_traffic_in(MACHINES[dst], traffic)
    # Periodically push the buffered data to the DB, and reset the buffer
    n += 1
    if n > PUSH_TO_DB_AFTER:
      n = 0
      for ip in sorted(MACHINES.keys(), key=lambda ip: int(ip.split('.')[3])):
        m = MACHINES[ip]
        dbm = db.get(ip)
        if dbm:
          m = Machine.merge(dbm, m)
        db.put(ip, m)
      MACHINES = {}

      

