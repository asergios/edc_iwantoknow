from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views import View


import app.static.database.BaseXClient.BaseXClient as BaseXClient


# My WolframAlpha API key, please be gentle, max. 2000 requests per month
API_KEY = 'JX8868-T9QE9WHQTJ'
API_LINK = 'http://api.wolframalpha.com/v2/query?appid=' + API_KEY + '&input='

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
		if( validate.is_valid() ):
			date = validate.cleaned_data['date']
		else:
			return redirect('index', error = 'Invalid Date Format')
	# If the request was a GET (or something not a POST), the user is redirected to index page
	else:
		return redirect('index')



'''
	API CALL Wolframalpha

	'''
def api_call(input):
	pass


'''
	BaseX FUNCTIONS

	'''	

# return db session (TODO: in case of failure)
def get_db_session():
	try:
		return BaseXClient.Session('localhost', 1984, 'admin', 'admin')
	except:
		pass


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



