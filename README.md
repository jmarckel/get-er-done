<div class="related" role="navigation" aria-label="related navigation">

### Navigation

-   [GetErDone](index.html#document-index) »

</div>

<div class="document">

<div class="documentwrapper">

<div class="bodywrapper">

<div class="body" role="main">

<div id="geterdone" class="section">

GetErDone[¶](#geterdone "Permalink to this headline"){.headerlink}
==================================================================

**GetErDone** is a technical exercise designed to demonstrate use cases
for authorization and authentication workflows of network based
applications using
[OAuth2](https://en.wikipedia.org/wiki/OAuth){.reference .external} and
[OpenID\_Connect](https://en.wikipedia.org/wiki/OpenID_Connect){.reference
.external}.

This free demo site is hosted on
[AWS](https://aws.amazon.com){.reference .external} and uses third party
authentication services provided by
[Auth0](https://auth0.com){.reference .external}.

The project is broken into three main applications, each making use of a
specific implementation method to demonstrate the different
authentication and authorization key flows. Together these applications
form a suite of tools that allow managers to create tasks, assigning
them to users, and also allowing users to view their own assigned tasks,
create their own tasks, and mark their tasks completed.

For the purposes of this demonstration site, access to the applications
and API is based on a users ‘title’, which is set based on the email
address that the user registers with. To create a user with the
‘manager’ title, use an email address where the username is split with
the plus (‘+’) sign, and the word to the right of the ‘+’ includes the
word ‘manager’. So the user jeff@epoxyloaf.com would have the title
‘user’, and the user jeff+the\_manager\_guy@epoxyloaf.com would have the
title ‘manager’.

In either case, you should get an email from a user techex-epoxyloaf-com
includng instructions (click one link) on how to complete the
registration process, before the free account can be accessed.

<div class="toctree-wrapper compound">

<span id="document-spa"></span>
<div id="geterdone-spa" class="section">

<span id="spa"></span>
GetErDone SPA[¶](#geterdone-spa "Permalink to this headline"){.headerlink}
--------------------------------------------------------------------------

**GetErDone-SPA** is a JavaScript based single page application that
allows authenticated users to interact with a list of assigned tasks.
These tasks may be assigned by the GetErDone-webapp or created on their
own. Once a user has completed a task, they may mark it done in the
application.

In order to use this application for the first time, you will need to
create a user. To create a new user, use the ‘Sign Up’ tab on the login
screen, and enter an email address. To create multiple accounts, enter
an email address where the username is split with the plus (‘+’) sign.

Modern email services like google will deliver the email for the user
‘jeff+test\_one’ to the inbox for ‘jeff’, and you can use as many
aliases as you like this way.

Once the new user is created, before the application will work
correctly, you will need to **finish the registration process** in the
account confirmation email from techex-epoxyloaf-com.

Click [here](http://spa.techex.epoxyloaf.com){.reference .external} to
launch.

<div class="toctree-wrapper compound">

<span id="document-spa-auth"></span>
<div id="geterdone-spa-authentication-and-authorization"
class="section">

<span id="spa-auth"></span>
### GetErDone SPA Authentication and Authorization[¶](#geterdone-spa-authentication-and-authorization "Permalink to this headline"){.headerlink}

**GetErDone-SPA** uses the Implicit Grant type from the OAuth 2.0
authorization framework, and authentication with OpenID Connect, using
services provided by Auth0.

The Implicit Grant flow is initiated by redirecting the user to the
GetErDone-SPA url that utlimately loads a JavaScript application
designed to load once and run in the user’s browser. Here the user may
choose to log in to the application, where a dialog is loaded allowing
the user to provide credentials to Auth0, or alternatively choose any
other configured identity provider. Once authenticated, Auth0 will then
issue the application an Access Token which will be stored and used as
credentials for calls to the GetErDone-API.

</div>

<span id="document-spa-stack"></span>
<div id="geterdone-spa-stack" class="section">

<span id="spa-stack"></span>
### GetErDone SPA Stack[¶](#geterdone-spa-stack "Permalink to this headline"){.headerlink}

**GetErDone-SPA** is a JavaScript based single page application

</div>

<span id="document-spa-ack"></span>
<div id="geterdone-spa-acknowledgements" class="section">

<span id="spa-ack"></span>
### GetErDone SPA Acknowledgements[¶](#geterdone-spa-acknowledgements "Permalink to this headline"){.headerlink}

**GetErDone-SPA** is based on the Backbone.js demo app “ToDo List”

</div>

</div>

</div>

<span id="document-webapp"></span>
<div id="geterdone-webapp" class="section">

<span id="webapp"></span>
GetErDone WebApp[¶](#geterdone-webapp "Permalink to this headline"){.headerlink}
--------------------------------------------------------------------------------

**GetErDone-WebApp** is an html based tool allowing managers to interact
with lists of tasks to be done by others.

In order to use this application, you will need to create a user with
the role of ‘manager’. To create a user with the ‘manager’ title, use
the ‘Sign Up’ tab on the login screen, and enter an email address where
the username is split with the plus (‘+’) sign, and the letters to the
right of the ‘+’ includes the word ‘manager’. So the user
jeff@epoxyloaf.com would have the title ‘user’, and the user
jeff+the\_manager\_guy@epoxyloaf.com would have the title ‘manager’.

Modern email services like google will deliver the email for the user
‘jeff+test\_manager’ to the inbox for ‘jeff’, and you can use as many
aliases as you like this way.

Once the new user is created, before the application will work
correctly, you will need to **finish the registration process** in the
account confirmation email from techex-epoxyloaf-com.

Click [here](http://webapp.techex.epoxyloaf.com){.reference .external}
to launch the webapp.

<div class="toctree-wrapper compound">

<span id="document-webapp-auth"></span>
<div id="geterdone-webapp-authentication-and-authorization"
class="section">

<span id="webapp-auth"></span>
### GetErDone WebApp Authentication and Authorization[¶](#geterdone-webapp-authentication-and-authorization "Permalink to this headline"){.headerlink}

**GetErDone-WebApp** uses the Authorization Code grant type from the
OAuth 2.0 authorization framework, and authentication with OpenID
Connect, using Auth0 as an identity provider.

The Authorization Code flow is initiated by redirecting the user to the
Auth0 /authorize endpoint cooresponding to the GetErDone-WebApp. Here
the user enters credentials to Auth0, or alternatively chooses any other
configured identity provider. Once authenticated, Auth0 will then
redirect the user back GetErDone-WebApp, where session information can
be verified and recorded, before sending the user on to the application
itself.

An access token is also stored, to be used as credentials for calls to
the GetErDone-API.

</div>

<span id="document-webapp-stack"></span>
<div id="geterdone-webapp-stack" class="section">

<span id="webapp-stack"></span>
### GetErDone WebApp Stack[¶](#geterdone-webapp-stack "Permalink to this headline"){.headerlink}

**GetErDone-WebApp** is hosted on an Apache2 web server running as a
WSGI process implemented in Python with Flask.

</div>

</div>

</div>

<span id="document-api"></span>
<div id="geterdone-api" class="section">

<span id="api"></span>
GetErDone API[¶](#geterdone-api "Permalink to this headline"){.headerlink}
--------------------------------------------------------------------------

The GetErDone-API is a ReST API service allowing network applications to
interact with lists of tasks assigned to users. Any authenticated user
is allowed to create and complete tasks for themselves, but only users
with a manager role may assign tasks to others.

<div class="toctree-wrapper compound">

<span id="document-api-auth"></span>
<div id="geterdone-api-authentication-and-authorization"
class="section">

<span id="api-auth"></span>
### GetErDone API Authentication and Authorization[¶](#geterdone-api-authentication-and-authorization "Permalink to this headline"){.headerlink}

The **GetErDone API** provides REST access to the To-Do lists owned by
the the users of various applications.

A primary goal of the API is to make sure that To-Do list tasks are only
accessed by the users that own them. This goal can be met using concepts
of Authenication - the user has provided valid credentials, and
Authorization - the user is provisioned for a valid set of activities.
To meet this end, the API uses services provided by Auth0.

Following OAuth2 and OIDC, in terms of Authentication and Authorization,
we can think of these users as “resource owners”, the To-Do lists
themselves as the “resources”, and the API server as the “resource
server”.

<div id="authentication" class="section">

#### Authentication[¶](#authentication "Permalink to this headline"){.headerlink}

In the GetErDone API, the resource owner’s identity is authenticated by
examining and validating the OAuth2 Access Token provided in the HTTP
Authorization header.

The Access Token is an encoded JSON Web Token (JWT). The GetErDone API
decodes the JWT using the ‘python-jose’ toolkit. In the decoding process
the toolkit will download public cryptographic keys from Auth0, using
them to verify an RS256 signature embedded in the JWT. Once the
signature is verified, the payload of the JWT can be trusted as
authentic.

</div>

<div id="authorization" class="section">

#### Authorization[¶](#authorization "Permalink to this headline"){.headerlink}

The GetErDone API, as the resource server, will grant the resource owner
access to operations on their resources based on Authorization
information contained within the set of “claims” made in the verified
Access Token. These claims include information about the user, including
the operations they are allowed to perform. The claim used by the
resource server to determine a resource owner is authorized to access an
operation is called “scope”.

The GetErDone API provides access using the following scopes:
‘read:tasks’, ‘write:tasks’, ‘assign:tasks’, and ‘delete:tasks’.

The GetErDone SPA makes use of the ‘read:tasks’ and ‘write:tasks’ scopes
to allow a user to view, update, and create new tasks for themselves.
The GetErDone WebApp uses the additional ‘assign:tasks’, and
‘delete:tasks’ to allow users with these scopes to assign tasks to
others, or delete them once they are completed.

The GetErDone suite makes use of Auth0 Rules to filter the scopes
available to individual users.

</div>

</div>

<span id="document-api-stack"></span>
<div id="geterdone-api-stack" class="section">

<span id="api-stack"></span>
### GetErDone API Stack[¶](#geterdone-api-stack "Permalink to this headline"){.headerlink}

**GetErDone-API** is a ReST API served on Apache2 with WSGI to a Python
Flask application using authentication and authorization services
provided by Auth0 ...

</div>

<span id="document-api-storage"></span>
<div id="geterdone-api-storage" class="section">

<span id="api-storage"></span>
### GetErDone API Storage[¶](#geterdone-api-storage "Permalink to this headline"){.headerlink}

**GetErDone-API Storage**

</div>

</div>

</div>

</div>

</div>

</div>

</div>

</div>

<div class="sphinxsidebar" role="navigation"
aria-label="main navigation">

<div class="sphinxsidebarwrapper">

### [Table Of Contents](index.html#document-index)

-   [GetErDone SPA](index.html#document-spa){.reference .internal}
-   [GetErDone WebApp](index.html#document-webapp){.reference .internal}
-   [GetErDone API](index.html#document-api){.reference .internal}

</div>

</div>

<div class="clearer">

</div>

</div>

<div class="related" role="navigation" aria-label="related navigation">

### Navigation

-   [GetErDone](index.html#document-index) »

</div>

<div class="footer" role="contentinfo">

© Copyright 2018, Jeff Marckel. Created using
[Sphinx](http://sphinx-doc.org/) 1.3.6.

</div>
