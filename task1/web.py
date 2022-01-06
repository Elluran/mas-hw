from flask import Flask, send_from_directory
from flask import render_template
from flask import url_for
from flask import jsonify
import threading
import time
import agents
from markupsafe import escape
import random
import logging

# log = logging.getLogger('werkzeug')
# log.setLevel(logging.ERROR)

N = 7
topology = [[1 for _ in range(N)] for __ in range(N)]
for i in range(N):
    topology[i][i] = 0
nodes = [['n' + str(i), 0] for i in range(N)]
edges = []


app = Flask(__name__)

@app.route("/json/graph")
def graph_json():
    return jsonify({'nodes' : nodes, 'edges' : edges, 'red' : list(agents.red_verts), 'grey' : list(agents.grey_verts)})


@app.route("/json/answer")
def get_answer():
    return jsonify({'answer' : agents.answer})


@app.route("/")
def main_page():
    return render_template('webpage.html', name="test")


@app.route("/run")
def run():
    try:
        agents.main(N, topology)
    except Exception as e:
        print(e)
    return ""


@app.route("/reset")
def reset():
    global topology
    topology = [[1 for _ in range(N)] for __ in range(N)]
    for i in range(N):
        topology[i][i] = 0
    
    update_topology()
    return ""


@app.route("/random")
def rand():
    global topology
    topology = [[random.choices([0, 1], [70, 30])[0] for _ in range(N)] for __ in range(N)]
    for i in range(N):
        for e in range(i, N):
            topology[i][e] = topology[e][i]

    for i in range(N):
        topology[i][i] = 0
    
    update_topology()
    return ""


@app.route("/remove_edge/<edge>")
def remove_edge(edge):
    _, x, y = escape(edge).split('n')
    x, y = int(x), int(y)
    topology[x][y] = 0
    topology[y][x] = 0
    update_topology()
    return ""

@app.route("/set_n/<agents>")
def set_n(agents):
    global N
    global topology
    global nodes

    N = int(escape(agents))
    topology = [[1 for _ in range(N)] for __ in range(N)]
    for i in range(N):
        topology[i][i] = 0
    nodes = [['n' + str(i), 0] for i in range(N)]
    update_topology()
    return ""


@app.route("/update_vert/<id>/<num>")
def update_vert(id, num):
    nodes[int(escape(id))][1] = num
    return ""


def update_topology():
    global edges
    edges = []
    agents.grey_verts = set()
    agents.red_verts = set()
    for i in range(N):
        for e in range(i, N):
            if topology[i][e]:
                edges.append(('n' + str(i), 'n' + str(e)))

update_topology()


app.run(debug=False,host='0.0.0.0')


            