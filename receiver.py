#!/usr/bin/env python

# This module runs on camera nodes.
# It will respond to multicast message from a sender node.
# install pysmb to enable connection to server's share
#   pip3 install pysmb
# photo taken will be in /home/pi until instructed to be deleted by cleanup command.
# filename begins with timestamp when the shot was issued.


import socket
import struct
import sys
from typing import Union
from pathlib import Path
from smb.SMBConnection import SMBConnection
import os
import glob
import subprocess

multicast_group = '224.1.1.1'
server_address = ('', 12345)

nodeName: str = socket.gethostname()
print('node: ' + nodeName)

photoName: str = nodeName + '.jpg'
latestPhoto: str = photoName


def upload_photo(server_addr, local_file):
    user_name = 'guest'
    passwd = ''
    c = SMBConnection(user_name, passwd, '', '', use_ntlm_v2=True)
    r = c.connect(server_addr, 445)  # smb Protocol default port 445
    print(' Login successful ')

    file_path = '/home/pi/' + local_file
    local_path = open(file_path, 'rb')
    server_path = 'photo/' + local_file
    try:
        c.storeFile('Share', server_path, local_path)
    except FileNotFoundError as exc:
        print('file not found')
    finally:
        local_path.close()
        print('uploaded')


# Create the socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind to the server address
sock.bind(server_address)

# Tell the operating system to add the socket to the multicast group
# on all interfaces.
group = socket.inet_aton(multicast_group)
mreq = struct.pack('4sL', group, socket.INADDR_ANY)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

try:
    # Receive/respond loop
    while True:
        print('\nwaiting for command')
        data, address = sock.recvfrom(1024)

        print('received ' + str(len(data)) + ' bytes from ' + str(address))
        # print(str(data))
        print(address[0])
        timestamp: str = str(data)[2:14]
        command: str = str(data)[14:len(data) + 2]
        # print(timestamp)
        # print(command)

        if command == 'shoot':
            # take a photo.
            # photo will be timestamped in filename
            print('taking photo...')
            photoName = timestamp + '_' + nodeName + '.jpg'
            filePath = '/home/pi/' + photoName
            latestPhoto = photoName
            reply = 'taken ' + photoName + ' successfully'

            try:
                complete_process = subprocess.run(
                    ['libcamera-still', '-o', filePath, '-n', '--autofocus'], check=True, timeout=20)
            except FileNotFoundError as exc:
                print('libcamera-still not found\n')
                reply = 'libcamera-still not found'
            except subprocess.TimeoutExpired as exc:
                print('process time out\n')
                reply = 'process time out'
            except subprocess.CalledProcessError as exc:
                print('process error')
                print('return code ' + str(exc.returncode) + str(exc))
                reply = 'process error ' + str(exc.returncode)

            sock.sendto(reply.encode(), address)
        elif command == 'stop':
            # stop receiver
            sock.sendto(bytes('receiver stop ' + nodeName, encoding="UTF-8"), address)
            exit()
        elif command == 'shutdown':
            # execute these two lines on each client to enable sudo command without password
            # sudo visudo
            # pi ALL=(ALL) NOPASSWD: /sbin/poweroff, /sbin/reboot, /sbin/shutdown
            sock.sendto(bytes('shutdown ' + nodeName, encoding="UTF-8"), address)
            subprocess.run(['sudo', 'shutdown', '-h', 'now'])
        elif command == 'get':
            # upload the latest photo to server's share folder
            reply = 'photo uploaded ' + latestPhoto
            try:
                upload_photo(address[0], latestPhoto)
            except FileNotFoundError as exc:
                reply = 'file not found' + latestPhoto
            finally:
                sock.sendto(reply.encode(), address)
        elif command == 'getall':
            reply = 'all photo uploaded from ' + nodeName
            file_list = glob.glob('/home/pi/*.jpg')
            for jpg_path in file_list:
                try:
                    upload_photo(address[0], os.path.basename(jpg_path))
                except FileNotFoundError as exc:
                    reply = 'file not found ' + os.path.basename(jpg_path)
                finally:
                    reply = 'uploaded ' + os.path.basename(jpg_path)
                    sock.sendto(reply.encode(), address)
        elif command == 'update':
            # download receiver.py from server's share folder
            username = 'guest'
            password = ''
            conn = SMBConnection(username, password, '', '', use_ntlm_v2=True)
            result = conn.connect(address[0], 445)  # smb Protocol default port 445
            print(' Login successful ')
            localFile = open('/home/pi/receiver.py', 'wb')
            conn.retrieveFile('Share', "receiver.py", localFile)
            localFile.close()
            print('updated')

            reply = 'client updated'
            sock.sendto(reply.encode(), address)
        elif command == 'cleanup':
            # delete jpg files in home folder
            reply = 'photo deleted from ' + nodeName
            file_list = glob.glob('/home/pi/*.jpg')
            for jpg_path in file_list:
                try:
                    os.remove(jpg_path)
                except FileNotFoundError as exc:
                    reply = 'file not found' + jpg_path
                except PermissionError as exc:
                    reply = 'permission error' + jpg_path
            sock.sendto(reply.encode(), address)
        else:
            print('unknown command from', str(address))
            print(command)
            sock.sendto(bytes('unknown ' + nodeName, encoding="UTF-8"), address)

finally:
    print('closing socket')
    sock.close()
