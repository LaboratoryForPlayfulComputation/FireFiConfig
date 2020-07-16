from flask import Flask, render_template, request
import subprocess
import os
import time
from threading import Thread
import fileinput
import requests

# this app is based on the configuration app from RaspiWiFi
# https://github.com/jasbur/RaspiWiFi

# but now it diverges quite significantly

# start our application
app = Flask(__name__)
app.debug = True

# this is the iotwifi docker container that we're talking to
app.wifiserver = 'http://192.168.27.1:8080/'


@app.route('/')
def index():
    print(request.args)
    hotspot_status = requests.get(app.wifiserver + 'status')
    hotspot_json = hotspot_status.json()
    
    connected_wifi = 'not connected'
    if 'ssid' in hotspot_json['payload']:
        connected_wifi = hotspot_json['payload']['ssid']

    # wifi_ap_array = scan_wifi_networks()
    wifi_ap_array = requests.get(app.wifiserver + 'scan')
    wifi_ap_array = [k for k in wifi_ap_array.json()['payload']]

    return render_template('app.html', wifi_ap_array = wifi_ap_array, \
        iotwifi_status = hotspot_json['status'], connected_wifi = connected_wifi, post_to = app.wifiserver + "connect")

@app.route('/manual_ssid_entry')
def manual_ssid_entry():
    return render_template('manual_ssid_entry.html')

@app.route('/connect', methods = ['GET'])
def save_credentials():
    success = request.args.get('success')

    # hotspot_status = requests.get(app.wifiserver + 'status')
    # hotspot_json = hotspot_status.json()
    
    connected_wifi = 'not connected'
    # if 'ssid' in hotspot_json['payload']:
    #     connected_wifi = hotspot_json['payload']['ssid']


    return render_template('save_credentials.html', success = success, ssid = connected_wifi)

######## FUNCTIONS ##########



# def create_wpa_supplicant(ssid, wifi_key):
#     temp_conf_file = open('wpa_supplicant.conf.tmp', 'w')

#     temp_conf_file.write('ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev\n')
#     temp_conf_file.write('update_config=1\n')
#     temp_conf_file.write('\n')
#     temp_conf_file.write('network={\n')
#     temp_conf_file.write('	ssid="' + ssid + '"\n')

#     if wifi_key == '':
#         temp_conf_file.write('	key_mgmt=NONE\n')
#     else:
#         temp_conf_file.write('	psk="' + wifi_key + '"\n')

#     temp_conf_file.write('	}')

#     temp_conf_file.close

#     os.system('mv wpa_supplicant.conf.tmp /etc/wpa_supplicant/wpa_supplicant.conf')

# def set_ap_client_mode():
#     os.system('rm -f /etc/raspiwifi/host_mode')
#     os.system('rm /etc/cron.raspiwifi/aphost_bootstrapper')
#     os.system('cp /usr/lib/raspiwifi/reset_device/static_files/apclient_bootstrapper /etc/cron.raspiwifi/')
#     os.system('chmod +x /etc/cron.raspiwifi/apclient_bootstrapper')
#     os.system('mv /etc/dnsmasq.conf.original /etc/dnsmasq.conf')
#     os.system('mv /etc/dhcpcd.conf.original /etc/dhcpcd.conf')
#     os.system('reboot')


# def config_file_hash():
#     config_file = open('/etc/raspiwifi/raspiwifi.conf')
#     config_hash = {}

#     for line in config_file:
#         line_key = line.split("=")[0]
#         line_value = line.split("=")[1].rstrip()
#         config_hash[line_key] = line_value

#     return config_hash


if __name__ == '__main__':
    # config_hash = config_file_hash()

    # if config_hash['ssl_enabled'] == "1":
    #     app.run(host = '0.0.0.0', port = int(config_hash['server_port']), ssl_context='adhoc')
    # else:
    app.run(host = '0.0.0.0', port = 3001)
