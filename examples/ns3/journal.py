#!/usr/bin/python

"""
This example shows how to create an empty Mininet object
(without a topology object) and add nodes to it manually.
"""

from mininet.net import Mininet
from mininet.node import OVSSwitch, Controller, RemoteController
from mininet.link import Link
from mininet.cli import CLI
from mininet.log import setLogLevel, info

import mininet.ns3
from mininet.ns3 import WIFIBridgeLink


def tunnelX11( node, display=None):
    """Create an X11 tunnel from node:6000 to the root host
       display: display on root host (optional)
       returns: node $DISPLAY, Popen object for tunnel"""
    if display is None:
        display = environ[ 'DISPLAY' ]
    host, screen = display.split( ':' )
    # Unix sockets should work
    if not host or host == 'unix':
        # GDM3 doesn't put credentials in .Xauthority,
        # so allow root to just connect
        quietRun( 'xhost +si:localuser:root' )
        return display, None
    else:
        # Create a tunnel for the TCP connection
        port = 6000 + int( float( screen ) )
        connection = r'TCP\:%s\:%s' % ( host, port )
        cmd = [ "socat", "TCP-LISTEN:%d,fork,reuseaddr" % port,
               "EXEC:'mnexec -a 1 socat STDIO %s'" % connection ]
    return 'localhost:' + screen, node.popen( cmd )

def makeTerm( node, fileName, nodeIP, nodePort, title='Node', term='xterm', display=None ):
    """Create an X11 tunnel to the node and start up a terminal.
       node: Node object
       title: base title
       term: 'xterm' or 'gterm'
       returns: two Popen objects, tunnel and terminal"""
    title += ': ' + node.name
    if not node.inNamespace:
        title += ' (root)'
    cmds = {
        'xterm': [ 'xterm', '-title', title, '-display' ],
        'gterm': [ 'gnome-terminal', '--title', title, '--display' ]
    }
    if term not in cmds:
        error( 'invalid terminal type: %s' % term )
        return
    display, tunnel = tunnelX11( node, display )
    term = node.popen( cmds[ term ] + [ display, '-e', 'python', fileName, nodeIP, nodePort] )
    return term


def linkStatusChange(switch1, switch2, newStatus, net, h1):
    net.configLinkStatus(switch1, switch2, newStatus)   

def startServer():
    os.system('./init.sh')
    #global h1term
    h1term = makeTerm( h1, 'server.py', '10.0.0.1', '1111', 'host1')

def startClient():
    #global h4term
    h4term = makeTerm( h4, 'client.py', '10.0.0.1', '1111', 'host4')

def stopMininet(): 
    global net                                                                                                         
    net.stop() 

def emptyNet():

    "Create an empty network and add nodes to it."
    "[h1]<---network-a--->[s3]<--wifi-bridge-->[s4]<---network-b--->[h2]"

    net = Mininet( )
    c2 = net.addController(name='FloodLight', controller=RemoteController, ip='10.102.206.207', port=6653)

    info( '*** Adding controllers\n' )
    net.addController( 'c0' )
    net.addController( 'c1' )

    info( '*** Adding hosts\n' )
    h1 = net.addHost( 'h1', ip='10.0.0.1' )
    h2 = net.addHost( 'h2', ip='10.0.0.2' )
    h3 = net.addHost( 'h3', ip='10.0.0.3' )
    h4 = net.addHost( 'h4', ip='10.0.0.4' )

    info( '*** Adding switches\n' )
    s1 = net.addSwitch( 's1' )
    s2 = net.addSwitch( 's2' )
    s3 = net.addSwitch( 's3' )
    s4 = net.addSwitch( 's4' )

    info( '*** Creating links\n' )
    Link( s1, h1 )
    Link( s2, h2 )
    Link( s3, h3 )
    Link( s4, h4 )
    Link( s1, s2 )
    Link( s1, s3 )
    Link( s2, s4 )
    Link( s3, s4 )
    WIFIBridgeLink( s3, s4 )

    info( '*** Starting network\n')
    net.start()
    mininet.ns3.start()

    info( '*** Running CLI\n' )
    CLI( net )

    info( '*** Stopping network' )
    mininet.ns3.stop()
    mininet.ns3.clear()
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    emptyNet()
