import json
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict

import pydotplus
import yaml


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


def get_dot_full(dot_path):
    graph_output = {}
    number_of_tasks = -1
    if "https" in dot_path:
        urllib.request.urlretrieve(dot_path, "tmp")

    graph = pydotplus.graphviz.graph_from_dot_file(dot_path)
    nodes = graph.get_nodes()
    for node in nodes:
        if node.get("size"):
            st = node.get("size").replace("'", "").replace('"', "")
            size = float(st)
            graph_output[node.get_name()] = size / 4

    return graph_output


def get_total_input(filename):
    # Parse the XML file
    tree = ET.parse(filename)
    root = tree.getroot()

    # Define variables to store the sum
    total_size = 0

    # Iterate over job elements
    for job in root.findall(".//{http://pegasus.isi.edu/schema/DAX}job"):
        # Iterate over uses elements within each job
        for uses in job.findall("{http://pegasus.isi.edu/schema/DAX}uses"):
            # Check if type is "data" and link is "input"
            if uses.attrib.get("type") == "data" and uses.attrib.get("link") == "input":
                # Add the size to the total
                total_size += int(uses.attrib.get("size"))
    return total_size


def read_xml_data(filename):
    tree = ET.parse(filename)
    # Parse the XML file
    root = tree.getroot()

    # Define the namespace
    namespace = {"dax": "http://pegasus.isi.edu/schema/DAX"}

    # Initialize the dictionary
    dax_dict = {}

    # Extract attributes from the root element
    dax_dict["version"] = root.attrib.get("version")
    dax_dict["count"] = int(root.attrib.get("count"))
    dax_dict["index"] = int(root.attrib.get("index"))
    dax_dict["name"] = root.attrib.get("name")
    dax_dict["jobCount"] = int(root.attrib.get("jobCount"))
    dax_dict["fileCount"] = int(root.attrib.get("fileCount"))
    dax_dict["childCount"] = int(root.attrib.get("childCount"))

    # Extract job information
    jobs = []
    for job in root.findall("dax:job", namespace):
        job_info = {}
        job_info["id"] = job.attrib.get("id")
        job_info["namespace"] = job.attrib.get("namespace")
        job_info["name"] = job.attrib.get("name")
        job_info["version"] = job.attrib.get("version")
        job_info["runtime"] = float(job.attrib.get("runtime"))
        job_uses = []
        for use in job.findall("dax:uses", namespace):
            use_info = {}
            use_info["file"] = use.attrib.get("file")
            use_info["link"] = use.attrib.get("link")
            use_info["register"] = use.attrib.get("register")
            use_info["transfer"] = use.attrib.get("transfer")
            use_info["optional"] = use.attrib.get("optional")
            use_info["type"] = use.attrib.get("type")
            use_info["size"] = int(use.attrib.get("size"))
            job_uses.append(use_info)
        job_info["uses"] = job_uses
        jobs.append(job_info)

    dax_dict["jobs"] = jobs

    # Extract control-flow dependencies
    dependencies = {}
    for child in root.findall("dax:child", namespace):
        child_id = child.attrib.get("ref")
        parents = [parent.attrib.get("ref") for parent in child.findall("dax:parent", namespace)]
        dependencies[child_id] = parents

    dax_dict["dependencies"] = dependencies

    return dax_dict


def generate_dict_of_size(dax_dict):
    graph = {}
    for job in dax_dict["jobs"]:
        job_id = job["id"]
        uses = job["uses"]
        runtime = job["runtime"]
        sizes = []
        for use in uses:
            if use["type"] == "data" and use["link"] == "input":
                sizes.append(use["size"])
        flop_factor = 4200000000 * runtime
        sm = sum(sizes)
        graph[job_id] = flop_factor

    return graph


def load_xml_data(xml_path, dot_path):
    dax_dict = read_xml_data(xml_path)
    graph = generate_dict_of_size(dax_dict)
    # graph = get_dot_full(dot_path)
    # del graph['end']
    # del graph['root']
    preds = dax_dict["dependencies"]

    missing = [el for el in graph.keys() if el not in preds.keys()]
    for mis in missing:
        preds[mis] = []

    succ = defaultdict(list)
    for dependent, dependencies in preds.items():
        for dependency in dependencies:
            succ[dependency].append(dependent)

    missing = [el for el in graph.keys() if el not in succ.keys()]
    for mis in missing:
        succ[mis] = []

    data = defaultdict(dict)
    for task_i in graph.keys():
        for task_j in graph.keys():
            if task_i != task_j:
                task_i_dependent = succ.get(task_i, [])
                if task_j in task_i_dependent:
                    data[task_i][task_j] = graph[task_i]

    return data, graph, preds, succ
