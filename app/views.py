from django.shortcuts import render, redirect
from django.http import HttpResponse, FileResponse
from django.views import View

import xml.etree.ElementTree as xmlParser
import lxml.etree as eTree
import requests
import app.static.database.BaseXClient.BaseXClient as BaseXClient
from .forms import *
import time

# My WolframAlpha API key, please be gentle, max. 2000 requests per month
USE_API 	=  False # Set to False when debbuging, in order to don't spend queries
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
		if (form_action == "b_day" or form_action == "was_born"):
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
			api_answer, success = api_call(api_input, get_schema_parser('b_day'))

			if ( success ):
				# Storing user input on DB
				store_user_input("b_day", date.strftime("%d-%m-%Y"))
				# Transforming XML into HTML
				results = transform(api_answer, "b_day")
				# Rendering
				return render(request,'results.html', {'user_picked': user_pick, 
													 'formAction': "b_day", 
													 'form': validate,
													 'entries': get_entries(),
													 'results' : results
													 })

		# Form not valid / render index where error will be shown
		return render_index(request, user_pick, "b_day", validate, True)

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
			api_answer, success = api_call(api_input, get_schema_parser('time_in'))

			if ( success ):
				# Storing user input on DB
				store_user_input("time_in", validate.cleaned_data['input_form'])
				# Transforming XML into HTML
				results = transform(api_answer, "time_in")

				return render(request,'results.html', {'user_picked': user_pick, 
													 'formAction': "time_in", 
													 'form': validate,
													 'entries': get_entries(),
													 'results' : results
													 })

		# Form not valid - render index
		return render_index(request, user_pick, "time_in", validate, True)

	# If the request was a GET (or something not a POST), the user is redirected to index page
	else:
		return redirect('index')


'''
	Answer to "Who was born in"

	'''
def was_born(request):
	if request.POST:
		# Filling InputForm with request
		validate = DateForm(request.POST)
		# Getting title for "was_born" action
		user_pick = get_user_pick("was_born")

		# If form is valid prepare API call
		if( validate.is_valid() ):
			date = validate.cleaned_data['date']

			# Translating month number to string
			month = MONTHS[date.month - 1]

			api_input = "people born in " + month + ' ' + str(date.day) + ' ' + str(date.year)
			api_answer, success = api_call(api_input, get_schema_parser('was_born'))

			if ( success ):
				# Storing user input on DB
				store_user_input("was_born", date.strftime("%d-%m-%Y"))

				# Getting result
				result = api_answer.findtext('./pod[@id=\'Result\']/subpod/plaintext')
				result = result.split('|')
				result[-1] = result[-1].split('(total')[0]

				return render(request,'was_born.html', {'user_picked': user_pick, 
													 'formAction': "was_born", 
													 'form': validate,
													 'entries': get_entries(),
													 'results' : result
													 })

		# Form not valid - render index
		return render_index(request, user_pick, "was_born", validate, True)

	# If the request was a GET (or something not a POST), the user is redirected to index page
	else:
		return redirect('index')


'''
	Answer to "How many calories on"

	'''
def calories_on(request):
	if request.POST:
		# Filling InputForm with request
		validate = InputForm(request.POST)
		# Getting title for "calories_on" action
		user_pick = get_user_pick("calories_on")

		# If form is valid prepare API call
		if( validate.is_valid() ):
			api_input = "calories on " + validate.cleaned_data['input_form']
			api_answer, success = api_call(api_input, get_schema_parser('calories_on'))

			if ( success ):
				# Storing user input on DB
				store_user_input("calories_on", validate.cleaned_data['input_form'])
				# Transforming XML into HTML
				results = transform(api_answer, "calories_on")

				return render(request,'results.html', {'user_picked': user_pick, 
													 'formAction': "calories_on", 
													 'form': validate,
													 'entries': get_entries(),
													 'results' : results
													 })

		# Form not valid - render index
		return render_index(request, user_pick, "calories_on", validate, True)

	# If the request was a GET (or something not a POST), the user is redirected to index page
	else:
		return redirect('index')


'''
	Answer to "Biggest in the world"

	'''
def weather(request):
	if request.POST:
		# Filling InputForm with request
		validate = InputForm(request.POST)
		# Getting title for "weather" action
		user_pick = get_user_pick("weather")

		# If form is valid prepare API call
		if( validate.is_valid() ):
			api_input = "weather in" + validate.cleaned_data['input_form']
			api_answer, success = api_call(api_input, get_schema_parser('weather'))

			if ( success ):
				# Storing user input on DB
				store_user_input("weather", validate.cleaned_data['input_form'])
				# Transforming XML into HTML
				results = transform(api_answer, "weather")

				return render(request,'results.html', {'user_picked': user_pick, 
													 'formAction': "weather", 
													 'form': validate,
													 'entries': get_entries(),
													 'results' : results
													 })

		# Form not valid - render index
		return render_index(request, user_pick, "weather", validate, True)

	# If the request was a GET (or something not a POST), the user is redirected to index page
	else:
		return redirect('index')


