function (user, context, callback) {

  // permissions should only be set for verified users.
  if (!user.email || !user.email_verified) {
    return callback(null, user, context);
  }

  user.app_metadata = user.app_metadata || {};

  const addPermsToUser = function(user) {
    var perms = ['read', 'write'];
    if (user.user_metadata.title === 'manager') {
      perms.push('assign');
      perms.push('delete');
    }
    return(perms);
  };

  const perms = addPermsToUser(user);

  user.app_metadata.perms = perms;

  // store the app metadata back to auth0, then update the id token
  auth0.users.updateAppMetadata(user.user_id, user.app_metadata)
    .then(function() {
      context.idToken['http://api.techex.epoxyloaf.com/perms'] = user.app_metadata.perms;
      callback(null, user, context);
    })
    .catch(function (err) {
      callback(err);
    });
}
