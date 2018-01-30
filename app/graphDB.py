import json
from s4api.graphdb_api import GraphDBApi
from s4api.swagger import ApiClient
import time

endpoint = "http://localhost:7200"
repository = "entries"

try:
	client = ApiClient(endpoint=endpoint)
	accessor = GraphDBApi(client)
except Exception as e:
	print(e)
	print("ERROR: I had trouble connecting to GraphDB!")



# Returns list of entries on db
def get_entries():
	query = """
        PREFIX pred: <http://www.entries.com/pred/>
		SELECT ?title
		WHERE {
		    ?some_entrie pred:title ?title
		}
	"""

	query = {"query": query}
	result = accessor.sparql_select(body=query,repo_name=repository)
	result = json.loads(result)['results']['bindings']

	entries = [title['title']['value'] for title in result]

	return entries


# Given an user_pick, returns the form action
def get_form_action(user_pick):
	query = """
        PREFIX pred: <http://www.entries.com/pred/>
		SELECT ?action
		WHERE {
		    ?d pred:title \"""" + user_pick + """\".
		    ?d pred:action ?action
		}
	"""

	query = {"query": query}
	result = accessor.sparql_select(body=query,repo_name=repository)
	result = json.loads(result)['results']['bindings']

	action = result[0]['action']['value']

	return action


# Given a form_action, returns the user_pick
def get_user_pick(form_action):
	query = """
        PREFIX pred: <http://www.entries.com/pred/>
		SELECT ?user_pick
		WHERE {
		    ?d pred:action \"""" + form_action + """\".
		    ?d pred:title ?user_pick
		}
	"""

	query = {"query": query}
	result = accessor.sparql_select(body=query,repo_name=repository)
	result = json.loads(result)['results']['bindings']
	title = result[0]['user_pick']['value']

	return title

# If inputs exists, increments times else creates new input
def store_user_input(action, user_input):
	user_input = user_input.replace(" ", "_")
	exists = check_if_exists(action, user_input)

	if(exists):
		current_value = get_current_value(action, user_input)
		update_times(action, user_input, current_value + 1)
	else:
		add_input(action, user_input)

# Adding new input
def add_input(action, user_input):
	query = """
        PREFIX pred: <http://www.entries.com/pred/>
        PREFIX user_inputs: <http://www.entries.com/user_inputs/>
		PREFIX input: <http://www.entries.com/user_inputs/"""+action+"""/"""+user_input+""">
		PREFIX result: <http://www.entries.com/result/"""+action+"""/"""+user_input+""">

		INSERT DATA{
		    user_inputs:"""+action+""" pred:user_input input:.
		    input: pred:input \""""+user_input+"""\".
		    input: pred:times "1".
		    input: pred:result result:
		}
	"""

	query = {"update": query}
	result = accessor.sparql_update(body=query,repo_name=repository)

# Update times value
def update_times(action, user_input, value):
	query = """
        PREFIX pred: <http://www.entries.com/pred/>

		DELETE{ 
		    $c pred:times $oldtimes
		 }
		INSERT{  
		    $c pred:times \""""+str(value)+"""\"
		}
		WHERE{ 
		    $d pred:action \""""+action+"""\".
		    $d pred:user_inputs $user_input.
		    $user_input pred:user_input $c.
		    $c pred:input \""""+user_input+"""\".
    		$c pred:times $oldtimes.
		}
	"""

	query = {"update": query}
	result = accessor.sparql_update(body=query,repo_name=repository)

# Get current times value
def get_current_value(action, user_input):
	query = """
        PREFIX pred: <http://www.entries.com/pred/>

		SELECT ?times
		WHERE{
		    $d pred:action \""""+action+"""\".
		    $d pred:user_inputs $user_input.
		    $user_input pred:user_input $c.
		    $c pred:input \""""+user_input+"""\".
		    $c pred:times ?times
		}
	"""

	query = {"query": query}
	result = accessor.sparql_select(body=query,repo_name=repository)
	result = json.loads(result)['results']['bindings']

	times = result[0]['times']['value']
	return int(times)

