$(function(){

    var GetErDoneTask = Backbone.Model.extend({

	defaults: function() {
	    return {
		title: "empty task...",
		priority: "normal",
		order: GetErDoneTasks.nextOrder(),
		done: false
	    };
	},

	toggle: function() {
	    this.save({done: !this.get("done")});
	}

    });

    var rem = {};

    var GetErDoneTaskList = Backbone.Collection.extend({

	model: GetErDoneTask,

        url: "http://api.techex.epoxyloaf.com/tasks",

	done: function() {
	    return this.where({done: true});
	},

	remaining: function() {
	    return this.where({done: false});
	},

	nextOrder: function() {
            var d = new Date();
            var seconds = Math.round(d.getTime() / 1000);
            return(seconds);
	},

	comparator: 'order'

    });

    var GetErDoneTasks = new GetErDoneTaskList;


    var GetErDoneTaskView = Backbone.View.extend({

	tagName:  "li",

	template: _.template($('#item-template').html()),

	events: {
	    "click .toggle" : "toggleDone",
	    "change .choosePriority" : "setPriority",
	    "dblclick .view" : "edit",
	    "click a.destroy" : "clear",
	    "keypress .edit" : "updateOnEnter",
	    "blur .edit" : "close"
	},

	initialize: function() {
	    this.listenTo(this.model, 'change', this.render);
	    this.listenTo(this.model, 'destroy', this.remove);
	},

	render: function() {
	    this.$el.html(this.template(this.model.toJSON()));
	    this.$el.toggleClass('done', this.model.get('done'));
	    this.input = this.$('.edit');
	    this.priority = this.$('.choosePriority');
	    return this;
	},

	toggleDone: function() {
	    this.model.toggle();
	},

	setPriority: function() {
	    var value = this.priority.val();
            console.log( "priority: " + value);
	    if (!value) {
		value = "normal";
	    }
            this.model.save({priority: value});
	},

	edit: function() {
	    this.$el.addClass("editing");
	    this.input.focus();
	},

	close: function() {
	    var value = this.input.val();
	    if (!value) {
		this.clear();
	    } else {
		this.model.save({title: value});
		this.$el.removeClass("editing");
	    }
	},

	updateOnEnter: function(e) {
	    if (e.keyCode == 13) this.close();
	},

	clear: function() {
	    this.model.destroy();
	}

    });


    var AppView = Backbone.View.extend({

	el: $("#get-er-done-spa"),

	statsTemplate: _.template($('#stats-template').html()),

	events: {
	    "keypress #new-self-task":  "createOnEnter",
	    "click #clear-completed": "clearCompleted",
	    "click #toggle-all": "toggleAllComplete"
	},

	initialize: function() {

	    this.input = this.$("#new-self-task");
	    this.allCheckbox = this.$("#toggle-all")[0];

	    this.listenTo(GetErDoneTasks, 'add', this.addOne);
	    this.listenTo(GetErDoneTasks, 'reset', this.addAll);
	    this.listenTo(GetErDoneTasks, 'all', this.render);

	    this.footer = this.$('footer');
	    this.main = $('#main');

	},

	render: function() {
	    var done = GetErDoneTasks.done().length;
	    var remaining = GetErDoneTasks.remaining().length;

	    if (GetErDoneTasks.length) {
		this.main.show();
		this.footer.show();
		this.footer.html(this.statsTemplate({done: done, remaining: remaining}));
	    } else {
		this.main.hide();
		this.footer.hide();
	    }

	    this.allCheckbox.checked = !remaining;
	},

	addOne: function(task) {
            console.log('addOne()');
	    var view = new GetErDoneTaskView({model: task});
	    this.$("#get-er-done-spa-list").append(view.render().el);
	},

	addAll: function() {
	    GetErDoneTasks.each(this.addOne, this);
	},

	createOnEnter: function(e) {
	    if (e.keyCode != 13) return;
	    if (!this.input.val()) return;

	    GetErDoneTasks.create({title: this.input.val()});
	    this.input.val('');
	},

	clearCompleted: function() {
	    _.invoke(GetErDoneTasks.done(), 'destroy');
	    return false;
	},

	toggleAllComplete: function () {
	    var done = this.allCheckbox.checked;
	    GetErDoneTasks.each(function (task) { task.save({'done': done}); });
	}

    });


    var App = new AppView;


    // AUTH0

    var content = $('.content');
    var loadingSpinner = $('#loading');
    content.css('display', 'block');
    loadingSpinner.css('display', 'none');;

    var webAuth = new auth0.WebAuth({
        domain: '{{ auth_config['auth0_domain'] }}',
        clientID: '{{ auth_config['auth0_client_id'] }}',
        redirectUri: '{{ auth_config['auth0_login_callback_url'] }}',
        audience: '{{ auth_config['auth0_audience'] }}',
        responseType: 'token id_token',
        scope: 'openid',
        leeway: 60
    });

    var loginStatus = $('.container h4');
    var loginView = $('#login-view');
    var getErDoneAppView = $('#get-er-done-spa-view');

    // buttons and event listeners
    var loginBtn = $('#btn-login');
    var logoutBtn = $('#btn-logout');

    loginBtn.click(function(e) {
        e.preventDefault();
        webAuth.authorize();
    });

    logoutBtn.click(logout);

    function setSession(authResult) {

        // Set the time when the access token will expire
        var expiresAt = JSON.stringify(
            authResult.expiresIn * 1000 + new Date().getTime()
        );

        localStorage.setItem('access_token', authResult.accessToken);
        localStorage.setItem('id_token', authResult.idToken);
        localStorage.setItem('expires_at', expiresAt);

        var backboneSync = Backbone.sync;
        Backbone.sync = function (method, model, options) {
            options.headers = {'Authorization': 'Bearer ' 
                                                + localStorage.getItem('access_token')};
            backboneSync(method, model, options);
        }

    }

    function logout() {

        // Remove tokens and expiry time from localStorage
        localStorage.removeItem('access_token');
        localStorage.removeItem('id_token');
        localStorage.removeItem('expires_at');

        displayButtons();
        displayGetErDoneApp();

        webAuth.logout({returnTo: '{{ auth_config['auth0_logout_callback_url'] }}'}, 
                       {version: 'v2'});

    }

    function isAuthenticated() {
        var expiresAt = JSON.parse(localStorage.getItem('expires_at'));
        var timeNow = new Date().getTime();
        console.log('isAuthenticated() timeNow=' + timeNow + ' expiresAt=' + expiresAt);
        if(timeNow < expiresAt) {
            return(1);
        }
        return(0);
    }

    function handleAuthentication() {
        webAuth.parseHash(function(err, authResult) {
            if (authResult && authResult.accessToken && authResult.idToken) {
                window.location.hash = '';
                setSession(authResult);
                loginBtn.css('display', 'none');
            } else if (err) {
                console.log(err);
                alert('Error: ' + err.error + '. Check the console for further details.');
            }
            displayButtons();
            displayGetErDoneApp();
        });
    }

    function displayButtons() {
        if (isAuthenticated()) {
            loginBtn.css('display', 'none');
            logoutBtn.css('display', 'inline-block');
            loginStatus.text('You are logged in!');
        } else {
            loginBtn.css('display', 'inline-block');
            logoutBtn.css('display', 'none');
            loginStatus.text('You are not logged in! Please log in to continue.');
        }
    }

    function displayGetErDoneApp() {
        if (isAuthenticated()) {
            console.log('displaying app');
            getErDoneAppView.css('display', 'inline-block');
	    GetErDoneTasks.fetch();
        } else {
            console.log('hiding app');
            getErDoneAppView.css('display', 'none');
        }
    }

    handleAuthentication();

});
