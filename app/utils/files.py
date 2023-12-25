import json
import yaml
from yattag import Doc, indent
import pydotplus
import urllib.request

def save_json(dc, filename):
    json_object = json.dumps(dc, indent=4)
    with open(filename, "w") as outfile:
        outfile.write(json_object)

def save_yaml(dc, filename):
    json_object = yaml.dump(dc, indent=4, sort_keys=False)
    with open(filename, "w") as outfile:
        outfile.write(json_object)


def generate_simgrid_xml(sol):
  doc, tag, text = Doc().tagtext()

  doc.asis("<?xml version='1.0'?>")
  doc.asis('<!DOCTYPE platform SYSTEM "http://simgrid.gforge.inria.fr/simgrid/simgrid.dtd">')
  machines = dict(list(enumerate(sol.x_aws)))
  with tag('platform', version="4"):
      with tag('AS', id="AS0",  routing="Floyd"):
          for id, machine in machines.items():
            doc.stag('host', id='host'+str(id), core=machine[1]['vcpu'], speed=machine[1]['flop'])
            doc.stag('link', id='link'+str(id), bandwidth=machine[1]['networkPerformance'], latency="0.0001s")
          idlink=0
          for idi in range(len(machines)):
            for idj in range(idi+1, len(machines)):
                with tag('route', src="host"+str(idi), dst="host"+str(idj)):
                  doc.stag('link_ctn', id="link"+str(idlink))
                idlink = idlink + 1

  result = indent(
      doc.getvalue(),
      indentation = ' '*4,
      newline = '\r\n'
  )
  return result

def get_dot(dot_path):
    urllib.request.urlretrieve("https://raw.githubusercontent.com/vinixnan/pysimgrid/master/test/data/basic_graph.dot", "basic_graph.dot")
    graph=pydotplus.graphviz.graph_from_dot_file('basic_graph.dot')
    nodes=graph.get_nodes()
    number_of_tasks=len(nodes)
    return number_of_tasks