from collections import defaultdict, namedtuple
import math
from pysim_helper import get_pysim_data

Machine = namedtuple("Machine", "name data link")


def dominates(s1, s2):
    better = 0
    eq = 0
    worse = 0
    for i in range(len(s1)):
        if s1[i] < s2[i]:
            better = better + 1
        elif s1[i] == s2[i]:
            eq = eq + 1
        else:
            worse = worse + 1

    if better == len(s1):
        # fullly dominates
        return 1
    if worse == len(s1):
        # fully dominated
        return -1
    if eq == len(s1):
        # exactly the same
        return 0

    if better > 0 and worse == 0:
        # dominates a little
        return 1
    if worse > 0 and better == 0:
        # is dominated a little
        return -1
    return 0


def remove_dominated(pop):
    returning = []
    for i in range(len(pop)):
        dominated = False
        for j in range(len(pop)):
            if i != j:
                if dominates(pop[i][0], pop[j][0]) == -1:
                    dominated = True
                    break
        if not dominated:
            returning.append(pop[i])
    return returning


def remove_non_dominated_from_dataset(dataset):
    pop = []
    final_region_machines = defaultdict(dict)
    for region_name, machines in dataset.items():
        for machine_data in machines.values():
            element = (
                (machine_data["ecu"] * -1, machine_data["pricePerUnit"]),
                (machine_data["name"], region_name),
            )
            pop.append(element)
    ndom = remove_dominated(pop)
    for element in ndom:
        machine_name, region_name = element[1]
        final_region_machines[region_name][machine_name] = dataset[region_name][machine_name]
    return final_region_machines


def discover_non_dominated_regions(dccv):
    final_region_machines = remove_non_dominated_from_dataset(dccv)
    return list(final_region_machines.keys())


def remove_non_dominated_per_region(dccv):
    non_dominated_regions = discover_non_dominated_regions(dccv)
    dataset = {}
    for region_name in non_dominated_regions:
        to_send = {}
        to_send[region_name] = dccv[region_name]
        dataset = dict(dataset, **remove_non_dominated_from_dataset(to_send))
    return dataset


def remove_bad_performing_machines(final_region_machines, number_of_tasks, data_trasfer_cost, problem_file_path):
    pop = []
    qtd_machines = []
    for region_name, machines_data in final_region_machines.items():
        for machine_name, machine_data in machines_data.items():
            selected_region_machines = [machine_data] * number_of_tasks
            machines = {}
            for i, machine_data in enumerate(selected_region_machines):
                mach = Machine("host" + str(i), machine_data, "link" + str(i))
                machines[mach.name] = mach

            resp = get_pysim_data(machines, problem_file_path, "HEFT")
            machines = {k: v for k, v in machines.items() if k in resp["tasks"].keys()}
            qtd_machines.append(len(machines))
            price = math.ceil(float(resp["makespan"]) / 3600) * sum(
                [machine.data["pricePerUnit"] for machine in machines.values()]
            ) + data_trasfer_cost.get(region_name, 0)
            element = (
                (resp["makespan"], price),
                (machine_data["name"], region_name, resp["tasks"]),
            )
            # print(element)
            pop.append(element)

    n_var = int(sum(qtd_machines) / len(qtd_machines) + 1)
    ndom_base = remove_dominated(pop)
    final_region_machines2 = defaultdict(dict)
    for element in ndom_base:
        machine_name, region_name, _ = element[1]
        final_region_machines2[region_name][machine_name] = final_region_machines[region_name][machine_name]
    return final_region_machines2, n_var, ndom_base
