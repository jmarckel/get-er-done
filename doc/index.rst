.. Get Er Done!

Get Er Done!
========================================

*GetErDone* is a technical exercise designed to demonstrate use cases
for authorization and authentication workflows of network based applications
using `OAuth2`_ and `OpenID_Connect`_. 

.. _OAuth2: https://en.wikipedia.org/wiki/OAuth
.. _OpenID_Connect: https://en.wikipedia.org/wiki/OpenID_Connect

The project is broken into three main applications, each making use of a
specific implementation method to demonstrate the flexibility of the tools.
Together these applications form a suite of tools that allow for managers
to create tasks and assign them to users, and allows users to view their 
assigned tasks, create their own tasks, and mark their tasks completed. 

.. _API: http://api.techex.epoxyloaf.com


GetErDone SPA
---------------

An application for users to interact with a list of tasks.

.. toctree::
   :maxdepth: 2

   spa

GetErDone WebApp
------------------

An application for managers to create tasks for users.

.. toctree::
   :maxdepth: 2

   webapp

GetErDone API
------------------

A web api for the applications to use.

.. toctree::
   :maxdepth: 2

   api



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

