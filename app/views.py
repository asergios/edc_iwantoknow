from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views import View

import xml.etree.ElementTree as xmlParser
import lxml.etree as xlsTransformer
import requests
import app.static.database.BaseXClient.BaseXClient as BaseXClient
from .forms import *
import time

# My WolframAlpha API key, please be gentle, max. 2000 requests per month
API_KEY 	= 'JX8868-T9QE9WHQTJ'
API_LINK 	= 'http://api.wolframalpha.com/v2/query?appid=' + API_KEY + '&input='
# Months array, used to translate number of month to string
MONTHS 		= ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
# Reddits ATOM link
ATOM_FEED   = 'https://www.reddit.com/r/wolframalpha.xml?limit=20'


'''
	Index View 

	'''
class index(View):

	# Response for a GET request, simply returns index page
	def get(self, request, *args, **kwargs):
		return render(request,'index.html', { 'formAction': '' , 
											  'form': '',
											  'entries': get_entries(),
											  'feed' : get_feed()
											})

	# Response for a POST request, returns index page, now with the form for the user to fill
	def post(self, request, *args, **kwargs):
		if "pick" in request.POST:
			user_pick = request.POST.get("pick")
			action, form = self.translate_user_pick(user_pick)
			return render(request,'index.html', {'user_picked': user_pick, 
												 'formAction': action, 
												 'form': form,
												 'entries': get_entries(),
												 'feed' : get_feed()
												 })
		else:
			# TODO: this works?
			return self.get()

	# From user_pick get the form actions and fields
	def translate_user_pick(self, user_pick):
		# Getting form actiong from DataBase
		form_action = get_form_action(user_pick)
		if (form_action == "b_day"):
			return (form_action, DateForm(initial= {'date': get_most_common(form_action)} ) )
		else:
			return (form_action, InputForm(initial= {'input_form': get_most_common(form_action)} ) )


'''
	Answer to "How much time has passed since my birthday"

	'''
def b_day(request):
	if request.POST:
		# Filling DateForm with request
		validate = DateForm(request.POST)
		# Getting title for "b_day" action
		user_pick = get_user_pick("b_day")

		# If form is valid prepare API call
		if( validate.is_valid() ):
			date = validate.cleaned_data['date']

			# Translating month number to string
			month = MONTHS[date.month - 1]

			api_input = str(date.day) + '+' + month + '+' + str(date.year)
			api_answer, success = api_call(api_input)

			if ( success ):
				# Storing user input on DB
				store_user_input("b_day", date)
				# Finding Pod with "DifferenceConversions" ID
				diff_days = api_answer.findall('./pod[@id=\'DifferenceConversions\']/subpod/plaintext')
				# Converting Sub Elements to Tezt
				diff_days = [d.text for d in diff_days]

				return render(request,'bday.html', {'user_picked': user_pick, 
													 'formAction': "b_day", 
													 'form': validate,
													 'entries': get_entries(),
													 'results' : diff_days
													 })

		# Form not valid / render index where error will be shown
		return render(request,'index.html', {'user_picked': user_pick, 
											 'formAction': "b_day", 
											 'form': validate,
											 'entries': get_entries(),
											 'error' : True,
											 'feed' : get_feed()
											 })
	# If the request was a GET (or something not a POST), the user is redirected to index page
	else:
		return redirect('index')


'''
	Answer to "What time is it in"

	'''
def time_in(request):
	if request.POST:
		# Filling InputForm with request
		validate = InputForm(request.POST)
		# Getting title for "time_in" action
		user_pick = get_user_pick("time_in")

		# If form is valid prepare API call
		if( validate.is_valid() ):
			api_input = "time in " + validate.cleaned_data['input_form']
			api_answer, success = api_call(api_input)

			if ( success ):
				# Storing user input on DB
				store_user_input("time_in", validate.cleaned_data['input_form'])
				# Getting hours in locatin and timeoffset from current location
				hours_in_location = api_answer.findtext('./pod[@id=\'Result\']/subpod/plaintext')
				time_offset = api_answer.findtext('./pod[@id=\'TimeOffsets\']/subpod/plaintext')

				return render(request,'time_in.html', {'user_picked': user_pick, 
													 'formAction': "time_in", 
													 'form': validate,
													 'entries': get_entries(),
													 'hour' : hours_in_location,
													 'offset': time_offset
													 })

		# Form not valid - render index (later will error message)
		return render(request,'index.html', {'user_picked': user_pick, 
											 'formAction': "time_in", 
											 'form': validate,
											 'entries': get_entries(),
											 'error' : True,
											 'feed' : get_feed()
											 })
	# If the request was a GET (or something not a POST), the user is redirected to index page
	else:
		return redirect('index')


