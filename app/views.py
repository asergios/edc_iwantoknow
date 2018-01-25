from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views import View

import xml.etree.ElementTree as xmlParser
import requests
import app.static.database.BaseXClient.BaseXClient as BaseXClient


# My WolframAlpha API key, please be gentle, max. 2000 requests per month
API_KEY 	= 'JX8868-T9QE9WHQTJ'
API_LINK 	= 'http://api.wolframalpha.com/v2/query?appid=' + API_KEY + '&input='
MONTHS 		= ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

from .forms import *

'''
	Index View 

	'''
class index(View):

	# Response for a GET request
	def get(self, request, *args, **kwargs):
		print(args)
		form = DateForm()
		return render(request,'index.html', { 'formAction': '' , 
											  'form': '',
											  'entries': get_entries()
											})

	# Response for a POST request
	def post(self, request, *args, **kwargs):
		if "pick" in request.POST:
			user_pick = request.POST.get("pick")
			form = self.translate_user_pick(user_pick)
			return render(request,'index.html', {'user_picked': user_pick, 
												 'formAction': form[0], 
												 'form': form[1],
												 'entries': get_entries()
												 })
		else:
			# TODO: this works?
			return self.get()

	# From user_pick get the form actions and fields
	def translate_user_pick(self, user_pick):
		form_action = get_form_action(user_pick)

		if (form_action == "b_day"):
			return (form_action, DateForm())
		else:
			return (form_action, DateForm())


'''
	Answer to "How much time has passed since my birthday"

	'''
def b_day(request):
	if request.POST:
		validate = DateForm(request.POST)
		user_pick = get_user_pick("b_day")
		# if form is valid prepare API call
		if( validate.is_valid() ):
			date = validate.cleaned_data['date']
			month = MONTHS[date.month - 1]
			api_input = str(date.day) + '+' + month + '+' + str(date.year)

			api_answer = api_call(api_input)
			return render(request,'bday.html', {'user_picked': user_pick, 
												 'formAction': "b_day", 
												 'form': validate,
												 'entries': get_entries(),
												 'results' : api_answer
												 })
		# form not valid TODO: error message	
		else:
			return render(request,'index.html', {'user_picked': user_pick, 
												 'formAction': "b_day", 
												 'form': validate,
												 'entries': get_entries()
												 })
	# If the request was a GET (or something not a POST), the user is redirected to index page
	else:
		return redirect('index')



'''
	API CALL Wolframalpha

	'''
def api_call(api_input):
	call = API_LINK + api_input

	'''
	# Commented to save queries
	response = requests.get(call)
	xml_tree = xmlParser.fromstring(response.content)
	'''
	# Sample file, for debbuging
	tree = xmlParser.parse('app/static/database/query.xml')
	root = tree.getroot()

	diff_days = root.findall('./pod[@id=\'DifferenceConversions\']/subpod/plaintext')
	# Converting Sub Elements to Tezt
	diff_days = [d.text for d in diff_days]

	return diff_days


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




