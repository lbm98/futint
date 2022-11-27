#!/usr/bin/python

import sys
import time

from mininet.log import setLogLevel, info
from mn_wifi.link import wmediumd
from mn_wifi.cli import CLI
from mn_wifi.net import Mininet_wifi
from mn_wifi.wmediumdConnector import interference


NUMBER_OF_OBSERVATIONS = 40
TIME_BETWEEN_OBSERVATIONS = 0.5
DELTA_X_POSITION = 1


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


def gather_telemetry(sta, start_x_position):
    # wait for wmediumd to startup
    while get_rssi(sta) is None:
        pass

    with open(f'{sta.name}.data', 'w') as fh:
        x_position = start_x_position

        for i in range(NUMBER_OF_OBSERVATIONS):
            delta_time = time.time() - start_time
            rssi = get_rssi(sta)
            if rssi is None:
                rssi = 0
            fh.write(f'{delta_time},{rssi}\n')
            time.sleep(TIME_BETWEEN_OBSERVATIONS)
            sta.setPosition(f"{x_position},150,0")
            x_position += DELTA_X_POSITION
            


def topology(args):
    net = Mininet_wifi(link=wmediumd, wmediumd_mode=interference,
                       noise_th=-91, fading_cof=3)

    start_x_position = 151

    info("*** Creating nodes\n")
    ap1 = net.addAccessPoint('ap1', ssid='new-ssid', mode='a', channel='36',
                             position='150,150,0')
    sta1 = net.addStation('sta1', mac='00:00:00:00:00:02', ip='10.0.0.1/8',
                          position=f'{start_x_position},150,0')
    c1 = net.addController('c1')

    info("*** Configuring Propagation Model\n")
    net.setPropagationModel(model="logDistance", exp=4)

    info("*** Configuring nodes\n")
    net.configureWifiNodes()

    info("*** Starting network\n")
    net.build()
    c1.start()
    ap1.start([c1])

    info("*** Gather telemetry\n")
    gather_telemetry(sta1, start_x_position)
    # CLI(net)

    info("*** Stopping network\n")
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    topology(sys.argv)
