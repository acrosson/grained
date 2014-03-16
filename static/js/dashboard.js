function edit_user(follow_user) {

	document.getElementById("key_words_"+follow_user).style.display = "block";
	document.getElementById('edit_'+follow_user).style.display = "none";
	document.getElementById('save_changes_'+follow_user).style.display = "inline-block";
	
	Array.prototype.remove = function(from, to) {
	  var rest = this.slice((to || from) + 1 || this.length);
	  this.length = from < 0 ? this.length + from : from;
	  return this.push.apply(this, rest);
	};
	
	var current_list = document.getElementById("key_words_list_"+follow_user).value;
	
	var list = current_list.split(",");
	
	var list_html = "<ul>";
	
	var list_str = "";
	for (i = 0; i < list.length; ++i) {
			list_html = list_html + "<li><a href='javascript:void(0);' onclick='remove_word("+i+",\"" + follow_user + "\")'>" + list[i] + " x</a></li>";
		
		if (i > 0) {
			list_str = list_str + "," + list[i];
		} else {
			list_str = list[i];
		}
	}
	list_html = list_html + "</ul>";
	
	document.getElementById("key_words_display_"+follow_user).innerHTML = list_html;
	
}

function add_key_word(follow_user) {

	var key_word = document.getElementById("key_words_"+follow_user).value;
	var current_list = document.getElementById("key_words_list_"+follow_user).value;
	
	if (key_word != "") {
		if (current_list != "") {
			current_list = current_list + "," + key_word;
		} else {
			current_list = key_word;
		}
		
		document.getElementById("key_words_"+follow_user).value = "";
		document.getElementById("key_words_list_"+follow_user).value = current_list;
		
		var list = current_list.split(",");
		var list_html = "<ul>";
		
		for (i = 0; i < list.length; ++i) {
			list_html = list_html + "<li><a href='javascript:void(0);' onclick='remove_word("+i+",\"" + follow_user + "\")'>" + list[i] + " x</a></li>";
		}
		list_html = list_html + "</ul>";
		
		document.getElementById("key_words_display_"+follow_user).innerHTML = list_html;
		
		document.getElementById("key_words_list_"+follow_user).value = current_list;
	}
}

function update(follow_user) {
	var current_list = document.getElementById("key_words_list_"+follow_user).value;
	
	if (current_list == "") {
		alert("You must add at least one key word");
	} else {
		Dajaxice.grain.edit_alert(Dajax.process,{'follow_user':follow_user,'key_words':current_list});
	}
	document.getElementById('edit_'+follow_user).style.display = "inline-block";
	document.getElementById('save_changes_'+follow_user).style.display = "none";
	document.getElementById("key_words_"+follow_user).style.display = "none";
	
}

function remove_word(num,follow_user) {
	Array.prototype.remove = function(from, to) {
	  var rest = this.slice((to || from) + 1 || this.length);
	  this.length = from < 0 ? this.length + from : from;
	  return this.push.apply(this, rest);
	};
	
	var current_list = document.getElementById("key_words_list_"+follow_user).value;
	
	var list = current_list.split(",");
	list.remove(num);
	
	var list_html = "<ul>";
	
	var list_str = "";
	for (i = 0; i < list.length; ++i) {
			list_html = list_html + "<li><a href='javascript:void(0);' onclick='remove_word("+i+",\"" + follow_user + "\")'>" + list[i] + " x</a></li>";
		
		if (i > 0) {
			list_str = list_str + "," + list[i];
		} else {
			list_str = list[i];
		}
	}
	list_html = list_html + "</ul>";
	
	document.getElementById("key_words_display_"+follow_user).innerHTML = list_html;
	document.getElementById("key_words_list_"+follow_user).value = list_str;
}