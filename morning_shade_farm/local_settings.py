import netifaces as ni
from morning_shade_farm.settings import *

DEBUG=True

# Add our local IP address to the allowed hosts so that the server replies to requests at my
# laptop's IP and we can hit the web UI from other devices (ex. cell phones), and not just from
# this Mac at 127.0.0.1
ni.ifaddresses('en0')
ip = ni.ifaddresses('en0')[ni.AF_INET][0]['addr']
ALLOWED_HOSTS.append(ip)