# Check if input exists
def check_if_exists(action, user_input):
	query = """
        PREFIX pred: <http://www.entries.com/pred/>

		ASK{
			$d pred:action \""""+action+"""\".
		    $d pred:user_inputs $user_input.
		    $user_input pred:user_input $c.
		    $c pred:input \""""+user_input+"""\"
		}
	"""

	query = {"query": query}
	result = accessor.sparql_select(body=query,repo_name=repository)
	result = json.loads(result)['boolean']
	return result

# Get most common input for given action
def get_most_common(action):
	query = """
        PREFIX pred: <http://www.entries.com/pred/>
		PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
		SELECT ?user_inputs
		WHERE {
		    ?d pred:action \""""+action+"""\".
		    ?d pred:user_inputs ?b.
		    ?b pred:user_input ?c.
		    ?c pred:input ?user_inputs.
		    ?c pred:times ?times
		}
		ORDER BY DESC(xsd:nonNegativeInteger(?times))
	"""

	query = {"query": query}
	result = accessor.sparql_select(body=query,repo_name=repository)
	result = json.loads(result)['results']['bindings']
	common = result[0]['user_inputs']['value']

	return common

# Get result from given user_input
def get_result(user_input, action, pod_name):
	user_input = user_input.replace(" ", "_")

	query = """
        PREFIX pred: <http://www.entries.com/pred/>
		PREFIX input: <http://www.entries.com/input/>

		SELECT ?content
		WHERE{
			$d pred:action \""""+action+"""\".
			$d pred:user_inputs $user_input.
			$user_input pred:user_input $c.
			$c pred:input \""""+user_input+"""\".
		    $c pred:result ?result.
		    ?result pred:has_pod ?pod.
		    $pod pred:id \""""+pod_name+"""\".
		    ?pod pred:content ?content.
		}
	"""

	query = {"query": query}
	result = accessor.sparql_select(body=query,repo_name=repository)
	result = json.loads(result)['results']['bindings']

	results = [r['content']['value'] for r in result]
	return results

# Return boolean representing if there is a valid result for given input
def exists_result(user_input, action):
	user_input = user_input.replace(" ", "_")

	query = """
        PREFIX pred: <http://www.entries.com/pred/>

		ASK{
			$d pred:action \""""+action+"""\".
		    $d pred:user_inputs $user_input.
		    $user_input pred:user_input $c.
		    $c pred:input \""""+ user_input +"""\".
		    $c pred:result $r.
		    $r pred:has_pod $p.
		    $r pred:expires $timestamp.
		    FILTER($timestamp > """+ str(int(time.time())) +""")
		}
	"""

	query = {"query": query}
	result = accessor.sparql_select(body=query,repo_name=repository)
	result = json.loads(result)['boolean']
	return result


# Store result into db
def store_result(results, action, user_input, pod_name, time_to_expirate):
	user_input = user_input.replace(" ", "_")

	delete_old_result(action, user_input, pod_name)

	expires_in = int(time.time()) + time_to_expirate

	query = """
        PREFIX pred: <http://www.entries.com/pred/>
		PREFIX pod: <http://www.entries.com/pod/"""+action+"""/"""+user_input+"""/"""+pod_name+""">

		INSERT{ $r pred:has_pod pod:.
				pod: pred:id \""""+pod_name+"""\".
				$r pred:expires """+str(expires_in)+""".
				"""

	for result in results:
		query += """ pod: pred:content \"""" + result + """\". """
	
	query2 = """}
		WHERE { 
		    $d pred:action \""""+ action +"""\".
			$d pred:user_inputs $user_input.
			$user_input pred:user_input $c.
			$c pred:input \""""+ user_input +"""\".
		    $c pred:result $r.
		}
	"""

	query += query2
	query = {"update": query}
	result = accessor.sparql_update(body=query,repo_name=repository)


# Delete old result no longer valid
def delete_old_result(action, user_input, pod_name):
	query = """
        PREFIX pred: <http://www.entries.com/pred/>
		PREFIX pod: <http://www.entries.com/pod/"""+action+"""/"""+user_input+"""/"""+pod_name+""">

		DELETE{
		    $r pred:has_pod pod:.
		    $r pred:expires ?e.
		    pod: $somethingpred $somethingobj
		}
		WHERE { 
		    $r pred:has_pod pod:.
		    $r pred:expires ?e.
		    pod: $somethingpred $somethingobj
		}
	"""

	query = {"update": query}
	result = accessor.sparql_update(body=query,repo_name=repository)