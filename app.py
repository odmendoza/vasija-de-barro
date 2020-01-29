#!/usr/bin/env python
import os
import re
from json import dumps
from flask import Flask, g, Response, request, render_template
from neo4j import GraphDatabase, basic_auth

app = Flask(__name__, static_url_path='/static/')

password = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver('bolt://localhost:7687', auth=basic_auth("neo4j", '5zp8eguj'))


def get_db():
    if not hasattr(g, 'neo4j.db'):
        g.neo4j_db = driver.session()
        print('DB conected')
    return g.neo4j_db


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'neo4j.db'):
        print('DB disconected')
        g.neo4j_db.close()


@app.route("/", methods=['GET'])
def get_index():
    return render_template('index.html')


@app.route("/search", methods=['GET', 'POST'])
def get_graph():
    if request.method == 'POST':
        q = request.form['query']
        print(q)
        db = get_db()
        results = db.run(
            "MATCH (n)-[r:esUna]->(p:Persona) WHERE n.nombres =~ '(?i)%s.*' or n.apellidos =~ '(?i)%s.*' RETURN n as person" % (
                str(q), str(q)))
        person = []
        for record in results:
            aux = []
            for node in record:
                aux.append(node['nombres'])
                aux.append(node['apellidos'])
                aux.append(node['enlaceBiografia'])
            person.append(aux)
        print("Person: ", person)
        return render_template('search.html', data=person)


@app.route("/search/triple", methods=['GET', 'POST'])
def get_triple():
    if request.method == 'POST':
        q = request.form['query']
        print(q)
        db = get_db()
        results = db.run(
            "match (n)-[r]->(m) where n.nombres =~ '(?i)%s.*' or n.apellidos =~ '(?i)%s.*' or n.apodo =~ "
            "'(?i)%s.*' or n.texto =~ '(?i)%s.*' or n.titulo =~ '(?i)%s.*' return labels(n), r.relType, "
            "labels(m)" % (str(q), str(q), str(q), str(q), str(q)))
        print(results)
        person = []
        for record in results:
            aux = []
            print(record)
            for node in record:
                node = str(node)
                node = node.replace("['", "")
                node = node.replace("']", "")
                print(node)
                aux.append(node)
            person.append(aux)
        return render_template('search.html', data=person)


if __name__ == '__main__':
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(port=5000, debug=True)
