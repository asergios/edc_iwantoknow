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
'''

def get_person_pic(name_of_person):
	name_of_person = name_of_person.strip()

	query = """
			SELECT ?pic
			WHERE
			{
				?item wdt:P31 wd:Q5 .
			    ?item ?something \""""+name_of_person+"""\"
				OPTIONAL {
					?item wdt:P18 ?pic
				}
				SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en" }
			}
	"""

	sparql.setQuery(query)
	sparql.setReturnFormat(JSON)
	result = sparql.query().convert()['results']['bindings']

	if( len(result) > 0 ):
		pic = result[0]['pic']['value']
		return pic


