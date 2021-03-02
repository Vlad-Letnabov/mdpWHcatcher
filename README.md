# mdp WH catcher
Lounch script on remote server via ssh connect.
Data for it received via get/post request

## For Grafana:
###POST application/json:

<pre><code class="shell">
ist@mdp-master-1:~$ curl -d '{"tags":{"script":"ping.sh"}}' -H "Content-Type: application/json" -X POST  http://mdp-monitor:5000/catchwh/
{"result":0}
</code></pre>
##POST
###Other POST application/x-www-form-urlencoded

<pre><code class="shell">
ist@mdp-master-1:~$ curl -d "script=ping.sh" -X POST  http://mdp-monitor:5000/catchwh/
{"result":0}
</code></pre>
## Get
### Other GET reuest

<pre><code class="shell">
ist@mdp-master-1:~$ curl http://mdp-monitor:5000/catchwh/ping.sh
{"result":0}
</code></pre>
