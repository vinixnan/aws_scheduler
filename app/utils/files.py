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


def read_json(filename):
    with open(filename, "r") as stream:
        return json.load(stream)


def read_yaml(filename):
    with open(filename, "r") as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)


def save_xml(xml_data, filename):
    with open(filename, "w") as outfile:
        outfile.write(xml_data)


def format_solution(s, problems):
    problem = problems[s.region]
    X = problem.show_solution(s)
    dc = {}
    dc["X"] = dict(Counter(X))
    dc["F"] = [float(f) for f in s.F]
    dc["region"] = s.region_name
    dc["x_aws_tasks"] = dict(s.data["saved_data"].item()["assignment"])
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
    succ = defaultdict(list)
    preds = defaultdict(list)
    if "https" in dot_path:
        urllib.request.urlretrieve(dot_path, "tmp")

    graph = pydotplus.graphviz.graph_from_dot_file(dot_path)
    nodes = graph.get_nodes()
    for node in nodes:
        if node.get("size"):
            st = node.get("size").replace("'", "").replace('"', "")
            graph_output[node.get_name()] = float(st)
    edges = graph.get_edges()
    for edge in edges:
        succ[edge.get_source()].append(edge.get_destination())
        preds[edge.get_destination()].append(edge.get_source())

    return graph_output, succ, preds


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
        graph[job_id] = sum(sizes)
    graph["root"] = 0
    graph["end"] = 0
    return graph


def load_xml_data(xml_path, dot_path):
    dax_dict = read_xml_data(xml_path)
    graph, succ, preds = get_dot_full(dot_path)
    graph = generate_dict_of_size(dax_dict)

    # They must be explicit, default dict is not enought
    missing = [el for el in graph.keys() if el not in preds.keys()]
    for mis in missing:
        preds[mis] = []

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
