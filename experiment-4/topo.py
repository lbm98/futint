#!/usr/bin/python

import time

from mininet.node import Controller
from mininet.log import setLogLevel, info
from mn_wifi.node import OVSKernelAP
from mn_wifi.cli import CLI
from mn_wifi.net import Mininet_wifi
from mn_wifi.link import wmediumd
from mn_wifi.wmediumdConnector import interference


NUMBER_OF_OBSERVATIONS = 80
START_X_POSITION = 10 # m
END_X_POSITION = 70 # m
VEHICLE_SPEED = 5 # m/s


start_time = time.time()


def get_rssi(sta):
    cmd = (
        f'iw dev {sta.name}-wlan0 link'
        f' | grep signal'
    )
    output = sta.cmd(cmd)
    try:
        # split on whitespace
        return output.split()[1]
    except:
        return None


def gather_telemetry(sta):
    # wait for wmediumd to startup
    while get_rssi(sta) is None:
        pass

    with open(f'{sta.name}.data', 'w') as fh:
        x_position = START_X_POSITION

        # tbo = time between obervations
        tbo = END_X_POSITION - START_X_POSITION
        tbo /= VEHICLE_SPEED
        tbo /= NUMBER_OF_OBSERVATIONS

        delta_x_position = tbo * VEHICLE_SPEED

        for i in range(NUMBER_OF_OBSERVATIONS):
            delta_time = time.time() - start_time
            rssi = get_rssi(sta)
            if rssi is None:
                rssi = 0
            fh.write(f'{delta_time},{rssi},{x_position}\n')
            time.sleep(tbo)
            sta.setPosition(f"{x_position},150,0")
            x_position += delta_x_position


def topology():
    # net = Mininet_wifi(controller=Controller, accessPoint=OVSKernelAP)
    net = Mininet_wifi(link=wmediumd, wmediumd_mode=interference,
                       noise_th=-91, fading_cof=3)

    info("*** Creating nodes\n")
    sta1 = net.addStation('sta1', position=f'{START_X_POSITION},10,0')
    ap1 = net.addAccessPoint('ap1', ssid='ssid-ap1', mode='g', channel='1',
                             position='15,30,0', range=30)
    ap2 = net.addAccessPoint('ap2', ssid='ssid-ap2', mode='g', channel='6',
                             position='55,30,0', range=30)
    s3 = net.addSwitch('s3')
    h1 = net.addHost('h1')
    c1 = net.addController('c1')

    net.setPropagationModel(model="logDistance", exp=5)

    info("*** Configuring wifi nodes\n")
    net.configureWifiNodes()

    info("*** Creating links\n")
    net.addLink(ap1, s3)
    net.addLink(ap2, s3)
    net.addLink(s3, h1)

    info("*** Starting network\n")
    net.build()
    c1.start()
    ap1.start([c1])
    ap2.start([c1])
    s3.start([c1])

    info("*** Running CLI\n")
    
    while get_rssi(sta1) is None:
        pass

    info(get_rssi(sta1))
    sta1.setPosition(f'11,10,0')
    time.sleep(0.5)
    info(get_rssi(sta1))


    # CLI(net)

    info("*** Stopping network\n")
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    topology()