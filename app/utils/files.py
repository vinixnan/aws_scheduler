import json
import yaml
import pydotplus
import urllib.request
import xmltodict


def save_json(dc, filename):
    json_object = json.dumps(dc, indent=4)
    with open(filename, "w") as outfile:
        outfile.write(json_object)


def save_yaml(dc, filename):
    json_object = yaml.dump(dc, indent=4, sort_keys=False)
    with open(filename, "w") as outfile:
        outfile.write(json_object)


def save_xml(xml_data, filename):
    with open(filename, "w") as outfile:
        outfile.write(xml_data)


def get_dot(dot_path):
    number_of_tasks = -1
    if "https" in dot_path:
        urllib.request.urlretrieve(dot_path, "tmp")
    if ".dot" in dot_path:
        graph = pydotplus.graphviz.graph_from_dot_file(dot_path)
        nodes = graph.get_nodes()
        number_of_tasks = len(nodes)
    elif ".xml" in dot_path or ".dax" in dot_path:
        with open(dot_path) as fd:
            doc = xmltodict.parse(fd.read())
            number_of_tasks = int(doc["adag"]["@jobCount"])

    return number_of_tasks
