.. _api-auth:

==============================================
GetErDone API Authentication and Authorization
==============================================

The GetErDone API provides access to the To-Do lists
owned by the the users of various applications. In 
terms of Authentication and Authorization, we can
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

In the GetErDone API, the resource server will grant
the resource owner access to operations on the To-Do
list based on Authorization information contained within
the "claims" made in the verified Access Token. These
claims include information about the user, as well as
the operations they are allowed to perform. The claim
used by the API to determine Authorization to access an
operation is called "scope".

The GetErDone API suite makes use of Auth0 Rules to
filter the scopes available to users.

The GetErDone API restricts access using the following
scopes: 'read:tasks', 'write:tasks', 'assign:tasks', and
'delete:tasks'.

The GetErDone SPA makes use of the 'read:tasks' and 
'write:tasks' scopes to allow a user with the title
of 'user' to view, update, and create new tasks for
themselves. The GetErDone WebApp uses the additional
'assign:tasks', and 'delete:tasks' to allow a user
with the 'manager' title to assign tasks to others
or to delete them once they are completed.



**GetErDone-API Authentication and Authorization** 
