function add_key_word() {
	var key_word = document.getElementById("key_words").value;
	var current_list = document.getElementById("key_words_list").value;
	
	if (key_word != "") {
		if (current_list != "") {
			current_list = current_list + "," + key_word;
		} else {
			current_list = key_word;
		}
		
		document.getElementById("key_words").value = "";
		document.getElementById("key_words_list").value = current_list;
		
		var list = current_list.split(",");
		var list_html = "<ul>";
		
		for (i = 0; i < list.length; ++i) {
			list_html = list_html + "<li><a href='javascript:void(0);' onclick='remove_word("+i+")'>" + list[i] + " x</a></li>";
		}
		list_html = list_html + "</ul>";
		
		document.getElementById("word_list").innerHTML = list_html;
	}
}

function create() {
	var current_list = document.getElementById("key_words_list").value;
	var follow_user = document.getElementById("follow_user").value;
	
	
	if (follow_user == "" || follow_user == "@") {
		alert("Please enter the screenname of the user, you want to track");
	} else if (current_list == "") {
		alert("You must add at least one key word");
	} else {
		//document.getElementById("addAlertForm").submit();
		Dajaxice.grain.add_alert(Dajax.process,{'follow_user':follow_user,'key_words':current_list});
	}
}

function remove_word(num) {
	Array.prototype.remove = function(from, to) {
	  var rest = this.slice((to || from) + 1 || this.length);
	  this.length = from < 0 ? this.length + from : from;
	  return this.push.apply(this, rest);
	};
	
	var current_list = document.getElementById("key_words_list").value;
	
	var list = current_list.split(",");
	list.remove(num);
	
	var list_html = "<ul>";
	
	var list_str = "";
	for (i = 0; i < list.length; ++i) {
		list_html = list_html + "<li><a href='javascript:void(0);' onclick='remove_word("+i+")'>" + list[i] + " x</a></li>";
		
		if (i > 0) {
			list_str = list_str + "," + list[i];
		} else {
			list_str = list[i];
		}
	}
	list_html = list_html + "</ul>";
	
	document.getElementById("word_list").innerHTML = list_html;
	document.getElementById("key_words_list").value = list_str;
}