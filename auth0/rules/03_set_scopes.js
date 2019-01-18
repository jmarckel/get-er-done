function (user, context, callback) {

  user.app_metadata = user.app_metadata || {};

  // restrict any scope starting with (read:|write:|delete:|assign:)
  // and ending in 'tasks' to the permissions in user.app_metadata.perms[]
  const setScopesForUser = function(user, scopes_requested) {
    var perms = user.app_metadata.perms || [];
    var user_scopes = [];
    var req_scopes = scopes_requested.split(' ');
    for (var i = 0; i < req_scopes.length; i++) {
       var parts = req_scopes[i].split(':');
       if (parts.length === 2 && parts[1] === 'tasks') {
           if (!perms.includes(parts[0])) {
               // the user cannot have this scope
               continue;
           }
       }
       user_scopes.push(req_scopes[i]);
    }
    return(user_scopes.join(' '));
  };

  var requested = context.request.body.scope || context.request.query.scope;
  var authorized = setScopesForUser(user, requested);

  console.log("requested_scopes=" + requested);
  console.log("authorized_scopes=" + authorized);

  context.accessToken.scope = authorized;

  callback(null, user, context);
}
