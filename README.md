
Build a python wheel like this:
# python3 setup.py bdist_wheel


**To run with Apache on Ubuntu**

# sudo pip install --upgrade --target /var/www/techex.epoxyloaf.com/python --ignore-installed  GetErDone-0.0.1-py3-none-any.whl


Make a place for the app to store "runtime stuff":
# sudo mkdir /var/www/techex.epoxyloaf.com/runtime
# sudo chown www-data /var/www/techex.epoxyloaf.com/runtime


Define the site in Apache:

Edit /etc/apache2/sites-enabled/techex.epoxyloaf.com.conf 


<virtualhost *:80>
    ServerName techex.epoxyloaf.com

    WSGIDaemonProcess GetErDoneSuite user=www-data group=www-data threads=5 home=/var/www/techex.epoxyloaf.com/
    WSGIScriptAlias / /var/www/techex.epoxyloaf.com/GetErDoneSuite.wsgi

    <directory /var/www/techex.epoxyloaf.com>
        WSGIProcessGroup GetErDoneSuite
        WSGIApplicationGroup %{GLOBAL}
        WSGIScriptReloading On
        <Files GetErDoneSuite.wsgi>
            Require all granted
        </Files>
    </directory>
    <directory /var/www/techex.epoxyloaf.com/runtime>
        Require all denied
    </directory>
    <directory /var/www/techex.epoxyloaf.com/python>
        Require all denied
    </directory>

    Alias "/static" "/var/www/techex.epoxyloaf.com/python/GetErDone/server/static"
    <directory /var/www/techex.epoxyloaf.com/python/GetErDone/server/static/>
        Require all granted
    </directory>
</virtualhost>
