### Navigation

-   [GetErDone](index.html#document-index) »

GetErDone<a href="#geterdone" class="headerlink" title="Permalink to this headline">¶</a>
=========================================================================================

**GetErDone** is a technical exercise designed to demonstrate use cases for authorization and authentication workflows of network based applications using <a href="https://en.wikipedia.org/wiki/OAuth" class="reference external">OAuth2</a> and <a href="https://en.wikipedia.org/wiki/OpenID_Connect" class="reference external">OpenID_Connect</a>.

This free demo site is hosted on <a href="https://aws.amazon.com" class="reference external">AWS</a> and uses third party authentication services provided by <a href="https://auth0.com" class="reference external">Auth0</a>.

The project is broken into three main applications, each making use of a specific implementation method to demonstrate the different authentication and authorization key flows. Together these applications form a suite of tools that allow managers to create tasks, assigning them to users, and also allowing users to view their own assigned tasks, create their own tasks, and mark their tasks completed.

For the purposes of this demonstration site, access to the applications and API is based on a users ‘title’, which is set based on the email address that the user registers with. To create a user with the ‘manager’ title, use an email address where the username is split with the plus (‘+’) sign, and the word to the right of the ‘+’ includes the word ‘manager’. So the user jeff@epoxyloaf.com would have the title ‘user’, and the user jeff+the\_manager\_guy@epoxyloaf.com would have the title ‘manager’.

In either case, you should get an email from a user techex-epoxyloaf-com includng instructions (click one link) on how to complete the registration process, before the free account can be accessed.

<span id="document-spa"></span>
<span id="spa"></span>
GetErDone SPA<a href="#geterdone-spa" class="headerlink" title="Permalink to this headline">¶</a>
-------------------------------------------------------------------------------------------------

**GetErDone-SPA** is a JavaScript based single page application that allows authenticated users to interact with a list of assigned tasks. These tasks may be assigned by the GetErDone-webapp or created on their own. Once a user has completed a task, they may mark it done in the application.

In order to use this application for the first time, you will need to create a user. To create a new user, use the ‘Sign Up’ tab on the login screen, and enter an email address. To create multiple accounts, enter an email address where the username is split with the plus (‘+’) sign.

Modern email services like google will deliver the email for the user ‘jeff+test\_one’ to the inbox for ‘jeff’, and you can use as many aliases as you like this way.

Once the new user is created, before the application will work correctly, you will need to **finish the registration process** in the account confirmation email from techex-epoxyloaf-com.

Click <a href="http://spa.techex.epoxyloaf.com" class="reference external">here</a> to launch.

<span id="document-spa-auth"></span>
<span id="spa-auth"></span>
### GetErDone SPA Authentication and Authorization<a href="#geterdone-spa-authentication-and-authorization" class="headerlink" title="Permalink to this headline">¶</a>

**GetErDone-SPA** uses the Implicit Grant type from the OAuth 2.0 authorization framework, and authentication with OpenID Connect, using services provided by Auth0.

The Implicit Grant flow is initiated by redirecting the user to the GetErDone-SPA url that utlimately loads a JavaScript application designed to load once and run in the user’s browser. Here the user may choose to log in to the application, where a dialog is loaded allowing the user to provide credentials to Auth0, or alternatively choose any other configured identity provider. Once authenticated, Auth0 will then issue the application an Access Token which will be stored and used as credentials for calls to the GetErDone-API.

<span id="document-spa-stack"></span>
<span id="spa-stack"></span>
### GetErDone SPA Stack<a href="#geterdone-spa-stack" class="headerlink" title="Permalink to this headline">¶</a>

**GetErDone-SPA** is a JavaScript based single page application

<span id="document-spa-ack"></span>
<span id="spa-ack"></span>
### GetErDone SPA Acknowledgements<a href="#geterdone-spa-acknowledgements" class="headerlink" title="Permalink to this headline">¶</a>

**GetErDone-SPA** is based on the Backbone.js demo app “ToDo List”

<span id="document-webapp"></span>
<span id="webapp"></span>
GetErDone WebApp<a href="#geterdone-webapp" class="headerlink" title="Permalink to this headline">¶</a>
-------------------------------------------------------------------------------------------------------

**GetErDone-WebApp** is an html based tool allowing managers to interact with lists of tasks to be done by others.

In order to use this application, you will need to create a user with the role of ‘manager’. To create a user with the ‘manager’ title, use the ‘Sign Up’ tab on the login screen, and enter an email address where the username is split with the plus (‘+’) sign, and the letters to the right of the ‘+’ includes the word ‘manager’. So the user jeff@epoxyloaf.com would have the title ‘user’, and the user jeff+the\_manager\_guy@epoxyloaf.com would have the title ‘manager’.

Modern email services like google will deliver the email for the user ‘jeff+test\_manager’ to the inbox for ‘jeff’, and you can use as many aliases as you like this way.

Once the new user is created, before the application will work correctly, you will need to **finish the registration process** in the account confirmation email from techex-epoxyloaf-com.

Click <a href="http://webapp.techex.epoxyloaf.com" class="reference external">here</a> to launch the webapp.

<span id="document-webapp-auth"></span>
<span id="webapp-auth"></span>
### GetErDone WebApp Authentication and Authorization<a href="#geterdone-webapp-authentication-and-authorization" class="headerlink" title="Permalink to this headline">¶</a>

**GetErDone-WebApp** uses the Authorization Code grant type from the OAuth 2.0 authorization framework, and authentication with OpenID Connect, using Auth0 as an identity provider.

The Authorization Code flow is initiated by redirecting the user to the Auth0 /authorize endpoint cooresponding to the GetErDone-WebApp. Here the user enters credentials to Auth0, or alternatively chooses any other configured identity provider. Once authenticated, Auth0 will then redirect the user back GetErDone-WebApp, where session information can be verified and recorded, before sending the user on to the application itself.

An access token is also stored, to be used as credentials for calls to the GetErDone-API.

<span id="document-webapp-stack"></span>
<span id="webapp-stack"></span>
### GetErDone WebApp Stack<a href="#geterdone-webapp-stack" class="headerlink" title="Permalink to this headline">¶</a>

**GetErDone-WebApp** is hosted on an Apache2 web server running as a WSGI process implemented in Python with Flask.

<span id="document-api"></span>
<span id="api"></span>
GetErDone API<a href="#geterdone-api" class="headerlink" title="Permalink to this headline">¶</a>
-------------------------------------------------------------------------------------------------

The GetErDone-API is a ReST API service allowing network applications to interact with lists of tasks assigned to users. Any authenticated user is allowed to create and complete tasks for themselves, but only users with a manager role may assign tasks to others.

<span id="document-api-auth"></span>
<span id="api-auth"></span>
### GetErDone API Authentication and Authorization<a href="#geterdone-api-authentication-and-authorization" class="headerlink" title="Permalink to this headline">¶</a>

The **GetErDone API** provides REST access to the To-Do lists owned by the the users of various applications.

A primary goal of the API is to make sure that To-Do list tasks are only accessed by the users that own them. This goal can be met using concepts of Authenication - the user has provided valid credentials, and Authorization - the user is provisioned for a valid set of activities. To meet this end, the API uses services provided by Auth0.

Following OAuth2 and OIDC, in terms of Authentication and Authorization, we can think of these users as “resource owners”, the To-Do lists themselves as the “resources”, and the API server as the “resource server”.

#### Authentication<a href="#authentication" class="headerlink" title="Permalink to this headline">¶</a>

In the GetErDone API, the resource owner’s identity is authenticated by examining and validating the OAuth2 Access Token provided in the HTTP Authorization header.

The Access Token is an encoded JSON Web Token (JWT). The GetErDone API decodes the JWT using the ‘python-jose’ toolkit. In the decoding process the toolkit will download public cryptographic keys from Auth0, using them to verify an RS256 signature embedded in the JWT. Once the signature is verified, the payload of the JWT can be trusted as authentic.

#### Authorization<a href="#authorization" class="headerlink" title="Permalink to this headline">¶</a>

The GetErDone API, as the resource server, will grant the resource owner access to operations on their resources based on Authorization information contained within the set of “claims” made in the verified Access Token. These claims include information about the user, including the operations they are allowed to perform. The claim used by the resource server to determine a resource owner is authorized to access an operation is called “scope”.

The GetErDone API provides access using the following scopes: ‘read:tasks’, ‘write:tasks’, ‘assign:tasks’, and ‘delete:tasks’.

The GetErDone SPA makes use of the ‘read:tasks’ and ‘write:tasks’ scopes to allow a user to view, update, and create new tasks for themselves. The GetErDone WebApp uses the additional ‘assign:tasks’, and ‘delete:tasks’ to allow users with these scopes to assign tasks to others, or delete them once they are completed.

The GetErDone suite makes use of Auth0 Rules to filter the scopes available to individual users.

<span id="document-api-stack"></span>
<span id="api-stack"></span>
### GetErDone API Stack<a href="#geterdone-api-stack" class="headerlink" title="Permalink to this headline">¶</a>

**GetErDone-API** is a ReST API served on Apache2 with WSGI to a Python Flask application using authentication and authorization services provided by Auth0 ...

<span id="document-api-storage"></span>
<span id="api-storage"></span>
### GetErDone API Storage<a href="#geterdone-api-storage" class="headerlink" title="Permalink to this headline">¶</a>

**GetErDone-API Storage**

### [Table Of Contents](index.html#document-index)

-   <a href="index.html#document-spa" class="reference internal">GetErDone SPA</a>
-   <a href="index.html#document-webapp" class="reference internal">GetErDone WebApp</a>
-   <a href="index.html#document-api" class="reference internal">GetErDone API</a>

### Navigation

-   [GetErDone](index.html#document-index) »

© Copyright 2018, Jeff Marckel. Created using [Sphinx](http://sphinx-doc.org/) 1.3.6.
