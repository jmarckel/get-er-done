# GetErDone

Work in progress here...

This is a technical exercise where I am building an application suite using a
mix of technologies to demonstrate the integration of external authentication
and authorization workflows into web based API and site.

Flask, Jinja2, Backbone.js, Auth0, OpenID Connect


## create an auth configuration file

```
{
    "SPA": {
        "auth0_domain": "techex-epoxyloaf-com.auth0.com",
        "auth0_audience": "",
        "algorithms": ["RS256"]
    },
    "WEBAPP": {
        "auth0_callback_url": "",
        "auth0_client_id": "",
        "auth0_client_secret": "",
        "auth0_domain": "",
        "auth0_audience": ""
    }
}
```

It should be located in the runtime directory and called get-er-done-config.json


## To build and run on localhost

```
python3 ./setup.py bdist
cd ..
mkdir install-test
cd install-test
tar -zxf ../get-er-done/dist/GetErDone-0.0.1.linux-x86_64.tar.gz

# need to figure out a better way for config of runtime path, but this worked...
mkdir ./usr/local/lib/python3.5/runtime

PYTHONPATH=./usr/local/lib/python3.5/dist-packages/ ./usr/local/bin/GetErDone-server 
```



## Build a python wheel like this:

```
python3 setup.py bdist_wheel
```


## **To run with Apache on Ubuntu**

```
sudo pip install --upgrade --target /var/www/<your site>/python --ignore-installed  GetErDone-0.0.1-py3-none-any.whl
```


## Make a place for the app to store "runtime stuff":
```
sudo mkdir /var/www/<your site>/runtime
sudo chown www-data /var/www/<your site>/runtime
```


## Define the site in Apache:

### Edit /etc/apache2/sites-enabled/<your site>.conf 

I defined the following to get things working in Apache2 on Ubuntu

```
<virtualhost *:80>
    ServerName <your site>

    WSGIDaemonProcess GetErDoneSuite user=www-data group=www-data threads=5 home=/var/www/<your site>/
    WSGIScriptAlias / /var/www/<your site>/GetErDoneSuite.wsgi

    <directory /var/www/<your site>>
        WSGIProcessGroup GetErDoneSuite
        WSGIApplicationGroup %{GLOBAL}
        WSGIScriptReloading On
        <Files GetErDoneSuite.wsgi>
            Require all granted
        </Files>
    </directory>
    <directory /var/www/<your site>/runtime>
        Require all denied
    </directory>
    <directory /var/www/<your site>/python>
        Require all denied
    </directory>

    Alias "/static" "/var/www/<your site>/python/GetErDone/server/static"
    <directory /var/www/<your site>/python/GetErDone/server/static/>
        Require all granted
    </directory>
</virtualhost>
```
