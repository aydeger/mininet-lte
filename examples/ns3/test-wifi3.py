import rlcompleter
import readline

import time

from mininet.net import Mininet
from mininet.node import Node, Switch
from mininet.link import Link, Intf
from mininet.log import setLogLevel, info
from mininet.cli import CLI

import mininet.ns3
from mininet.ns3 import WIFISegment
from mininet.node import OVSController
from mininet.link import TCLink

readline.parse_and_bind("tab: complete")

if __name__ == '__main__':
    setLogLevel( 'info' )

    net = Mininet( controller=OVSController )
    c0 = net.addController( 'c0' )

    info( '*** Adding hosts\n' )
    h1 = net.addHost( 'h1', ip='192.168.0.1' )
    h2 = net.addHost( 'h2', ip='192.168.0.2' )
    h3 = net.addHost( 'h3', ip='192.168.0.3' ) 

    info( '*** Adding switch\n' )
    s0 = net.addSwitch( 's0' )
    s0.listenPort = 6634
    c0.start()
    s0.start( [c0] )
    linkopts=dict( bw=100, delay='1ms', loss=0 )
    TCLink( s0, h3, **linkopts )
	
    #net.hosts.append( s0 )
    net.hosts.append( h1 )
    net.hosts.append( h2 )

    wifi = WIFISegment()

    wifi.addAp( s0 )
    wifi.addSta( h1 )
    wifi.addSta( h2 )

    net.start()
    mininet.ns3.start()

    CLI(net)


