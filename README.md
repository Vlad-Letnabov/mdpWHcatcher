# mdp WH catcher
Lounch script on remote server via ssh connect.
Data for it received via get/post request

## For Grafana:
### POST application/json:

<pre><code class="shell">
ist@mdp-master-1:~$ curl -d '{"tags":{"script":"ping.sh"}}' -H "Content-Type: application/json" -X POST  http://mdp-monitor:5000/catchwh/
{"result":0}
</code></pre>

## POST
### Other POST application/x-www-form-urlencoded

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


## Create alert from Grafana:
Create tickets for WH with state='alerting'


### curl POST application/json request for test:

<pre><code class="shell">
ist@mdp-master-1:~$ curl -d '{"title":"[Alerting] Panel Title alert", "message":"Notification Message", "imageUrl":"https://grafana.com/assets/img/blog/mixed_styles.png","tags":{"tag1":"tag 1 value","tag2":"tag 2 value"},"state":"alerting"}' -H "Content-Type: application/json" -X POST  http://localhost:5000/catchwh/
</code></pre>

### Return data

<pre><code class="shell">
> POST /catchwh/ HTTP/1.1
> Host: localhost:5000
> User-Agent: curl/7.68.0
> Accept: */*
> Content-Type: application/json
> Content-Length: 211
> 
* upload completely sent off: 211 out of 211 bytes
* Mark bundle as not supporting multiuse
* HTTP 1.0, assume close after body
< HTTP/1.0 201 CREATED
< Content-Type: application/json
< Content-Length: 0
< Server: Werkzeug/1.0.1 Python/3.8.5
< Date: Tue, 09 Mar 2021 15:08:02 GMT
< 
* Closing connection 0
</code></pre>
