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
from mininet.ns3 import WIFIApStaLink       # line added
import ns.wifi

def emptyNet():
 
    "Create an empty network and add nodes to it."
    "[h1]<---wifi-network-a--->[s3]<---wifi-network-b--->[h2]"
    "   ^                      ^  ^                      ^   "
    "  Sta                    Ap  Ap                    Sta  "

    net = Mininet( controller=OVSController )

    info( '*** Adding controller\n' )
    net.addController( 'c0' )

    info( '*** Adding hosts\n' )
    h1 = net.addHost( 'h1', ip='10.0.0.1' )
    h2 = net.addHost( 'h2', ip='10.0.0.2' )

    info( '*** Adding switch\n' )
    s3 = net.addSwitch( 's3' )
    s3.listenPort = 6634

    WIFIApStaLink( s3, h1, ssid="wifi-network-a", standard = ns.wifi.WIFI_PHY_STANDARD_80211a )  
    #WIFIApStaLink( s3, h1, ssid="wifi-network-a", standard = ns.wifi.WIFI_PHY_STANDARD_80211b )   
    #WIFIApStaLink( s3, h2, ssid="wifi-network-b", standard = ns.wifi.WIFI_PHY_STANDARD_80211a )  
    WIFIApStaLink( s3, h2, ssid="wifi-network-b", standard = ns.wifi.WIFI_PHY_STANDARD_80211b ) 

    info( '*** Starting network\n')
    net.start()
    mininet.ns3.start()                     # line added
 
    info( '*** Testing network connectivity\n' )
    net.pingAll()
 
    h2.cmdPrint( "iperf -s -p 6666 &" )
    h1.cmdPrint( "iperf -c 10.0.0.2 -p 6666" )

    info( '*** Running CLI\n' )
    CLI( net )

    info( '*** Stopping network' )
    mininet.ns3.stop()
    mininet.ns3.clear()                     # line added
    h2.cmdPrint("sudo killall iperf")
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    emptyNet()
