import rdflib
from flask import Flask

endpoints = {
'film': 
    { 'endpoint':   'film',
      'rdftype':    rdflib.URIRef('http://dbpedia.org/ontology/Film'),
      'update':     'false',
      'attributes': [{
          'predicate': rdflib.URIRef('http://dbpedia.org/property/name'),
          'name':       'title',
          },{
          'predicate': rdflib.URIRef('http://dbpedia.org/property/runtime'),
          'name':       'runtime'
          },{
          'predicate': rdflib.URIRef('http://dbpedia.org/property/gross'),
          'name':       'gross'
          },{
          'predicate': rdflib.URIRef('http://dbpedia.org/ontology/starring'),
          'name':       'starring'
          },{
          'predicate': rdflib.URIRef('http://purl.org/dc/terms/subject'),
          'name':       'subject'
      }]
  }
}

sparql_endpoint = 'http://dbpedia.org/sparql'

graph = rdflib.ConjunctiveGraph('SPARQLStore')
graph.open(sparql_endpoint)

app = Flask(__name__)

exploration_query = """
select ?entity where {{
    ?entity rdf:type {} .
}}"""

attribute_query = "select {} where {{ {} }}"

def list_compactor(input_list):
    if len(input_list) == 0:
        return input_list
    compacted_dict = {}
    for key in input_list[0].keys():
        s = set()
        for d in input_list:
            s.add(d[key])
        if len(s) == 1:
            compacted_dict[key] = s.pop()
        else:
            compacted_dict[key] = list(s)
    return compacted_dict


def query_explore(entity):
    query = graph.query(exploration_query.format(endpoints[entity]['rdftype'].n3()))
    entities = []
    for e in query.bindings:
        print(e)
        entities.append(e[rdflib.term.Variable('entity')])
    return entities
    
def get_attributes(entity, uri):
    bindings = []
    internal = []
    for attribute in endpoints[entity]['attributes']:
        bindings.append("?{}".format(attribute['name']))
        internal.append("<{}> {} ?{} .".format(uri,
            attribute['predicate'].n3(),
            attribute['name']))
    query_string = attribute_query.format(' '.join(bindings), ' '.join(internal))
    print(query_string)
    query = graph.query(query_string)
    query_results = []
    for q in query.bindings:
        result = {}
        for attribute in endpoints[entity]['attributes']:
            result[attribute['name']] = q[rdflib.term.Variable(attribute['name'])].encode()
        query_results.append(result)
    return list_compactor(query_results)

def create_url(entity, uri):
    url = "/rest/{}/{}".format(entity, uri.encode())
    link = '<a href="{}">{}</a>'.format(url, uri.encode())
    return link


@app.route('/rest/<endpoint>/')
def list_all(endpoint=None):
    if endpoint in endpoints.keys():
        entities = query_explore(endpoint)
        print(len(entities))
        return '\n'.join([create_url(endpoint, x) for x in entities])
    return 'Endpoint not found' 

@app.route('/rest/<endpoint>/<path:uri>/')
def get_attr(endpoint=None, uri=None):
    if endpoint in endpoints.keys() and uri:
        d = get_attributes(endpoint, uri)
        return str(d)
    return 'Bad entity or no URI'

if __name__ == '__main__':
    app.run(debug=True)
