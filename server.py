import rdflib
from flask import Flask

endpoints = { 'film': 
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
              'predicate': rdflib.URIRef('http://dbpedia.org/ontology/starring'),
              'name':       'starring'
          },{
              'predicate': rdflib.URIRef('http://purl.org/dc/terms/subject'),
              'name':       'subject'
          }]
          }
        }

# server = 'http://localhost:8080/openrdf-sesame/repositories/movies'
server = 'http://dbpedia.org/sparql'

graph = rdflib.ConjunctiveGraph('SPARQLStore')
graph.open(server)

app = Flask(__name__)

list_query = """
select ?entity where {{
    ?entity rdf:type {} .
}}"""

attribute_query = "select {} where {{ {} }}"

def list_compactor(l):
    if len(l) == 0:
        return l
    ret = {}
    for key in l[0].keys():
        s = set()
        for d in l:
            s.add(d[key])
        if len(s) == 1:
            ret[key] = s.pop()
        else:
            ret[key] = list(s)
    return ret


def list_entities(entity):
    query = graph.query(list_query.format(endpoints[entity]['rdftype'].n3()))
    ret = []
    for e in query.bindings:
        print(e)
        ret.append(e[rdflib.term.Variable('entity')])
    return ret
    
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
    ret = []
    for q in query.bindings:
        d = {}
        for attribute in endpoints[entity]['attributes']:
            d[attribute['name']] = q[rdflib.term.Variable(attribute['name'])].encode()
        ret.append(d)
    return list_compactor(ret)

@app.route('/rest/<endpoint>/')
def list_all(endpoint=None):
    if endpoint in endpoints.keys():
        entities = list_entities(endpoint)
        print(len(dentities))
        return str(entities)
    return 'Endpoint not found' 

@app.route('/rest/<endpoint>/<path:uri>/')
def get_attr(endpoint=None, uri=None):
    if endpoint in endpoints.keys() and uri:
        d = get_attributes(endpoint, uri)
        return str(d)
    return 'Bad entity or no URI'

if __name__ == '__main__':
    app.run(debug=True)
