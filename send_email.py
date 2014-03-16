import os

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import datetime
from grain.models import Config

def SendEmail(follow_user,tweet_string,profile):

	email_content = """
	<head>
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
	<title>Grained - Tweet Alert</title>
	</head>
	<body>"""
	email_content += '<img src="http://grained.co/static/images/logo.jpg" /></br>'
	email_content += "<h3>@"+follow_user+" just tweeted:</h3>"
	email_content += "<p>"+tweet_string+"</p>"
	email_content += "</br>"
	email_content += '<p>We thought you might be interested.</p>'
	email_content += '<p> - Grained Team</p>'
	email_content += '</body>'

	TO = profile.email
	FROM ='support@grained.co'
	SUBJECT = "Grained - @"+follow_user+" has just tweeted "+tweet_string[0:25]+'...'
	PASS = Config.objects.all().latest('id').support_email_pass
	
	"""With this function we send out our html email"""
	
	# Create message container - the correct MIME type is multipart/alternative here!
	MESSAGE = MIMEMultipart('alternative')
	MESSAGE['subject'] = SUBJECT
	MESSAGE['To'] = TO
	MESSAGE['From'] = "Grained Team"
	MESSAGE.preamble = """
	Your mail reader does not support the report format.
	Please visit us <a href="http://www.grained.co">online</a>!"""
	
	# Record the MIME type text/html.
	HTML_BODY = MIMEText(email_content, 'html')
	
	# Attach parts into message container.
	# According to RFC 2046, the last part of a multipart message, in this case
	# the HTML message, is best and preferred.
	MESSAGE.attach(HTML_BODY)
	
	# The actual sending of the e-mail
	server = smtplib.SMTP('smtp.gmail.com:587')
	
	# Print debugging output when testing
	if __name__ == "__main__":
		server.set_debuglevel(1)
	
	server.starttls()
	server.login(FROM,PASS)
	server.sendmail(FROM, [TO], MESSAGE.as_string())
	server.quit()