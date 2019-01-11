function (user, context, callback) {

  user.app_metadata = user.app_metadata || {};

  // restrict any scope starting with (read:|write:|delete:|assign:)
  // to the permissions in user.app_metadata.perms[]
  const setScopesForUser = function(user, scopes_requested) {
    var user_scopes = scopes;
    return(user_scopes);
  };

  const scope = setScopesForUser(user, context.idToken.scope);

  context.idToken.scope = scope;

  callback(null, user, context);
}
