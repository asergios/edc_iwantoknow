from django.shortcuts import render, redirect
from django.http import HttpResponse, FileResponse
from django.views import View

import xml.etree.ElementTree as xmlParser
import lxml.etree as eTree
import requests
from .forms import *
import time
import datetime


from app import graphDB as db

# My WolframAlpha API key, please be gentle, max. 2000 requests per month
USE_API 	=  True # Set to False when debbuging, in order to don't queries
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
											  'entries': db.get_entries(),
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
												 'entries': db.get_entries(),
												 'feed' : get_feed()
												 })
		else:
			# TODO: this works?
			return self.get()

	# From user_pick get the form actions and fields
	def translate_user_pick(self, user_pick):
		# Getting form actiong from DataBase
		form_action = db.get_form_action(user_pick)
		if (form_action == "b_day" or form_action == "was_born"):
			return (form_action, DateForm(initial= {'date': db.get_most_common(form_action)} ) )
		else:
			return (form_action, InputForm(initial= {'input_form': db.get_most_common(form_action)} ) )


'''
	Answer to "How much time has passed since my birthday"

	'''
def b_day(request):
	if request.POST:
		# Filling DateForm with request
		validate = DateForm(request.POST)
		# Getting title for "b_day" action
		user_pick = db.get_user_pick("b_day")

		# If form is valid
		if( validate.is_valid() ):
			date = validate.cleaned_data['date']
			success = True

			# If a valide result already exists
			if( db.exists_result(date.strftime("%d-%m-%Y"), "b_day") ):
				diff_days = db.get_result(date.strftime("%d-%m-%Y"), "b_day", "DifferenceConversions")

			# Else use API to generate new one and then store it
			else:
				# Translating month number to string
				month = MONTHS[date.month - 1]
				api_input = str(date.day) + '+' + month + '+' + str(date.year)
				api_answer, success = api_call(api_input, get_schema_parser('b_day'))
				if (success):
					# Getting DifferenceConversions with the results we want
					diff_days = api_answer.findall('./pod[@id=\'DifferenceConversions\']/subpod/plaintext')
					diff_days = [d.text for d in diff_days]
					seconds_to_midnight = (24 - datetime.datetime.now().hour) * 60
					db.store_result(diff_days, "b_day", date.strftime("%d-%m-%Y"), "DifferenceConversions", seconds_to_midnight)

			if ( success ):
				# Storing user input on DB
				db.store_user_input("b_day", date.strftime("%d-%m-%Y"))
				
				# Rendering
				return render(request,'b_day.html', {'user_picked': user_pick, 
													 'formAction': "b_day", 
													 'form': validate,
													 'entries': db.get_entries(),
													 'results' : diff_days
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
		user_pick = db.get_user_pick("time_in")

		# If form is valid prepare API call
		if( validate.is_valid() ):
			user_input = validate.cleaned_data['input_form']
			success = True

			# If a valide result already exists
			if( db.exists_result( user_input, "time_in") ):
				hours_in_location = db.get_result( user_input, "time_in", "Result")[0]
				time_offset = db.get_result( user_input, "time_in", "TimeOffsets")[0]
			else:
				api_input = "time in " + user_input
				api_answer, success = api_call(api_input, get_schema_parser('time_in'))
				if (success):
					hours_in_location = api_answer.findtext('./pod[@id=\'Result\']/subpod/plaintext')
					time_offset = api_answer.findtext('./pod[@id=\'TimeOffsets\']/subpod/plaintext')
					time_offset = "+0" if time_offset is None else time_offset
					db.store_result([hours_in_location], "time_in",  user_input, "Result", 30)
					db.store_result([time_offset], "time_in", user_input, "TimeOffsets", 30)

			if ( success ):
				# Storing user input on DB
				db.store_user_input("time_in", user_input)

				return render(request,'time_in.html', {'user_picked': user_pick, 
													 'formAction': "time_in", 
													 'form': validate,
													 'entries': db.get_entries(),
													 'hour' : hours_in_location,
													 'offset' : time_offset
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
		user_pick = db.get_user_pick("was_born")

		# If form is valid prepare API call
		if( validate.is_valid() ):
			date = validate.cleaned_data['date']
			user_input = date.strftime("%d-%m-%Y")
			success = True

			# If a valide result already exists
			if( db.exists_result(user_input, "was_born") ):
				result = db.get_result(user_input, "was_born", "Result")

			# Else use API to generate new one and then store it
			else:
				# Translating month number to string
				month = MONTHS[date.month - 1]
				api_input = "people born in " + month + ' ' + str(date.day) + ' ' + str(date.year)
				api_answer, success = api_call(api_input, get_schema_parser('was_born'))
				if (success):
					# Getting result
					result = api_answer.findtext('./pod[@id=\'Result\']/subpod/plaintext')
					result = result.split('|')
					result[-1] = result[-1].split('(total')[0]
					db.store_result(result, "was_born",  user_input, "Result", 604800)


			if ( success ):
				# Storing user input on DB
				db.store_user_input("was_born", user_input)

				return render(request,'was_born.html', {'user_picked': user_pick, 
													 'formAction': "was_born", 
													 'form': validate,
													 'entries': db.get_entries(),
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
		user_pick = db.get_user_pick("calories_on")

		# If form is valid prepare API call
		if( validate.is_valid() ):
			user_input = validate.cleaned_data['input_form']
			success = True

			# If a valide result already exists
			if( db.exists_result( user_input, "calories_on") ):
				calories = db.get_result( user_input, "calories_on", "Result")[0]
				rdf = db.get_result( user_input, "calories_on", "RDVPod")[0]
			else:
				api_input = "calories on " + validate.cleaned_data['input_form']
				api_answer, success = api_call(api_input, get_schema_parser('calories_on'))
				if ( success ):
					calories = api_answer.findtext('./pod[@id=\'Result\']/subpod/plaintext')
					rdf = api_answer.findtext('./pod[@id=\'RDVPod:Calories:ExpandedFoodData\']/subpod/plaintext').split("|", 3)[-1].replace("\n"," ")
					db.store_result([calories], "calories_on",  user_input, "Result", 604800)
					db.store_result([rdf], "calories_on",  user_input, "RDVPod", 604800)

			if ( success ):
				# Storing user input on DB
				db.store_user_input("calories_on", validate.cleaned_data['input_form'])

				return render(request,'calories_on.html', {'user_picked': user_pick, 
														 'formAction': "calories_on", 
														 'form': validate,
														 'entries': db.get_entries(),
														 'calories' : calories,
														 'rdf' : rdf
														 })

		# Form not valid - render index
		return render_index(request, user_pick, "calories_on", validate, True)

	# If the request was a GET (or something not a POST), the user is redirected to index page
	else:
		return redirect('index')


'''
	Answer to "Hows the weather in"

	'''
def weather(request):
	if request.POST:
		# Filling InputForm with request
		validate = InputForm(request.POST)
		# Getting title for "weather" action
		user_pick = db.get_user_pick("weather")

		# If form is valid prepare API call
		if( validate.is_valid() ):
			user_input = validate.cleaned_data['input_form']
			success = True

			# If a valide result already exists
			if( db.exists_result( user_input, "weather") ):
				result = db.get_result( user_input, "weather", "WeatherForecast")[0]
			else:
				api_input = "weather in " + user_input
				api_answer, success = api_call(api_input, get_schema_parser('weather'))
				if ( success ):
					result = api_answer.findtext('./pod[@id=\'WeatherForecast:WeatherData\']/subpod/plaintext').replace("\n"," ")
					db.store_result([result], "weather",  user_input, "WeatherForecast", 900)

			if ( success ):
				# Storing user input on DB
				db.store_user_input("weather", validate.cleaned_data['input_form'])

				result = result.split("|")[0]

				return render(request,'weather.html', {'user_picked': user_pick, 
													 'formAction': "weather", 
													 'form': validate,
													 'entries': db.get_entries(),
													 'result' : result
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
											 'entries': 	db.get_entries(),
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
	return FileResponse(open('app/static/EDC_report_tp2.pdf', 'rb'), content_type='application/pdf')



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



