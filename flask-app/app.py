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
app.wifiserver = 'http://localhost:8080/'


@app.route('/')
def index():
    hotspot_status = requests.get(app.wifiserver + 'status')
    hotspot_json = hotspot_status.json()
    print(hotspot_json)
    print(hotspot_json['payload'])

    wifi_ap_array = scan_wifi_networks()
    print(wifi_ap_array)

    return render_template('app.html', wifi_ap_array = wifi_ap_array, iotwifi_status = hotspot_status['status'])


@app.route('/status')
def status():
    wifi_ap_array = scan_wifi_networks()

    return render_template('app.html', wifi_ap_array = wifi_ap_array)

@app.route('/manual_ssid_entry')
def manual_ssid_entry():
    return render_template('manual_ssid_entry.html')


@app.route('/save_credentials', methods = ['GET', 'POST'])
def save_credentials():
    ssid = request.form['ssid']
    wifi_key = request.form['wifi_key']

    # make a curl call to our other server that is in charge of wifi connection
    # curl -w "\n" -d '{"ssid":"Mp", "psk":"12345678"}'      -H "Content-Type: application/json"      -X POST localhost:8080/connect
    data = '{"ssid":' + ssid + ', "psk":' + wifi_key + '}'
    print(data)
    headers = {'Content-type': 'application/json; charset=UTF-8'}
    response = requests.post(app.wifiserver + "connect", data=data, headers=headers)

    # wait for the response. it should not be higher 
    # than keep alive time for TCP connection

    # render template or redirect to some url:
    # return redirect("some_url")

    return render_template('save_credentials.html', ssid = ssid)

######## FUNCTIONS ##########


# def create_dnsmasq():
#     # should go to /etc/dnsmasq.conf
#     create_file = subprocess.Popen(['cp', './configs/dnsmasq.conf', '/etc/dnsmasq.conf'])
#     print(create_file)

#     # then sudo service dnsmasq start
#     start_it = subprocess.Popen(['dnsmasq', 'start'])
#     print(start_it)

# def create_hostapd_conf():

#     # to see what the best channel to use is
#     #iwlist wlan0 channel
#     iwlist = subprocess.Popen(['iwlist', 'wlan0', 'channel'], stdout=subprocess.PIPE)
#     ap_list, err = iwlist.communicate()
#     ap_array = []

#     for line in ap_list.decode('utf-8').rsplit('\n'):
#         print(line)

#     # add DAEMON_CONF="/etc/hostapd/hostapd.conf"
#     # to /etc/default/hostapd

#     # copy hostapdstart to /usr/local/bin/hostapdstart
#     # then chmod 775 /usr/local/bin/hostapdstart



# def test_connections():
#     # command for scanning the networks on on a pi
#     ifconfig = subprocess.Popen(['ifconfig'], stdout=subprocess.PIPE)
#     ap_list, err = ifconfig.communicate()
#     ap_array = []

#     for line in ap_list.decode('utf-8').rsplit('\n'):
#         print(line)
#         # if 'ESSID' in line:
#         #     ap_ssid = line[27:-1]
#         #     if ap_ssid != '':
#         #         ap_array.append(ap_ssid)

    # return ap_array

def scan_wifi_networks():
    # could theoretically also get this by accessing
    # localhost:8080/scan


    # command for scanning the networks on on a pi
    iwlist_raw = subprocess.Popen(['iwlist', 'scan'], stdout=subprocess.PIPE)
    ap_list, err = iwlist_raw.communicate()
    ap_array = []

    for line in ap_list.decode('utf-8').rsplit('\n'):
        if 'ESSID' in line:
            ap_ssid = line[27:-1]
            if ap_ssid != '':
                ap_array.append(ap_ssid)

    return ap_array

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

def update_wpa(wpa_enabled, wpa_key):
    with fileinput.FileInput('/etc/raspiwifi/raspiwifi.conf', inplace=True) as raspiwifi_conf:
        for line in raspiwifi_conf:
            if 'wpa_enabled=' in line:
                line_array = line.split('=')
                line_array[1] = wpa_enabled
                print(line_array[0] + '=' + str(line_array[1]))

            if 'wpa_key=' in line:
                line_array = line.split('=')
                line_array[1] = wpa_key
                print(line_array[0] + '=' + line_array[1])

            if 'wpa_enabled=' not in line and 'wpa_key=' not in line:
                print(line, end='')


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
    app.run(host = '0.0.0.0', port = 80)
