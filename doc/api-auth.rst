.. _api-auth:

==============================================
GetErDone API Authentication and Authorization
==============================================

The GetErDone API provides REST access to the To-Do
lists owned by the the users of various applications.

A primary goal of the API is to make sure that To-Do
list tasks are only accessed by the users that own
them. This goal can be met using concepts of
Authenication - the user has provided valid
credentials, and Authorization - the user is
provisioned for a valid set of activities. To meet
this end, the API uses services provided by Auth0.

In terms of Authentication and Authorization, we can
think of these users as "resource owners", the To-Do
lists themselves as "resources", and the API server as
the "resource server".


Authentication

In the GetErDone API, the resource owner's identity is
authenticated by examining and validating the OAuth2
Access Token provided in the HTTP Authorization header.

The Access Token is an encoded JSON Web Token (JWT). The
GetErDone API decodes the JWT using the 'python-jose'
toolkit. In the decoding process the toolkit will
download public cryptographic keys from Auth0, using
them to verify an RS256 signature embedded in the JWT. 
Once the signature is verified, the payload of the JWT
can be trusted as authentic.


Authorization

The GetErDone API, as the resource server, will grant
the resource owner access to operations on the To-Do
list based on Authorization information contained within
the set of "claims" made in the verified Access Token.
These claims include information about the user, as well
as the operations they are allowed to perform. The claim
used by the resource server to determine a user is
authorized to access an operation is called "scope".

The GetErDone API provides access using the following
scopes: 'read:tasks', 'write:tasks', 'assign:tasks', and
'delete:tasks'.

The GetErDone SPA makes use of the 'read:tasks' and 
'write:tasks' scopes to allow a user to view, update,
and create new tasks for themselves. The GetErDone
WebApp uses the additional 'assign:tasks', and
'delete:tasks' to allow users with these scopes
to assign tasks to others, or delete them once
they are completed. 

The GetErDone suite makes use of Auth0 Rules to
filter the scopes available to individual users.


**GetErDone-API Authentication and Authorization** 
