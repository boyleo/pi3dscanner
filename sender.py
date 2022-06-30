#!/usr/bin/env python

# This module sends command to receiver nodes
# available command:
#   shoot - take a photo
#   get - tell clients to upload the latest photo to server's share
#           create smb folder called Share/photo/ beforehand
#   update - copy new receiver.py from server's share to client
#   cleanup - delete photo remains on each client
#   exit - close receiver
import anvil.server
import socket
import struct
from datetime import datetime
import sys
import subprocess


@anvil.server.callable
def send_command(command):
    # handle commands on server side
    if command == "exit":
        return 0
    elif command == 'gallery':
        subprocess.run(['sigal', 'build'])

    # command = input('type message : ')
    multicast_group = ('224.1.1.1', 12345)

    # Create the datagram socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Set a timeout so the socket does not block indefinitely when trying
    # to receive data.
    sock.settimeout(10)

    # Set the time-to-live for messages to 1, so they do not go past the
    # local network segment.
    ttl = struct.pack('b', 1)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

    # Send data to the multicast group
    # timestamp the command for easy photo grouping
    now = datetime.now()
    msg = now.strftime('%y%m%d%H%M%S') + command
    print('sending ' + msg)
    try:
        sent = sock.sendto(msg.encode(), multicast_group)

        # Look for responses from all recipients
        while True:
            print('waiting to receive')
            try:
                data, server = sock.recvfrom(64)
            except socket.timeout:
                print('timed out, no more responses')
                break
            else:
                print('received ' + str(data) + str(server))
    finally:
        print('closing socket')
        sock.close()


anvil.server.connect("server_K5SNTEYEVJEPMS54JP47G33A-LKVFOIIUYW7JW2GE", url="ws://localhost:3030/_/uplink")
anvil.server.wait_forever()
