.. _webapp-auth:

=================================================
GetErDone WebApp Authentication and Authorization
=================================================

**GetErDone-WebApp** uses the Authorization Code grant type from the OAuth 2.0
authorization framework, and authentication with OpenID Connect, using Auth0 
as an identity provider.

The Authorization Code flow is initiated by redirecting the user to the
Auth0 /authorize endpoint cooresponding to the GetErDone-WebApp. Here the
user enters credentials to Auth0, or alternatively chooses any other configured
identity provider. Once authenticated, Auth0 will then redirect the user back
GetErDone-WebApp, where session information can be verified and recorded, 
before sending the user on to the application itself.

An access token is also stored, to be used as credentials for calls to 
the GetErDone-API.

