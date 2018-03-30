"""
NS-3 integration for Mininet.

"""

import threading, time

from mininet.log import info, error, warn, debug
from mininet.link import Intf, Link
from mininet.node import Switch, Node
from mininet.util import quietRun, moveIntf, errRun

import ns.core
import ns.network
import ns.tap_bridge
import ns.csma
import ns.wifi
import ns.mobility


default_duration = 3600

ns.core.GlobalValue.Bind( "SimulatorImplementationType", ns.core.StringValue( "ns3::RealtimeSimulatorImpl" ) )
ns.core.GlobalValue.Bind( "ChecksumEnabled", ns.core.BooleanValue ( "true" ) )

allTBIntfs = []
allNodes = []

def start():
    global thread
    if 'thread' in globals() and thread.isAlive():
        warn( "NS-3 simulator thread already running." )
        return
    for intf in allTBIntfs:
        if not intf.nsInstalled:
            intf.nsInstall()
    thread = threading.Thread( target = runthread )
    thread.daemon = True
    thread.start()
    for intf in allTBIntfs:
        if not intf.inRightNamespace:
            intf.namespaceMove()
    return

def runthread():
    ns.core.Simulator.Stop( ns.core.Seconds( default_duration ) )
    ns.core.Simulator.Run()

def stop():
    ns.core.Simulator.Stop( ns.core.MilliSeconds( 1 ) )
    while thread.isAlive():
        time.sleep( 0.01 )
    return

def clear():
    ns.core.Simulator.Destroy()
    for intf in allTBIntfs:
        intf.nsInstalled = False
        intf.delete()
    for node in allNodes:
        del node.nsNode
    del allTBIntfs[:]
    del allNodes[:]
    return

def getPosition( node ):
    ''' Return the ns-3 (x, y, z) position of a node.
    '''
    if hasattr( node, 'nsNode' ) and node.nsNode is not None:
        pass
    else:
        node.nsNode = ns.network.Node()
        allNodes.append( node )
    try:
        mm = node.nsNode.GetObject(ns.mobility.MobilityModel.GetTypeId())
        pos = mm.GetPosition()
        return (pos.x, pos.y, pos.z)
    except AttributeError:
        warn("ns-3 mobility model not found\n")
        return (0,0,0)

def setPosition( node, x, y, z ):
    ''' Set the ns-3 (x, y, z) position of a node.
    '''
    if hasattr( node, 'nsNode' ) and node.nsNode is not None:
        pass
    else:
        node.nsNode = ns.network.Node()
        allNodes.append( node )
    try:
        mm = node.nsNode.GetObject(ns.mobility.MobilityModel.GetTypeId())
        if z is None:
            z = 0.0
        pos = mm.SetPosition(ns.core.Vector(x, y, z))
    except AttributeError:
        warn("ns-3 mobility model not found, not setting position\n")


class TBIntf( Intf ):
    def __init__( self, name, node, port=None,
                  nsNode=None, nsDevice=None, mode=None, **params ):
        """
        """
        self.name = name
        self.createTap()
        self.delayedMove = True
        if node.inNamespace:
            self.inRightNamespace = False
        else:
            self.inRightNamespace = True
        Intf.__init__( self, name, node, port , **params)
        allTBIntfs.append( self )
        self.nsNode = nsNode
        self.nsDevice = nsDevice
        self.mode = mode
        self.params = params
        self.nsInstalled = False
        self.tapbridge = ns.tap_bridge.TapBridge()
        if self.nsNode and self.nsDevice and ( self.mode or self.node ):
            self.nsInstall()
        if self.node and self.nsInstalled and self.isInstant(): # instant mode to be implemented in ns-3
            self.namespaceMove()

    def createTap( self ):
        quietRun( 'ip tuntap add ' + self.name + ' mode tap' )

    def nsInstall( self ):
        if not isinstance( self.nsNode, ns.network.Node ):
            warn( "Cannot install TBIntf to ns-3 Node: "
                  "nsNode not specified\n" )
            return
        if not isinstance( self.nsDevice, ns.network.NetDevice ):
            warn( "Cannot install TBIntf to ns-3 Node: "
                  "nsDevice not specified\n" )
            return
        if self.mode is None and self.node is not None:
            if isinstance( self.node, Switch ):
                self.mode = "UseBridge"
            else:
                self.mode = "UseLocal"
        if self.mode is None:
            warn( "Cannot install TBIntf to ns-3 Node: "
                  "cannot determine mode: neither mode nor (mininet) node specified\n" )
            return
        self.tapbridge.SetAttribute ( "Mode", ns.core.StringValue( self.mode ) )
        self.tapbridge.SetAttribute ( "DeviceName", ns.core.StringValue( self.name ) )
        self.tapbridge.SetAttributeFailSafe ( "Instant", ns.core.BooleanValue( True ) ) # to be implemented in ns-3
        self.nsNode.AddDevice( self.tapbridge )
        self.tapbridge.SetBridgedNetDevice( self.nsDevice )
        self.nsInstalled = True

    def namespaceMove( self ):
        loops = 0
        while not self.isConnected():
            time.sleep( 0.01 )
            loops += 1
            if loops > 10:
                warn( "Cannot move TBIntf to mininet Node namespace: "
                      "ns-3 has not connected yet to the TAP interface\n" )
                return
        time.sleep( 0.01 )
        moveIntf( self.name, self.node )
        self.inRightNamespace = True
        # IP address has been reset while moving to namespace, needs to be set again
        if self.ip is not None:
            self.setIP( self.ip, self.prefixLen )
        # The same for 'up'
        self.isUp( True )

    def isConnected( self ):
        return self.tapbridge.IsLinkUp()

    def isInstant( self ):
        return False # to be implemented in ns-3

    def cmd( self, *args, **kwargs ):
        "Run a command in our owning node or in root namespace when not yet inRightNamespace"
        if self.inRightNamespace:
            return self.node.cmd( *args, **kwargs )
        else:
            cmd = ' '.join( [ str( c ) for c in args ] )
            return errRun( cmd )[ 0 ]

    def rename( self, newname ):
        "Rename interface"
        if self.nsInstalled and not self.isConnected():
            self.tapbridge.SetAttribute ( "DeviceName", ns.core.StringValue( newname ) )
        Intf.rename( self, newname )

    def delete( self ):
        "Delete interface"
        if self.nsInstalled:
            warn( "You can not delete once installed ns-3 device, "
                  "run mininet.ns3.clear() to delete all ns-3 devices\n" )
        else:
            Intf.delete( self )