'''
	About Page

	'''
def about(request):
	return render(request,'about.html')


'''
	API CALL Wolframalpha

	'''
def api_call(api_input):
	call = API_LINK + api_input
	debbuging = 1


	if(debbuging):
		tree = xmlParser.parse('app/static/database/failure_example.xml')
		tree = tree.getroot()
		success = tree.find('.[@success]').attrib['success']
	else:
		response = requests.get(call)
		tree = xmlParser.fromstring(response.content)
		success = tree.find('.[@success]').attrib['success']

	success = False if success == 'false' else True
	
	return tree, success


'''
	BaseX FUNCTIONS

	'''	

# return db session (TODO: in case of failure)
def get_db_session():
	try:
		return BaseXClient.Session('localhost', 1984, 'admin', 'admin')
	except:
		pass

# returns every entry found on DB
def get_entries():
	session = get_db_session()

	# Building Query to get entries titles
	query = "for $i in collection('entries')//entrie" \
			" let $title :=$i/title/text()" \
			" return $title"

	# Executing Query
	result = session.query(query)
	# Transfer titles to a list
	list_entries = [item for code, item in result.iter()]

	if session:
		session.close()

	return list_entries

# given an user_pick, returns the form action
def get_form_action(user_pick):
	session = get_db_session()

	# Building Query to form action
	query = "for $i in collection('entries')//entrie" \
			" where $i/title = \"" + user_pick + "\"" +\
			" return $i/action/text()"

	# Executing Query
	result = session.query(query)

	# Getting Action
	action = [action for code, action in result.iter()]

	if session:
		session.close()

	return action[0]


# given a form_action, returns the user_pick
def get_user_pick(form_action):
	session = get_db_session()

	# Building Query to form action
	query = "for $i in collection('entries')//entrie" \
			" where $i/action = \"" + form_action + "\"" +\
			" return $i/title/text()"

	# Executing Query
	result = session.query(query)

	# Getting title
	title = [title for code, title in result.iter()]

	if session:
		session.close()

	return title[0]

def store_user_input(action, user_input):
	session = get_db_session()

	# Location of user_inputs for this action
	location = "collection(\"entries\")//entrie/action[text()=\""+ action +"\"]/../user_inputs"
	# Condition to check if input already exists
	exists = "(exists(" + location + "/user_input[text()=\""+ user_input +"\"]))"
	# If already exists it will increments his 'times' value, else will create a new user_input
	query = " if " + exists + " then " \
			"(replace value of node (" + location + "/user_input[text()=\""+ user_input +"\"]/@times) with (" + location + "/user_input[text()=\""+ user_input +"\"]/data(@times)) + 1) else " \
			"(insert node (<user_input times=\"1\">" + user_input + "</user_input>) into  " + location + " )"
	
	result = session.query(query)
	
	if session:
		session.close()

def get_most_common(action):
	session = get_db_session()

	# Location of user_inputs of this action
	inputs = "collection('entries')//entrie/action[text()=\""+ action +"\"]/../user_inputs/user_input"
	# Ordering by times descending and returning first
	query =  "(for $i in " + inputs + \
			 " order by $i/data(@times) descending " \
			 "return $i/text())[1]"

	result = session.query(query)
	common = [common for code, common in result.iter()]

	if session:
		session.close()

	return common[0]

'''
	Reddit's ATOM feed

	'''	

def get_feed():
	# Request Feed
	response = requests.get(ATOM_FEED)

	# If answer was 200, it saves the file and returns the transformed feed
	if(response.status_code == 200):
		with open('app/static/feed_reddit/last_feed.xml', mode='wb') as newfile:
			newfile.write(response.content)
			newfile.close()
		return transform_feed( xlsTransformer.fromstring(response.content) )

	# Reddit answer with 429 when it is feeling spammed, in that case return the last feed saved
	elif(response.status_code == 429):
		return transform_feed( xlsTransformer.parse('app/static/feed_reddit/last_feed.xml') )

	return False

def transform_feed(feed):
	# Using feed_transform.xsl to feed, turns it to a HTML list
	xsl = xlsTransformer.parse('app/static/feed_reddit/feed_transform.xsl')
	transform = xlsTransformer.XSLT(xsl)
	html_content = transform(feed)
	return html_content



