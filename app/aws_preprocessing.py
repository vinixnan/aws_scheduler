from collections import defaultdict


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
        final_region_machines[region_name][machine_name] = dataset[region_name][
            machine_name
        ]
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
