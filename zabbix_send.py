import socket
import subprocess
import sys
from datetime import datetime
import time
from random import choice
from syslog import syslog


MESSAGE = """OPTIONS sip:{DST_IP}:{DST_PORT} SIP/2.0
Via: SIP/2.0/UDP {SRC_IP}:{SRC_PORT}
Max-Forwards: 70
From: "sip_ping" <sip:sip_ping@{SRC_IP}>
To: <sip:{DST_IP}:{DST_PORT}>
Contact: <sip:sip_ping@{SRC_IP}:{SRC_PORT}>
Call-ID: sip_ping{randomchar}@{SRC_IP}
CSeq: 1 OPTIONS
User-Agent: SIPPing
Content-Length: 0\r\n"""

SRC_IP = '127.0.0.3'
SRC_PORT = 8899
DST_IP = '213.170.84.105'
DST_PORT = 5060
ZABB_ADDR = '213.170.81.131'
ZABB_HOST = 'sip-main'
ZABB_NAME = 'kamailio.responsemain'


def zabbix_send(data):
    cmd_template = "zabbix_sender -z {ZABB_ADDR} -p 10051 -s {ZABB_HOST} -k {ZABB_NAME} -o {data}"
    cmd = cmd_template.format(ZABB_ADDR=ZABB_ADDR, ZABB_HOST=ZABB_HOST, ZABB_NAME=ZABB_NAME, data=data)
    subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def open_sock():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setblocking(0)
    except Exception, e:
        sys.stderr.write("ERROR: cannot create socket. %s\n" % e)
        sys.exit(-1)
    sock.bind((SRC_IP, SRC_PORT))
    sock.settimeout(0.5)
    return sock


while True:
    startTime = datetime.now()
    try:
        sock = open_sock()
    except Exception, e:
        sys.stderr.write("ERROR: cannot open socket. %s\n" % e)
        sys.exit(-1)

    try:
        try:
            callid = ''.join(choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789") for _ in range(10))
            sock.sendto(MESSAGE.format(DST_IP=DST_IP, DST_PORT=DST_PORT, SRC_IP=SRC_IP, SRC_PORT=SRC_PORT,
                                       randomchar=callid),
                        (DST_IP, DST_PORT))
        except Exception, e:
            sys.stderr.write("ERROR: cannot send packet to %s:%d. %s\n" % (DST_IP, DST_PORT, e))

        buf = sock.recvfrom(0xffff)
        if buf:
            zabbix_send((datetime.now() - startTime).total_seconds())
        sock.close()
        time.sleep(1)
    except socket.timeout:
        zabbix_send('0.5')
        syslog(callid + ' socket timeout (0.5 sec)')
        sock.close()
        time.sleep(1)
