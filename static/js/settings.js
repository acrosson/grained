function update_settings() {
	var email = $('#email:checked').val();
	var sms = $('#sms:checked').val();
	
	if(! email){
		email = 'off';
	}
	if(! sms){
		sms = 'off';
	}
	
	var phone = document.getElementById("phone").value;
	var email_address = document.getElementById("email_address").value;
	
	document.getElementById("status").innerHTML = "";
	Dajaxice.grain.update_settings(Dajax.process,{'email':email,'sms':sms,'phone':phone,'email_address':email_address,'form_type':'settings'});
}
