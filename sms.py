from flask import flash
import os

twilio_account_sid = os.environ['ggj12_twilio_account_sid']
twilio_auth_token = os.environ['ggj12_twilio_auth_token']

def send_sms(number,message):
	from twilio.rest import TwilioRestClient
	try:
		flash("sending '"+message+"' to "+number)
		client = TwilioRestClient(twilio_account_sid, twilio_auth_token)
		message = client.sms.messages.create(to=number,
		                                     from_="+14157023723",
		                                     body=message)
	except:
		pass
		flash("error sending message")