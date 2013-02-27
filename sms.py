from flask import flash
import os

twilio_account_sid = os.environ['ggj12_twilio_account_sid']
twilio_auth_token = os.environ['ggj12_twilio_auth_token']

def send_sms(number,message):
	from twilio.rest import TwilioRestClient
	try:
		number = twilio_format_number(number)
		client = TwilioRestClient(twilio_account_sid, twilio_auth_token)
		message = client.sms.messages.create(to=number,
		                                     from_="+15107358741",
		                                     body=message)
	except:
		pass
		flash("error sending message","error")
		
def twilio_format_number(number):
	return "+1"+number