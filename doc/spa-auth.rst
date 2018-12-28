.. _spa-auth:

==============================================
GetErDone SPA Authentication and Authorization
==============================================

**GetErDone-SPA** uses the Implicit grant type from the OAuth 2.0
authorization framework, and authentication with OpenID Connect,
using Auth0 as an identity provider.

The Implicit flow is initiated by redirecting the user to the
GetErDone-SPA url that utlimately loads a JavaScript application
designed to load once and run in the user's browser. Here the
user may choose to log in to the application, where a dialog
is loaded allowing the user to provide credentials to Auth0, or
alternatively choose any other configured identity provider. Once
authenticated, the identity provider will then issue the application
an access token which will be stored and used as credentials for
calls to the GetErDone-API.
