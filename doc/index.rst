.. Get Er Done!

============
GetErDone!
============

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

.. toctree::
   :maxdepth: 2

   spa
   webapp
   api