def render_index(request, user_picked, formAction, form, error):
	return render(request,'index.html', {	 'user_picked': user_picked, 
											 'formAction':  formAction, 
											 'form': 		form,
											 'entries': 	get_entries(),
											 'error' : 		error,
											 'feed' : 		get_feed()
											 })


'''
	About Page

	'''
def about(request):
	return render(request,'about.html')


'''
	Report Page

	'''
def report(request):
	return FileResponse(open('app/static/EDC_report_tp1.pdf', 'rb'), content_type='application/pdf')



'''
	API CALL Wolframalpha

	'''
def api_call(api_input, parser):
	call = API_LINK + api_input
	try:
		if(not USE_API):
			tree = xmlParser.parse('app/static/debug_samples/query_sample.xml',parser)
			tree = tree.getroot()
		else:
			response = requests.get(call)
			tree = xmlParser.fromstring(response.content, parser)
		
		return tree, True

	# If Schema fails on validation
	except Exception as e:
		print(e)
		return None, False

# Returns parser for XML schema validation
def get_schema_parser(action):
	schema_root = eTree.parse('app/static/schemas/' + action + '.xsd')
	xsd_file = eTree.XMLSchema(schema_root)
	parser = eTree.XMLParser(schema = xsd_file)
	return parser


'''
	BaseX FUNCTIONS

	'''	

# return db session
def get_db_session():
	try:
		return BaseXClient.Session('127.0.0.1', 1984, 'admin', 'admin')
	except Exception as e:
		print( e )
		print('I was unable to connect to DataBase. Is BaseXServer running? You should have a DataBase called "entries".')
		return False

# returns every entry found on DB
def get_entries():
	session = get_db_session()

	if session:
		# Building Query to get entries titles
		query = "for $i in collection('entries')//entrie" \
				" let $title :=$i/title/text()" \
				" return $title"

		# Executing Query
		result = session.query(query)
		# Transfer titles to a list
		list_entries = [item for code, item in result.iter()]

		session.close()
	else:
		return ["ERROR: I wasn't able to connect to BaseX, please check log"]

	return list_entries

# given an user_pick, returns the form action
def get_form_action(user_pick):
	session = get_db_session()

	if session:
		# Building Query to form action
		query = "for $i in collection('entries')//entrie" \
				" where $i/title = \"" + user_pick + "\"" +\
				" return $i/action/text()"

		# Executing Query
		result = session.query(query)

		# Getting Action
		action = [action for code, action in result.iter()]

		session.close()
	else:
		return "db_error"

	return action[0]


# given a form_action, returns the user_pick
def get_user_pick(form_action):
	session = get_db_session()

	if session:
		# Building Query to form action
		query = "for $i in collection('entries')//entrie" \
				" where $i/action = \"" + form_action + "\"" +\
				" return $i/title/text()"

		# Executing Query
		result = session.query(query)

		# Getting title
		title = [title for code, title in result.iter()]

		session.close()
	else:
		return "db_error"

	return title[0]

def store_user_input(action, user_input):
	session = get_db_session()

	if session:
		# Location of user_inputs for this action
		location = "collection('entries')//entrie/action[text()=\""+ action +"\"]/../user_inputs"
		# Condition to check if input already exists
		exists = "(exists(" + location + "/user_input[text()=\""+ user_input +"\"]))"
		# If already exists it will increments his 'times' value, else will create a new user_input
		query = "xquery if " + exists + " then " \
				"(replace value of node (" + location + "/user_input[text()=\""+ user_input +"\"]/@times) with (" + location + "/user_input[text()=\""+ user_input +"\"]/data(@times)) + 1) else " \
				"(insert node (<user_input times=\"1\">" + user_input + "</user_input>) into  " + location + " )"
		
		result = session.execute(query)
		
		session.close()

def get_most_common(action):
	session = get_db_session()

	if session:
		# Location of user_inputs of this action
		inputs = "collection('entries')//entrie/action[text()=\""+ action +"\"]/../user_inputs/user_input"
		# Ordering by times descending and returning first
		query =  "(for $i in " + inputs + \
				 " order by $i/data(@times) descending " \
				 "return $i/text())[1]"

		result = session.query(query)
		common = [common for code, common in result.iter()]


		session.close()
	else:
		return "db_error"

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
		return transform( eTree.fromstring(response.content), 'feed')

	# Reddit answer with 429 (Too Many Requests) when it is feeling spammed, in that case return the last feed saved
	elif(response.status_code == 429):
		return transform( eTree.parse('app/static/feed_reddit/last_feed.xml'), 'feed' )

	return False

def transform(xml, xsl_file):
	xsl = eTree.parse('app/static/transform/'+ xsl_file +'.xsl')
	transform = eTree.XSLT(xsl)
	html_content = transform(xml)
	return html_content