class SimpleSegment( object ):
    def __init__( self ):
        self.channel = ns.network.SimpleChannel()

    def add( self, node, port=None, intfName=None ):
        if hasattr( node, 'nsNode' ) and node.nsNode is not None:
            pass
        else:
            node.nsNode = ns.network.Node()
            allNodes.append( node )
        device = ns.network.SimpleNetDevice()
        device.SetChannel(self.channel)
        node.nsNode.AddDevice(device)
        if port is None:
            port = node.newPort()
        if intfName is None:
            intfName = Link.intfName( node, port ) # classmethod
        tb = TBIntf( intfName, node, port, node.nsNode, device )
        return tb


class SimpleLink( SimpleSegment, Link ):
    def __init__( self, node1, node2, port1=None, port2=None,
                  intfName1=None, intfName2=None ):
        SimpleSegment.__init__( self )
        intf1 = SimpleSegment.add( self, node1, port1, intfName1 )
        intf2 = SimpleSegment.add( self, node2, port2, intfName2 )
        intf1.link = self
        intf2.link = self
        self.intf1, self.intf2 = intf1, intf2


class CSMASegment( object ):
    def __init__( self, DataRate=None, Delay=None ):
        self.channel = ns.csma.CsmaChannel()
        if DataRate is not None:
            self.channel.SetAttribute( "DataRate", ns.network.DataRateValue( ns.network.DataRate( DataRate ) ) )
        if Delay is not None:
            self.channel.SetAttribute( "Delay", ns.core.TimeValue( ns.core.Time( Delay ) ) )

    def add( self, node, port=None, intfName=None ):
        if hasattr( node, 'nsNode' ) and node.nsNode is not None:
            pass
        else:
            node.nsNode = ns.network.Node()
            allNodes.append( node )
        device = ns.csma.CsmaNetDevice()
        queue = ns.network.DropTailQueue()
        device.Attach(self.channel)
        device.SetQueue(queue)
        node.nsNode.AddDevice(device)
        if port is None:
            port = node.newPort()
        if intfName is None:
            intfName = Link.intfName( node, port ) # classmethod
        tb = TBIntf( intfName, node, port, node.nsNode, device )
        return tb


class CSMALink( CSMASegment, Link ):
    def __init__( self, node1, node2, port1=None, port2=None,
                  intfName1=None, intfName2=None, DataRate=None, Delay=None ):
        CSMASegment.__init__( self, DataRate, Delay )
        intf1 = CSMASegment.add( self, node1, port1, intfName1 )
        intf2 = CSMASegment.add( self, node2, port2, intfName2 )
        intf1.link = self
        intf2.link = self
        self.intf1, self.intf2 = intf1, intf2


