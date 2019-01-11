function (user, context, callback) {

  // title should only be set for verified users.
  if (!user.email || !user.email_verified) {
    return callback(null, user, context);
  }

  user.user_metadata = user.user_metadata || {};

  const addTitleToUser = function(user) {
    var user_title = 'user';
    return(user_title);
  };

  const title = addTitleToUser(user);

  user.user_metadata.title = title;

  // store the app metadata back to auth0, then update the id token
  auth0.users.updateUserMetadata(user.user_id, user.user_metadata)
    .then(function() {
      context.idToken['http://api.techex.epoxyloaf.com/title'] = user.user_metadata.title;
      callback(null, user, context);
    })
    .catch(function (err) {
      callback(err);
    });
}
