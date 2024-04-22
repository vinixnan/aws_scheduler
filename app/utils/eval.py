import json
import math
import subprocess
import tempfile
from collections import OrderedDict, defaultdict

from aws.ec2 import generate_aws_dict, get_aws_regions_full
from app.optimization.pysimgrid.pysim_helper import generate_simgrid_xml
from utils.files import save_json, save_xml


def get_simple_decision(task2ins, ins2type, taskInOrder, task_names, machines_dataset):
    prepared = defaultdict(list)
    dc_types = {}
    task_in_host = OrderedDict()

    for id_task in range(len(ins2type)):
        instance = task2ins[id_task]
        machine_type = ins2type[instance]
        order = taskInOrder[id_task]
        prepared[instance].append((task_names[id_task], order))
        dc_types[instance] = Machine(
            "host" + str(instance),
            machines_dataset[machine_type],
            "link" + str(instance),
        )

    ret = [(dc_types[k], [el[0] for el in sorted(v, key=lambda x: x[1])]) for k, v in prepared.items()]
    for k, values in ret:
        for v in values:
            task_in_host[v] = k.name

    return ret, task_in_host


def calc_makespan(machines, task_in_host, problem_file_path):
    tf_json = tempfile.NamedTemporaryFile()
    save_json(task_in_host, tf_json.name)
    tf_xml = tempfile.NamedTemporaryFile()

    xml_data = generate_simgrid_xml(machines)
    save_xml(xml_data, tf_xml.name)
    p = subprocess.Popen(
        "runsimulation --hostconf " + tf_xml.name + " -p " + problem_file_path + " -a " + tf_json.name,
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


full_name_regions = get_aws_regions_full()
region_machines_dataset, regions = generate_aws_dict(full_name_regions, False)


problems = [
    "Montage_25",
    "Montage_50",
    "Montage_100",
    "Epigenomics_24",
    "Epigenomics_46",
    "Epigenomics_100",
    "CyberShake_30",
    "CyberShake_50",
    "CyberShake_100",
    "Sipht_30",
    "Sipht_60",
    "Inspiral_30",
    "Inspiral_50",
    "Sipht_100",
    "Inspiral_100",
]
iteration = 0
max_iter = 20

# max_iter = 2
# problems=["Montage_25"]

problem_all_data = {}
for problem in problems:
    print(problem)
    all_data = []
    for iteration in range(max_iter):
        filename = f"/results/VARVmSchedule_2obj_sci_{problem}_2_sci_{problem}_{iteration}_nsgaii_ZHU.default"

        file = open(filename, "r")
        Lines = file.readlines()

        solutions = []
        for line in Lines:
            data = json.loads(line)
            task2ins = data["variables"]["task2ins"]
            ins2type = data["variables"]["ins2type"]
            taskInOrder = data["variables"]["taskInOrder"]
            machines_dataset = region_machines_dataset[data["variables"]["region"]]
            problem_file_path = "datasets/" + data["problem"].replace("sci_", "") + ".dot"
            task_name = {}
            for i in range(len(taskInOrder) - 2):
                istr = str(i)
                zero_size = 5 - len(istr)
                extra = "0" * zero_size
                id_name = "ID" + extra + istr
                task_name[i] = id_name

            task_name[len(taskInOrder) - 2] = "root"
            task_name[len(taskInOrder) - 1] = "end"
            ret, task_in_host = get_simple_decision(task2ins, ins2type, taskInOrder, task_name, machines_dataset)
            machines = {el[0].name: el[0] for el in ret}
            resp = calc_makespan(machines, task_in_host, problem_file_path)
            data["ret"] = [((machine.name, machine.data["name"]), tasks) for machine, tasks in ret]
            # data['decision']=task_in_host
            data["pysim_makespan"] = resp["makespan"]
            data["pysim_price"] = math.ceil(float(resp["makespan"]) / 3600) * sum(
                [machine.data["pricePerUnit"] for machine in machines.values()]
            )
            solutions.append(data)
        all_data.append(solutions)
    problem_all_data[problem] = all_data


save_json(problem_all_data, "resp/all_problem_data_1000.json")
