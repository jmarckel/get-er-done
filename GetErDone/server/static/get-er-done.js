$(function(){


    // GetErDone Task Model
    var GetErDoneTask = Backbone.Model.extend({

	// default values for an empty task
	defaults: function() {
	    return {
		title: "empty task...",
		order: GetErDoneTasks.nextOrder(),
		done: false
	    };
	},

	toggle: function() {
	    this.save({done: !this.get("done")});
	}

    });


    // GetErDone Task Collection
    var GetErDoneTaskList = Backbone.Collection.extend({

	// Reference to this collection's model.
	model: GetErDoneTask,

	// Save all of the tasks under the `"tasks-backbone"` namespace.
	localStorage: new Backbone.LocalStorage("tasks-backbone"),

	// Filter down the list of all tasks that are finished.
	done: function() {
	    return this.where({done: true});
	},

	// Filter down the list to only tasks that are still not finished.
	remaining: function() {
	    return this.where({done: false});
	},

	// We keep the GetErDoneTasks in sequential order, despite being saved by unordered
	// GUID in the database. This generates the next order number for new items.
	nextOrder: function() {
	    if (!this.length) return 1;
	    return this.last().get('order') + 1;
	},

	// GetErDoneTasks are sorted by their original insertion order.
	comparator: 'order'

    });

    var GetErDoneTasks = new GetErDoneTaskList;


    var GetErDoneTaskView = Backbone.View.extend({

	tagName:  "li",

	template: _.template($('#item-template').html()),

	events: {
	    "click .toggle"   : "toggleDone",
	    "dblclick .view"  : "edit",
	    "click a.destroy" : "clear",
	    "keypress .edit"  : "updateOnEnter",
	    "blur .edit"      : "close"
	},

	initialize: function() {
	    this.listenTo(this.model, 'change', this.render);
	    this.listenTo(this.model, 'destroy', this.remove);
	},

	render: function() {
	    this.$el.html(this.template(this.model.toJSON()));
	    this.$el.toggleClass('done', this.model.get('done'));
	    this.input = this.$('.edit');
	    return this;
	},

	toggleDone: function() {
	    this.model.toggle();
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
	    "keypress #new-todo":  "createOnEnter",
	    "click #clear-completed": "clearCompleted",
	    "click #toggle-all": "toggleAllComplete"
	},

	initialize: function() {

	    this.input = this.$("#new-todo");
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
	    this.$("#todo-list").append(view.render().el);
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
