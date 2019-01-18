
=========
GetErDone
=========

**GetErDone** is a technical exercise designed to demonstrate use cases
for authorization and authentication workflows of network based applications
using `OAuth2`_ and `OpenID_Connect`_. 

.. _OAuth2: https://en.wikipedia.org/wiki/OAuth
.. _OpenID_Connect: https://en.wikipedia.org/wiki/OpenID_Connect

This free demo site is hosted on `AWS`_ and uses third party authentication
services provided by `Auth0`_.

.. _AWS: https://aws.amazon.com
.. _Auth0: https://auth0.com

The project is broken into three main applications, each making use of a
specific implementation method to demonstrate the different authentication
and authorization key flows. Together these applications form a suite of 
tools that allow managers to create tasks, assigning them to users, and
also allowing users to view their own assigned tasks, create their own
tasks, and mark their tasks completed. 

For the purposes of this demonstration site, access to the applications
and API is based on a users 'title', which is set based on the email address
that the user registers with. To create a user with the 'manager' title, use
an email address where the username is split with the plus ('+') sign, and
the word to the right of the '+' includes the word 'manager'. So the user
`jeff@epoxyloaf.com` would have the title 'user', and the user
`jeff+the_manager_guy@epoxyloaf.com` would have the title 'manager'.

In either case, you should get an email from a user `techex-epoxyloaf-com`
includng instructions (click one link) on how to complete the registration
process, before the free account can be accessed.

.. toctree::
   :maxdepth: 1

   spa
   webapp
   api
