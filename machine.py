# A machine is a single IP address on the LAN, with accumulated traffic data

from traffic import Traffic

class Machine (object):

  @staticmethod
  def new (local_ip, mac):
    j = {}
    j['ip'] = local_ip
    j['mac'] = mac
    j['traffic_in'] = {}
    j['traffic_out'] = {}
    j['count_in'] = 0
    j['count_out'] = 0
    return j

  @staticmethod
  def merge (m1, m2):
    assert(m1['ip'] == m2['ip'])
    # Update MAC, in case it changes
    m1['mac'] = m2['mac']
    # Manually add all the traffic entries
    for i in m2['traffic_in'].keys():
      Machine.add_traffic_in(m1, m2['traffic_in'][i])
    for o in m2['traffic_out'].keys():
      Machine.add_traffic_out(m1, m2['traffic_out'][o])
    # Sum up the counts
    m1['count_in'] += m2['count_in']
    m1['count_out'] += m2['count_out']
    return m1

  @staticmethod
  def add_traffic_in (m, traffic):
    # This traffic is coming in *to* this machine (from traffic['src'])
    assert(m['ip'] == traffic['dst'])
    m['count_in'] += traffic['size']
    if traffic['src'] in m['traffic_in']:
      t = m['traffic_in'][traffic['src']] 
      tt = Traffic.merge(t, traffic)
      m['traffic_in'][traffic['src']] = tt
    else:
      m['traffic_in'][traffic['src']] = traffic

  @staticmethod
  def add_traffic_out (m, traffic):
    # This traffic is coming out *from* this machine (to traffic['dst'])
    assert(m['ip'] == traffic['src'])
    m['count_out'] += traffic['size']
    if traffic['dst'] in m['traffic_out']:
      t = m['traffic_out'][traffic['dst']] 
      tt = Traffic.merge(t, traffic)
      m['traffic_out'][traffic['dst']] = tt
    else:
      m['traffic_out'][traffic['dst']] = traffic

  @staticmethod
  def mosts (m):
    hosts_t = sorted(m['traffic_in'].keys())
    most_t = None
    if 0 != len(hosts_t):
      most_t = hosts_t.pop(0)
      for h in hosts_t:
        t = m['traffic_in'][h]['size']
        if t > m['traffic_in'][most_t]['size']:
          most_t = h
      if 0 == m['traffic_in'][most_t]['size']:
        most_t = None
    hosts_f = sorted(m['traffic_out'].keys())
    most_f = None
    if 0 != len(hosts_f):
      most_f = hosts_f.pop(0)
      for h in hosts_f:
        f = m['traffic_out'][h]['size']
        if f > m['traffic_out'][most_f]['size']:
          most_f = h
      if 0 == m['traffic_out'][most_f]['size']:
        most_f = None
    return(most_t, most_f)

def main ():
  pass

if __name__ == '__main__':
  main();

