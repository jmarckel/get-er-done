.. _spa-auth:

==============================================
GetErDone SPA Authentication and Authorization
==============================================

**GetErDone-SPA** uses the Implicit Grant type from the OAuth 2.0
authorization framework, and authentication with OpenID Connect,
using services provided by Auth0.

The Implicit Grant flow is initiated by redirecting the user to the
GetErDone-SPA url that ultimately loads a JavaScript application
designed to load once and run in the user's browser. Here the
user may choose to log in to the application, where a dialog
is loaded allowing the user to provide credentials to Auth0, or
alternatively choose any other configured identity provider. Once
authenticated, Auth0 will then issue the application an Access
Token which will be stored and used as credentials for calls
to the GetErDone-API.

