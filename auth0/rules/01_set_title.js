function (user, context, callback) {

  // This is a contrived rule, meant to demonstrate ordering of
  // rules and the updating of User Metadata at Auth0

  // title should only be set for verified users.
  if (!user.email || !user.email_verified) {
    return callback(null, user, context);
  }

  user.user_metadata = user.user_metadata || {};

  const addTitleToUser = function(user) {
    // look at the email address
    // split into name and domain parts on '@'
    // try to split name part on '+'
    // if RHS of name part contains 'goob' then title is 'manager'
    // else default is 'user'
    var user_title = 'user';
    var tmp = user.email;
    var parts = tmp.split('@');
    if(parts.length === 2) {
      var uparts = parts[0].split('+');
      if(uparts.length === 2) {
        if(uparts[1].includes('goob')) {
          user_title = 'manager';
        }
      }
    }
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