class WIFISegment( object ):
    def __init__( self, standard = ns.wifi.WIFI_PHY_STANDARD_80211a ):
        # Helpers instantiation
        self.channelhelper = ns.wifi.YansWifiChannelHelper.Default()
        self.phyhelper = ns.wifi.YansWifiPhyHelper.Default()
        self.wifihelper = ns.wifi.WifiHelper.Default()
        self.wifihelper.SetStandard( standard )
        self.machelper = ns.wifi.NqosWifiMacHelper.Default()
        # Setting channel to phyhelper
        self.channel = self.channelhelper.Create()
        self.phyhelper.SetChannel( self.channel )

    def add( self, node, port=None, intfName=None ):
        if hasattr( node, 'nsNode' ) and node.nsNode is not None:
            pass
        else:
            node.nsNode = ns.network.Node()
            allNodes.append( node )
        device = self.wifihelper.Install( self.phyhelper, self.machelper, node.nsNode ).Get( 0 )
        mobilityhelper = ns.mobility.MobilityHelper()
        mobilityhelper.Install( node.nsNode )
        if port is None:
            port = node.newPort()
        if intfName is None:
            intfName = Link.intfName( node, port ) # classmethod
        tb = TBIntf( intfName, node, port, node.nsNode, device )
        return tb

    def addAp( self, node, port=None, intfName=None, ssid="default-ssid" ):
        self.machelper.SetType ("ns3::ApWifiMac", "Ssid", ns.wifi.SsidValue (ns.wifi.Ssid(ssid)),
                                "BeaconGeneration", ns.core.BooleanValue(True),
                                "BeaconInterval", ns.core.TimeValue(ns.core.Seconds(2.5)))
        return self.add( node, port, intfName )

    def addSta( self, node, port=None, intfName=None, ssid="default-ssid" ):
        self.machelper.SetType ("ns3::StaWifiMac", "Ssid", ns.wifi.SsidValue (ns.wifi.Ssid(ssid)))
        return self.add( node, port, intfName )


class WIFIApStaLink( WIFISegment, Link ):
    def __init__( self, node1, node2, port1=None, port2=None,
                  intfName1=None, intfName2=None, ssid="default-ssid", standard = ns.wifi.WIFI_PHY_STANDARD_80211a ):
        WIFISegment.__init__( self, standard )
        intf1 = WIFISegment.addAp( self, node1, port1, intfName1, ssid )
        intf2 = WIFISegment.addSta( self, node2, port2, intfName2, ssid )
        intf1.link = self
        intf2.link = self
        self.intf1, self.intf2 = intf1, intf2


class WIFIBridgeLink( WIFISegment, Link ):
    def __init__( self, node1, node2, port1=None, port2=None,
                  intfName1=None, intfName2=None ):
        WIFISegment.__init__( self, standard = ns.wifi.WIFI_PHY_STANDARD_80211n_5GHZ )
        #
        if hasattr( node1, 'nsNode' ) and node1.nsNode is not None:
            pass
        else:
            node1.nsNode = ns.network.Node()
            allNodes.append( node1 )
        mobilityhelper1 = ns.mobility.MobilityHelper()
        mobilityhelper1.Install( node1.nsNode )
        if port1 is None:
            port1 = node1.newPort()
        if intfName1 is None:
            intfName1 = Link.intfName( node1, port1 ) # classmethod
        tb1 = TBIntf( intfName1, node1, port1, node1.nsNode )
        #
        if hasattr( node2, 'nsNode' ) and node2.nsNode is not None:
            pass
        else:
            node2.nsNode = ns.network.Node()
            allNodes.append( node2 )
        mobilityhelper2 = ns.mobility.MobilityHelper()
        mobilityhelper2.Install( node2.nsNode )
        if port2 is None:
            port2 = node2.newPort()
        if intfName2 is None:
            intfName2 = Link.intfName( node2, port2 ) # classmethod
        tb2 = TBIntf( intfName2, node2, port2, node2.nsNode )
        #
        self.machelper.SetType ("ns3::WDSWifiMac",
                                "ReceiverAddress", ns.network.Mac48AddressValue( ns.network.Mac48Address( tb2.MAC() ) ) )
        device1 = self.wifihelper.Install( self.phyhelper, self.machelper, node1.nsNode ).Get( 0 )
        tb1.nsDevice = device1
        tb1.nsInstall()
        #
        self.machelper.SetType ("ns3::WDSWifiMac",
                                "ReceiverAddress", ns.network.Mac48AddressValue( ns.network.Mac48Address( tb1.MAC() ) ) )
        device2 = self.wifihelper.Install( self.phyhelper, self.machelper, node2.nsNode ).Get( 0 )
        tb2.nsDevice = device2
        tb2.nsInstall()
        #
        tb1.link = self
        tb2.link = self
        self.intf1, self.intf2 = tb1, tb2

