
=========
GetErDone
=========

**GetErDone** is a technical exercise designed to demonstrate use cases
for authorization and authentication workflows of network based applications
using `OAuth2`_ and `OpenID_Connect`_. 

.. _OAuth2: https://en.wikipedia.org/wiki/OAuth
.. _OpenID_Connect: https://en.wikipedia.org/wiki/OpenID_Connect

This demo site is hosted on `AWS`_ and uses third party authentication
services provided by `Auth0`_.

.. _AWS: https://aws.amazon.com
.. _Auth0: https://auth0.com

The project is broken into three main applications, each making use of a
specific implementation method to demonstrate the different authentication
and authorization key flows. Together these applications form a suite of 
tools that allow managers to create tasks and assign them to users, and
allows users to view their assigned tasks, create their own tasks, and 
mark their tasks completed. 

.. toctree::
   :maxdepth: 1

   spa
   webapp
   api
