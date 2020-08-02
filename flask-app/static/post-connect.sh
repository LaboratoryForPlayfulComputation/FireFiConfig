SSID=$1
PSK=$2
echo SSID
echo PSK
curl -w "\n" -d '{"ssid":"$SSID", "psk":"$PSK"}' -H "Content-Type: application/json" -X POST http://192.168.27.1:8080/connect