from fastprocess import FastProcess
import uuid
import tempfile
import subprocess
from utils.files import save_xml, save_json
from yattag import Doc, indent
import json
from optimization.generate import get_simple_decision
from collections import defaultdict
from utils.definitions import Machine


def generate_simgrid_xml(machines, machines_as_one=False):
    factor = 1
    latency = 0.00000001
    if machines_as_one:
        factor = 10000000000000
        latency = 0

    doc, tag, _ = Doc().tagtext()
    doc.asis("<?xml version='1.0'?>")
    doc.asis(
        '<!DOCTYPE platform SYSTEM "http://simgrid.gforge.inria.fr/simgrid/simgrid.dtd">'
    )

    with tag("platform", version="4"):
        with tag("AS", id="AS0", routing="Floyd"):
            for machine in machines.values():
                doc.stag(
                    "host",
                    id=machine.name,
                    core=machine.data["vcpu"],
                    speed=machine.data["flop"],
                )
                doc.stag(
                    "link",
                    id=machine.link,
                    bandwidth=str(machine.data["networkPerformance"] * factor) + "Bps",
                    latency=str(latency) + "s",
                )
            keys = list(machines.keys())
            routes = defaultdict(dict)
            for i in range(len(keys)):
                origin = machines[keys[i]]
                for j in range(len(keys)):
                    if i != j and routes[i].get(j) is None:
                        routes[i][j] = True
                        routes[j][i] = True
                        destiny = machines[keys[j]]
                        with tag("route", src=origin.name, dst=destiny.name):
                            doc.stag("link_ctn", id=origin.link)

    return indent(doc.getvalue(), indentation=" " * 4, newline="\r\n")


def calc_makespan(machines, x_aws_tasks, problem_file_path):
    task_in_host = get_simple_decision(x_aws_tasks)
    tf_json = tempfile.NamedTemporaryFile()
    save_json(task_in_host, tf_json.name)
    tf_xml = tempfile.NamedTemporaryFile()

    xml_data = generate_simgrid_xml(machines)
    save_xml(xml_data, tf_xml.name)
    p = subprocess.Popen(
        "runsimulation --hostconf "
        + tf_xml.name
        + " -p "
        + problem_file_path
        + " -a "
        + tf_json.name,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    retval = p.wait()
    if retval == 0:
        returned_str = p.stdout.readlines()[0].decode("utf-8").rstrip()
        data = json.loads(returned_str)
        return data
    else:
        print(xml_data)
        print(p.stdout.readlines())


def get_pysim_data(combination, problem_file_path, alg, machines_as_one=False):
    tf = tempfile.NamedTemporaryFile(suffix=str(uuid.uuid4()))
    tf2 = tempfile.NamedTemporaryFile(suffix=str(uuid.uuid4()))
    f = open(tf2.name, "w")
    xml_data = generate_simgrid_xml(combination, machines_as_one)
    save_xml(xml_data, tf.name)
    # start_time = time.time()
    p = FastProcess(
        ["pysim", "--conf", tf.name, "-p", problem_file_path, "-a", alg], stdout=f
    )

    # p = subprocess.Popen(
    #    "pysim --conf " + tf.name + " -p " + problem_file_path + " -a " + alg,
    #    shell=True,
    #    stdout=subprocess.PIPE,
    #    stderr=subprocess.STDOUT,
    #    close_fds=True
    # )

    # f.close()
    # with open(tf2.name) as json_data:
    #    d = json.load(json_data)
    #    json_data.close()

    retval = p.wait()
    # print("--- %s seconds ---" % (time.time() - start_time))
    if retval == 0:
        # returned_str = p.stdout.readlines()[0].decode("utf-8").rstrip()
        # data = json.loads(returned_str)
        with open(tf2.name) as f:
            data = json.load(f)
            f.close()
        data["alg"] = alg
    else:
        print(xml_data)
        print(p.stdout.readlines())

    return data
