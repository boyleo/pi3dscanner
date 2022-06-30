# raspi 3d scanner control center
# server installation on raspbery pi
# raspi 4B/2G OS lite bullseye 22.04

sudo apt update
sudo apt upgrade
sudo apt install python3-pip samba

# edit /etc/samba/smb.conf
# to add Share folder , assumed /home/pi/Share
 
[Share]
  browseable = yes
  path = /home/pi/Share
  guest ok = yes
  writeable = yes
  read only = no
  create mask = 0644
  directory mask = 0755

# restart samba service
sudo systemctl restart smbd.service

# copy project files to Share

cd /home/pi/Share

# install dependecies
# * pysmb might not be needed
pip install pysmb anvil-app-server anvil-uplink
sudo apt install openjdk-8-jdk

# start anvil server
# first run will download required jar package
anvil-app-server --config-file config.yaml &

# start sender script
python sender.py &

# open http://server:3030 to access UI

# ---

# install sigal to generate preview gallery
# gallery can be access at Share/_build/index.html
# you may need libopenjp2-7 - install with apt
pip install sigal

# generate/update photo gallery
sigal build

# ---

# config anvil app server to start as a service
# create /etc/systemd/system/anvil-app.service

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

# register and start service
sudo chmod 644 /etc/systemd/system/anvil-app.service
sudo systemctl enable anvil-app.service
sudo systemctl start anvil-app.service

# also start sender.py as a service
# create /etc/systemd/system/sender.service

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

# register and start service
sudo chmod 644 /etc/systemd/system/sender.service
sudo systemctl enable sender.service
sudo systemctl start sender.service

# now the sender will automatically start with pi
