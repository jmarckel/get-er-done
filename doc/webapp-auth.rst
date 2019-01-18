.. _webapp-auth:

=================================================
GetErDone WebApp Authentication and Authorization
=================================================

**GetErDone-WebApp** uses the Authorization Code grant type from the OAuth 2.0
authorization framework, and authentication with OpenID Connect, using Auth0 
as an identity provider.

The Authorization Code flow is initiated by redirecting the user to the
Auth0 /authorize endpoint corresponding to the GetErDone-WebApp. Parameters
to the call include a callback URL, and the "scopes" the application requests
access to. At this point control is passed to Auth0 where they will display a
dialog the user can login, or create a new account with. Here the user enters
credentials to Auth0, or alternatively chooses any other configured identity
provider. Once authenticated, Auth0 will then redirect the user back
GetErDone-WebApp at the callback address specified, where session information
can be verified and recorded, before sending the user on to the application
itself.

The GetErDone suite uses OIDC scope claims to authorize users access to the
various services provided by the GetErDone-API. These scopes are encoded into
the Authorization header which is used by the webapp to make calls to the
API on behalf of the user.

The GetErDone-WebApp will request the following GetErDone-API scopes:
    * read:tasks
    * write:tasks
    * delete:tasks
    * assign:tasks

