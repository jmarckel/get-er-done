$(function(){

    var GetErDoneTask = Backbone.Model.extend({

	// default values for an empty task
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

        url: "/tasks",

	done: function() {
	    return this.where({done: true});
	},

	remaining: function() {
	    return this.where({done: false});
	},

	nextOrder: function() {
            var d = new Date();
            var seconds = Math.round(d.getTime() / 1000);
            return(seconds)
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

	    GetErDoneTasks.fetch();
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

});
