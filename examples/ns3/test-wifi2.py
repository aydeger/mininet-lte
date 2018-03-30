#!/usr/bin/python

"""
This example shows how to create an empty Mininet object
(without a topology object) and add nodes to it manually.
"""

from mininet.net import Mininet
from mininet.node import OVSController
from mininet.cli import CLI
from mininet.log import setLogLevel, info

import mininet.ns3                          # line added
from mininet.ns3 import WIFISegment
from mininet.link import TCLink
import ns.wifi

def emptyNet():
 
    "Create an empty network and add nodes to it."
    "[h1]<---wifi-network---> [h0:AP] <---wired-link ---> [s0] <---wired-link--->[h3]"
    "[h2]<---wifi-network--->         "

    net = Mininet( controller=OVSController )

    info( '*** Adding controller\n' )
    net.addController( 'c0' )

    info( '*** Adding switch\n' )
    s0 = net.addSwitch( 's0' )
    s0.listenPort = 6634

    h0 = net.addHost( 'h0' ) 
    h1 = net.addHost( 'h1', ip='192.168.0.2' ) 
    h2 = net.addHost( 'h2', ip='192.168.0.3' ) 
    h3 = net.addHost( 'h3', ip='10.0.0.2' ) 
    linkopts=dict( bw=100, delay='1ms', loss=0 )
    TCLink( s0, h3, **linkopts )
    TCLink( h0, s0, **linkopts )
    
    wifi = WIFISegment()

    wifi.addAp( h0 )
    wifi.addSta( h1 )
    wifi.addSta( h2 )

    info( '*** Starting network\n')
    net.start()
    mininet.ns3.start()                

    h0.cmdPrint ( "ifconfig h0-eth0 10.0.0.1 netmask 255.255.255.0" )
    h0.cmdPrint ( "ifconfig h0-eth1 192.168.0.1 netmask 255.255.255.0" )
    h0.cmdPrint ( "sudo echo 1 > /proc/sys/net/ipv4/ip_forward" )
    h1.cmdPrint ( "route add default gw 192.168.0.1" )
    h2.cmdPrint ( "route add default gw 192.168.0.1" )
    h3.cmdPrint ( "route add default gw 10.0.0.1" )
 
    info( '*** Testing network connectivity\n' )
    net.pingAll()

    info( '*** Running CLI\n' )
    CLI( net )

    info( '*** Stopping network' )
    mininet.ns3.stop()
    mininet.ns3.clear()                     # line added
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    emptyNet()
