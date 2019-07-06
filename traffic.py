# A class to represent traffic records (extracted by Wiresharks's tshark

class Traffic(object):

  @staticmethod
  def new (src, src_mac, dst, dst_mac, udp_ports, tcp_ports, size):
    j = {}
    j['src'] = src
    j['src_mac'] = src_mac
    j['dst'] = dst
    j['dst_mac'] = dst_mac
    j['udp_ports'] = udp_ports
    j['tcp_ports'] = tcp_ports
    j['size'] = size
    return j

  @staticmethod
  def merge (t1, t2):
    assert(t1['src'] == t2['src'] and t1['dst'] == t2['dst'])
    # Update mac addresses in case they have changes
    t1['src_mac'] = t2['src_mac']
    t1['dst_mac'] = t2['dst_mac']
    # Append any new ports
    t1['udp_ports'].extend(t2['udp_ports'])
    t1['udp_ports'] = list(set(t1['udp_ports']))
    t1['tcp_ports'].extend(t2['tcp_ports'])
    t1['tcp_ports'] = list(set(t1['tcp_ports']))
    # Add to size
    t1['size'] += t2['size']
    return t1

