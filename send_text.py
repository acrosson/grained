from nexmomessage import NexmoMessage
from grain.models import Config

def SendText(follow_user,tweet,phone):
	
	print follow_user
	print tweet
	
	message = '@'+follow_user+' just tweeted: '+tweet
	
	api_key = Config.objects.all().latest('id').nexmo_key
	api_secret = Config.objects.all().latest('id').nexmo_secret
	api_num = Config.objects.all().latest('id').nexmo_number
	
	msg = {
	    'reqtype': 'json',
	    'api_key': api_key,
	    'api_secret': api_secret,
	    'from': api_num,
	    'to': '1'+phone,
	    'text': message,
	}
	
	sms = NexmoMessage(msg)
	sms.set_text_info(msg['text'])

	response = sms.send_request()
	
	if response:
		status = response['messages'][0]['status']
		
		if status == '0':
			print 'Text Msg Sent Successfully'
	else:
		print 'Error: Problem sending text'