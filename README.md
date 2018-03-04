
running locally:

# "install it"
PYTHONPATH=/home/jmarckel/work/github/python3-jblob/install/lib/python3.5/site-packages pip install -e . --prefix=/home/jmarckel/work/github/python3-jblob/install

# run it:
PYTHONPATH=/home/jmarckel/work/github/python3-jblob/install/lib/python3.5/site-packages ./install/bin/jblob_server


# python3 setup.py bdist_wheel

# sudo pip install --upgrade --target /var/www/techex.epoxyloaf.com/python --ignore-installed  GetErDone-0.0.1-py3-none-any.whl

sudo mkdir /var/www/techex.epoxyloaf.com/runtime
sudo chown www-data /var/www/techex.epoxyloaf.com/runtime


