function (user, context, callback) {

  user.app_metadata = user.app_metadata || {};

  // restrict any scope starting with (read:|write:|delete:|assign:)
  // and ending in 'tasks' to the permissions in user.app_metadata.perms[]
  const setScopesForUser = function(user, scopes_requested) {
    var perms = user.app_metadata.perms;
    var user_scopes = [];
    for (var req_scope in scopes_requested.split(' ')) {
       var parts = req_scope.split(':');
       if (parts.length === 2 && parts[1] === 'tasks') {
           if (!perms.includes(parts[0])) {
               // the user cannot have this scope
               continue;
           }
       }
       user_scopes.push(req_scope);
    }
    return(user_scopes.join(' '));
  };

  var requested = context.request.body.scope || context.request.query.scope;

  context.accessToken.scope = setScopesForUser(user, requested);

  callback(null, user, context);
}
