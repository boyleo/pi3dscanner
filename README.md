# Raspi 3d Scanner Control Center

## Server 

A server is hosting Anvil app that serve control interface through standard http protocol\
so you can send command from any device in the same network. \
It can be connected to local network via ethernet or wifi. \
Static IP is optional.\
\
It can be Raspi or a Linux/Windows PC \
I have not tested it on Mac, but Anvil also supports MacOS so it should work. \
\
Server will issue command via multicast message. \
It has time out of 10 seconds to receive responses. \
But it actually does not react to responses, just send and forget for now. \
\
After shooting, camera nodes will **not** automatically send photos back. \
You will need to manually `get` or `getall` photos from each camera nodes.\
This is to minimize waiting time between shots,\
as you don't need to wait for all photos to be sent to the server before taking another.\
\
Photos will stay in each camera nodes until `cleanup` command is issued. \
\
Photos will be found in `smb://server/Share/photo` \
\
For previewing photos, \
a gallery of small thumbnails can be generated manually using Sigal python module. \
Gallery is a local static html page in `smb://server/Share/_build/index.html` <br>
You can open it from file browser, not the web browser, as Anvil does not serve this folder though http \
You may set up Apache and serve this folder to be able to access this gallery from web browser.

## Camera Node

A camera node runs a single `receiver.py` script that waits for multicast command. \
It uses the new `libcamera` to shoot. It should be compatible with wide range of cameras. \
It might work with many USB cameras connected to a single pi with a few lines of code modification. \
\
Camera node does not need static IP, does not need to know the server's IP \
It will respond to message come through multicast group. \
It gets server's IP from the message,  and can send the photo back to that server. \
So you could have many servers in the network, just for redundant.

## Server Installation

Development server is\
Raspi 4B/2G RaspiOS lite bullseye 22.04 \
Server should be connected to the internet for initial setup to go through.
```
sudo apt update
sudo apt upgrade
sudo apt install python3-pip samba
```
edit `/etc/samba/smb.conf` to add Share folder\
assumed `/home/pi/Share`

```
[Share]
  browseable = yes
  path = /home/pi/Share
  guest ok = yes
  writeable = yes
  read only = no
  create mask = 0644
  directory mask = 0755
```
restart samba service
```
sudo systemctl restart smbd.service
```
confirm that you can access samba share on the server `smb://server/Share` \
and guest user have read/write access to this folder. \
\
copy or clone this repository to Share
```
cd /home/pi/Share
git clone https://github.com/boyleo/pi3dscanner.git .
```
then install dependencies \
`pysmb` might not be needed

```
pip install pysmb anvil-app-server anvil-uplink
sudo apt install openjdk-8-jdk
```
***

### Manual start

start anvil server\
first run will take some time as it will download required jar package
```
anvil-app-server --config-file config.yaml &
```
start sender script
```
python sender.py &
```
open `http://server:3030` to access UI

***

### Image Gallery

install sigal to generate preview gallery.\
gallery can be access at `smb://server/Share/_build/index.html` \
you may need `libopenjp2-7` - install with apt
```
pip install sigal
```
to generate/update photo gallery
```
sigal build
```
***

### Configure services
create `/etc/systemd/system/anvil-app.service`
```
[Unit]
Description=Anvil 3D Scanner Control Center
After=network.target
StartLimitIntervalSec=0

[Service]
Type=simple
Restart=always
RestartSec=1
User=pi
ExecStart=/home/pi/.local/bin/anvil-app-server --config-file /home/pi/Share/config.yaml
WorkingDirectory=/home/pi/Share

[Install]
WantedBy=multi-user.target
```
register and start service
```
sudo chmod 644 /etc/systemd/system/anvil-app.service
sudo systemctl enable anvil-app.service
sudo systemctl start anvil-app.service
```
also start `sender.py` as a service \
create `/etc/systemd/system/sender.service` \
use ExecStartPre to probe port 3030 and wait for anvil server to be ready
```
[Unit]
Description=Send multicast command

[Service]
ExecStartPre=/bin/bash -c '(while ! nc -z -v -w1 localhost 3030 2>/dev/null; do echo "Waiting for port 3030 to open..."; sleep 2; done); sleep 2'
User=pi
WorkingDirectory=/home/pi/Share
ExecStart=python /home/pi/Share/sender.py
Restart=always

[Install]
WantedBy=multi-user.target
```
register and start service
```
sudo chmod 644 /etc/systemd/system/sender.service
sudo systemctl enable sender.service
sudo systemctl start sender.service
```
now the sender will automatically start with pi

## Camera Node Installation

Development device is \
Raspi Zero W + ArduCAM IMX519 \
RaspiOS Lite bullseye 22.04 

```
sudo apt update
sudo apt upgrade
sudo apt install python3-pip
pip install pysmb
```
### Install ArduCAM driver

If you have official cameras v1, v2 or HQ you can skip this step\
Otherwise install IMX519 driver and libcamera apps according to this link

https://www.arducam.com/docs/cameras-for-raspberry-pi/raspberry-pi-libcamera-guide/

### Install full version of libcamera

**If you have installed ArduCAM driver from previous step, skip this.** \
\
Default RaspiOS Lite comes with `libcamera-lite` \
If you have official v1, v2, or HQ cameras, upgrade to full version of libcamera \
\
**Do not activate legacy camera from raspi-config** \
\
That is for the obsoleted raspi-still. It will conflicts with libcamera.
```
sudo apt install libcamera libcamera-apps
```
### Receiver script

You may clone this repository into home folder \
but the only needed file is `receiver.py`

```
cd /home/pi
git clone https://github.com/boyleo/pi3dscanner.git .
```

### Set hostname

You need to set hostname of a camera node differently, \
as its name will be included in photo filename to be able to identify where each photo comes from.
```
sudo nano /etc/hostname
```
