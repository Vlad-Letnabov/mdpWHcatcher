Lounch script on remote server via ssh connect.
Data for it receive via get/post request

For Grafana:
POST application/json:

ist@mdp-master-1:~$ curl -d '{"tags":{"script":"ping.sh"}}' -H "Content-Type: application/json" -X POST  http://mdp-monitor:5000/catchwh/
{"result":0}

Other POST application/x-www-form-urlencoded

ist@mdp-master-1:~$ curl -d "script=ping.sh" -X POST  http://mdp-monitor:5000/catchwh/
{"result":0}

Other GET reuest


ist@mdp-master-1:~$ curl http://mdp-monitor:5000/catchwh/ping.sh
{"result":0}

