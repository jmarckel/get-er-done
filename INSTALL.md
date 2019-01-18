# GetErDone

This is a technical exercise where I am building an application suite using a
mix of technologies to demonstrate the integration of external authentication
and authorization workflows into web based API and site.

Flask, Jinja2, Backbone.js, Auth0, OpenID Connect


## create an auth configuration file

```
{ 
    "SPA": { 
        "algorithms": ["RS256"],
        "auth0_audience": "http://api.your.domain.com",
        "auth0_client_id": "xxxxxxxxx-client-id-here-xxxxxxx",
        "auth0_domain": "your.domain-com.auth0.com",
        "auth0_login_callback_url": "http://spa.your.domain.com/get-er-done",
        "auth0_logout_callback_url": "http://your.domain.com/"
    },
    "WEBAPP": {
        "auth0_login_callback_url": "http://webapp.your.domain.com/callback",
        "auth0_logout_callback_url": "http://your.domain.com/",
        "auth0_client_id": "xxxxxxxxx-client-id-here-xxxxxxx",
        "auth0_client_secret": "xxxxxxxxx-client-secret-here-xxxxxxx",
        "auth0_domain": "your.domain-com.auth0.com",
        "auth0_audience": "http://api.your.domain.com",
        "auth0_profile_key": "profile",
        "auth0_jwt_payload": "jwt_payload"
    }
}
```

It should be located in the runtime directory and called get-er-done-config.json


## To build and run on localhost

First, use git to clone the repo, and cd into the get-er-done directory.

Then ...

```
# build the wheel (to allow pip install to manage deps in a later step)
python3 setup.py bdist_wheel

# build a bdist (because pip install wheel doesn't make the entry point to run locally)
python3 setup.py bdist

# create a place to run locally
mkdir ../install/
cd ../install/

# untar the bdist
tar -zxf ../get-er-done/dist/GetErDone-0.0.1.linux-x86_64.tar.gz

# pip install the wheel (and all the deps) into the bdist tree
pip3 install --upgrade ../get-er-done/dist/GetErDone-0.0.1-py3-none-any.whl  --target=usr/local/lib/python3.5/dist-packages

# create the runtime directory for get-er-done state
mkdir ./usr/local/lib/python3.5/runtime

# copy the get-er-done-config.json file into the runtime directory
cp <wherever you put it>/get-er-done-config.json usr/local/lib/python3.5/runtime

# start the app (which uses Flask to create a localhost http process, serving the app)
PYTHONPATH=./usr/local/lib/python3.5/dist-packages ./usr/local/bin/GetErDone-server

```
If everything was correct, you will see the app start and report it's base url with port number:
```
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```
Browse to that location to see the app!



## **To run with Apache on Ubuntu**

## Build a python wheel like this:

```
python3 setup.py bdist_wheel
```


## Install the wheel on your web server

```
sudo pip install --upgrade --target /var/www/<your site>/python --ignore-installed  GetErDone-0.0.1-py3-none-any.whl
```


## Make a place for the app to store "runtime stuff":
```
sudo mkdir /var/www/<your site>/runtime
sudo chown www-data /var/www/<your site>/runtime
```


## Define the site in Apache:

### create /etc/apache2/sites-enabled/service.<your site>.conf for
### each service - api, spa, and webapp

I defined the following to get things working in Apache2 on Ubuntu

Main site:

```
<virtualhost *:80>
    ServerName your.domain.com
    DocumentRoot "/var/www/your.domain.com/html"
</virtualhost>
```

Site 'api':

```
<virtualhost *:80>
    ServerName api.your.domain.com

    WSGIDaemonProcess GetErDoneSuite-api user=www-data group=www-data threads=5 home=/var/www/your.domain.com/
    WSGIScriptAlias / /var/www/your.domain.com/GetErDoneSuite-api.wsgi

    Alias "/static" "/var/www/your.domain.com/python/GetErDone/server/static"

    <directory /var/www/your.domain.com>
        WSGIPassAuthorization On
        WSGIProcessGroup GetErDoneSuite-api
        WSGIApplicationGroup %{GLOBAL}
        WSGIScriptReloading On
        <Files GetErDoneSuite-api.wsgi>
            Require all granted
        </Files>
    </directory>
    <directory /var/www/your.domain.com/runtime>
        Require all denied
    </directory>
    <directory /var/www/your.domain.com/python>
        Require all denied
    </directory>
    <directory /var/www/your.domain.com/python/GetErDone/server/static/>
        Require all granted
    </directory>
</virtualhost>
```

Site 'spa':

```
<virtualhost *:80>
    ServerName spa.your.domain.com

    WSGIDaemonProcess GetErDoneSuite-spa user=www-data group=www-data threads=5 home=/var/www/your.domain.com/
    WSGIScriptAlias / /var/www/your.domain.com/GetErDoneSuite-spa.wsgi

    Alias "/static" "/var/www/your.domain.com/python/GetErDone/server/static"

    <directory /var/www/your.domain.com>
        WSGIPassAuthorization On
        WSGIProcessGroup GetErDoneSuite-spa
        WSGIApplicationGroup %{GLOBAL}
        WSGIScriptReloading On
        <Files GetErDoneSuite-spa.wsgi>
            Require all granted
        </Files>
    </directory>
    <directory /var/www/your.domain.com/runtime>
        Require all denied
    </directory>
    <directory /var/www/your.domain.com/python>
        Require all denied
    </directory>
    <directory /var/www/your.domain.com/python/GetErDone/server/static/>
        Require all granted
    </directory>
</virtualhost>
```

Site 'webapp':

```
<virtualhost *:80>
    ServerName webapp.your.domain.com

    WSGIDaemonProcess GetErDoneSuite-webapp user=www-data group=www-data threads=5 home=/var/www/your.domain.com/
    WSGIScriptAlias / /var/www/your.domain.com/GetErDoneSuite-webapp.wsgi

    Alias "/static" "/var/www/your.domain.com/python/GetErDone/server/static"

    <directory /var/www/your.domain.com>
        WSGIPassAuthorization On
        WSGIProcessGroup GetErDoneSuite-webapp
        WSGIApplicationGroup %{GLOBAL}
        WSGIScriptReloading On
        <Files GetErDoneSuite-webapp.wsgi>
            Require all granted
        </Files>
    </directory>
    <directory /var/www/your.domain.com/runtime>
        Require all denied
    </directory>
    <directory /var/www/your.domain.com/python>
        Require all denied
    </directory>
    <directory /var/www/your.domain.com/python/GetErDone/server/static/>
        Require all granted
    </directory>
</virtualhost>
```
