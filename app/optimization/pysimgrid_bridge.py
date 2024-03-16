from utils.files import save_xml
import subprocess
import tempfile
import json
import numpy as np


def get_pysim_data(solution, algs, selections):
    problem = solution.problem
    tf = tempfile.NamedTemporaryFile()
    xml_data, machines = problem.generate_simgrid_xml(solution)
    save_xml(xml_data, tf.name)
    data_arr = []
    for alg in algs:
        p = subprocess.Popen(
            "pysim --conf "
            + tf.name
            + " -p "
            + problem.problem_file_path
            + " -a "
            + alg,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        retval = p.wait()
        if retval == 0:
            returned_str = p.stdout.readlines()[0].decode("utf-8").rstrip()
            data = json.loads(returned_str)
            data["alg"] = alg
            data_arr.append(data)

            save_xml(xml_data, "examplex2.xml")
        else:
            print(xml_data)
            print(p.stdout.readlines())
    selected = min(data_arr, key=lambda x: x["makespan"])

    if selections:
        selections[selected["alg"]] = 1 + selections.get(selected["alg"], 0)

    makespan = float(selected["makespan"])
    tasks = selected["tasks"]
    ids = [int(el.replace("host", "")) for el in tasks.keys()]
    solution.x_aws = [machines[id][0] for id in ids]
    solution.x_aws_tasks = tasks
    solution.alg = selected["alg"]
    problem.update_decision_variables(solution, makespan)
    return makespan
