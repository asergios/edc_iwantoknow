from SPARQLWrapper import SPARQLWrapper, JSON
from wikidata.client import Client

try:
	client = Client()
	sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
except Exception as e:
	print(e)
	print("ERROR: I had trouble connection to Wikidata")


'''
	image -> 'P18'
	instance_of -> "P31"
	human -> "Q5"
	givenname -> "Q202444"  
	human settlement -> "Q486972"
'''

def get_person_pic(name_of_person):
	name_of_person = name_of_person.strip()

	query = """
			SELECT ?pic ?description
			WHERE
			{
				?item wdt:P31 wd:Q5 .
			    ?item ?something \""""+name_of_person+"""\"
				OPTIONAL {
					?item wdt:P18 ?pic .
					?item schema:description ?description .
        			FILTER (LANG(?description) = "en") 
				}
				SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en" }
			}
	"""

	sparql.setQuery(query)
	sparql.setReturnFormat(JSON)
	result = sparql.query().convert()['results']['bindings']

	if( len(result) > 0 ):
		pic = result[0]['pic']['value'] if 'pic' in result[0] else "../static/images/not_available.jpg"
		description = result[0]['description']['value'] if 'description'in result[0] else ""
		return (pic, description)

def get_pic_location(location):
	location = location.strip()

	query = """
		SELECT ?pic 
		WHERE {
			  ?item wdt:P31/wdt:P279* wd:Q486972.
			  ?item ?something \""""+location+"""\".
			  OPTIONAL { ?item wdt:P18 ?pic. }
			}
	"""

	sparql.setQuery(query)
	sparql.setReturnFormat(JSON)
	result = sparql.query().convert()['results']['bindings']

	if( len(result) > 0 ):
		pic = result[0]['pic']['value'] if 'pic' in result[0] else "../static/images/not_available.jpg"
		return pic
