import threading
import time
import random
import logging
import os
from markupsafe import escape
from flask import Flask, send_from_directory, request
from flask import render_template
from flask import url_for
from flask import jsonify
import agents


# log = logging.getLogger('werkzeug')
# log.setLevel(logging.ERROR)


alpha = 0.5
noise_distribution = 10
N = 10
loss_prob = 0.5
delay_prob = 0.5
stop = False
green_edges = set()
red_edges = set()
topology = [[1 for _ in range(N)] for __ in range(N)]
for i in range(N):
    topology[i][i] = 0
nodes = [['n' + str(i), 0] for i in range(N)]
edges = []


app = Flask(__name__)


@app.route("/json/graph")
def graph_json():
    json = jsonify({'nodes' : nodes, 'edges' : edges, 'red' : [], 'grey' : [], 
    'red_edges' : list(red_edges), 'green_edges' : list(green_edges)})
    return json


@app.route("/redgreen", methods=['POST'])
def redgreen():
    global red_edges
    global green_edges
    content = request.json
    red_edges = content['red']
    green_edges = content['green']
    return ""


@app.route("/")
def main_page():
    return render_template('webpage.html', name="test")


@app.route("/run")
def run():
    global stop
    global red_edges
    global green_edges
    red_edges = []
    green_edges = []
    stop = False
    try:
        agents.main(N, topology)
    except Exception as e:
        print(e)
    return ""


@app.route("/stop")
def reset():
    global stop
    stop = True    
    return ""


@app.route("/random")
def rand():
    global topology
    topology = [[random.choices([0, 1], [60, 40])[0] for _ in range(N)] for __ in range(N)]

    for i in range(N):
        topology[i][i] = 0
    
    update_topology()
    return ""


@app.route("/remove_edge/<edge>")
def remove_edge(edge):
    _, x, y = escape(edge).split('n')
    x, y = int(x), int(y)
    topology[x][y] = 0
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


@app.route("/set_alpha/<alpha2>")
def set_alpha(alpha2):
    global alpha
    alpha = float(escape(alpha2))
    return ""


@app.route("/set_noise/<noise>")
def set_noise(noise):
    global noise_distribution
    noise_distribution = float(escape(noise))
    return ""


@app.route("/set_prob/<prob>")
def set_prob(prob):
    global loss_prob
    loss_prob = float(escape(prob))
    return ""


@app.route("/set_delay/<delay>")
def set_delay(delay):
    global delay_prob
    delay_prob = float(escape(delay))
    return ""


@app.route("/get_parameters")
def get_alpha():
    return jsonify({'alpha' : alpha, 'noise' : noise_distribution, 'prob' : loss_prob, 'stop' : stop, 'delay' : delay_prob})


@app.route("/update_vert/<id>/<num>")
def update_vert(id, num):
    nodes[int(escape(id))][1] = escape(num)
    return ""


def update_topology():
    global edges
    edges = []
    agents.grey_verts = set()
    agents.red_verts = set()
    for i in range(N):
        for e in range(N):
            if topology[i][e]:
                edges.append(('n' + str(i), 'n' + str(e)))


update_topology()

app.run(debug=False,host='0.0.0.0', port=os.environ.get('PORT'))

            