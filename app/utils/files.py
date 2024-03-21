import json
import yaml
import pydotplus
import urllib.request
from collections import Counter
import xml.etree.ElementTree as ET


def save_json(dc, filename):
    json_object = json.dumps(dc, indent=4)
    with open(filename, "w") as outfile:
        outfile.write(json_object)


def save_yaml(dc, filename):
    json_object = yaml.dump(dc, indent=4, sort_keys=False)
    with open(filename, "w") as outfile:
        outfile.write(json_object)


def read_yaml(filename):
    with open(filename, "r") as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)


def save_xml(xml_data, filename):
    with open(filename, "w") as outfile:
        outfile.write(xml_data)


def format_solution(s):
    dc = {}
    dc["X"] = s.x_aws
    dc["F"] = [float(f) for f in s.F]
    dc["region"] = s.region
    dc["x_aws_tasks"] = s.x_aws_tasks
    dc["valid"] = s.valid
    dc["fitness"] = s.fitness
    return dc


def format_solution_b(s):
    dc = {}
    dc["X"] = Counter(s.X)
    dc["F"] = [float(f) for f in s.F]
    dc["region"] = s.region_name
    dc["x_aws_tasks"] = s.tasks
    dc["valid"] = True
    return dc


def get_dot(dot_path):
    number_of_tasks = -1
    if "https" in dot_path:
        urllib.request.urlretrieve(dot_path, "tmp")

    graph = pydotplus.graphviz.graph_from_dot_file(dot_path)
    nodes = graph.get_nodes()
    number_of_tasks = len(nodes)
    return number_of_tasks

def get_total_input(filename):
    # Parse the XML file
    tree = ET.parse(filename)
    root = tree.getroot()

    # Define variables to store the sum
    total_size = 0

    # Iterate over job elements
    for job in root.findall('.//{http://pegasus.isi.edu/schema/DAX}job'):
        # Iterate over uses elements within each job
        for uses in job.findall('{http://pegasus.isi.edu/schema/DAX}uses'):
            # Check if type is "data" and link is "input"
            if uses.attrib.get('type') == 'data' and uses.attrib.get('link') == 'input':
                # Add the size to the total
                total_size += int(uses.attrib.get('size'))
    return total_size
