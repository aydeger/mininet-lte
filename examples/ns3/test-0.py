

import rlcompleter
import readline

import mininet.ns3

readline.parse_and_bind("tab: complete")



mininet.ns3.start()
mininet.ns3.stop()
mininet.ns3.clear()
