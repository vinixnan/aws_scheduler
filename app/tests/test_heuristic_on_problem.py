from aws.ec2 import generate_aws_dict, get_aws_regions_full
from optimization.heuristic.base import generate_W
from optimization.heuristic.heft import HEFT
from optimization.pysimgrid.pysim_helper import calc_makespan
from utils.definitions import Config
from utils.files import get_dot, load_xml_data


def test_real():
    problem = "Cybershake_100.dot"
    problem_file_path = "datasets/" + problem
    problem_name = problem_file_path.split("/")[1].replace(".dot", "")
    problem_xml_name = problem_file_path.replace(".dot", ".xml")
    config = Config(
        None,
        None,
        None,
        None,
        None,
        problem_name,
        problem,
        False,
        False,
        0,
        "us-east-1",
    )
    full_name_regions = get_aws_regions_full()
    number_of_tasks = int(get_dot(problem_file_path)) - 2
    # print("dataset size",size_of_dataset_in_gb/number_of_tasks * 1024, number_of_tasks)
    region_machines_dataset, regions = generate_aws_dict(full_name_regions, config.eager_aws)

    region_machines_dataset = {"us-east-1": region_machines_dataset["us-east-1"]}
    region_machines_dataset["us-east-1"] = {"m1.small": region_machines_dataset["us-east-1"]["m1.small"]}
    region_machines_dataset["us-east-1"]["m1.small"]["networkPerformance"] = 1000000000
    regions = ["us-east-1"]
    region = "us-east-1"

    data, graph, pred, succ = load_xml_data(problem_xml_name, problem_file_path)
    task_names = list(graph.keys())

    w = generate_W(config, problem, problem_file_path, regions, region_machines_dataset)
    w = w[region]
    machine_types = ["m1.small", "m1.small"]

    heu = HEFT(w, region_machines_dataset["us-east-1"], succ, pred, data)

    assignment, makespan, first_host, last_host, machines = heu.schedule(machine_types)
    assert makespan > 0

    assignment[last_host].append(
        {
            "machine": last_host,
            "name": "end",
            "AFT": assignment[last_host][-1],
            "EST": assignment[last_host][-1],
        }
    )
    assignment[first_host].insert(0, {"machine": last_host, "name": "root", "AFT": 0, "EST": 0})
    resp2 = calc_makespan(machines, assignment, problem_file_path)
    print(makespan, resp2["makespan"])
