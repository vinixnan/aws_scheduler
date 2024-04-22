import json


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
                s1 = (pop[i][1], pop[i][2])
                s2 = (pop[j][1], pop[j][2])
                if dominates(s1, s2) == -1:
                    dominated = True
                    break
        if not dominated:
            returning.append(pop[i])
    return returning


file = open("resp/all_problem_data_1000.json", "r")
data = json.load(file)


for problem_name, problem_populations in data.items():
    simpler = []
    for population in problem_populations:
        for solution in population:
            el = (
                solution["variables"]["region"],
                solution["pysim_makespan"],
                solution["pysim_price"],
                solution["objectives"]["makespan"],
                solution["objectives"]["cost"],
                solution["ret"],
            )
            simpler.append(el)
    print(len(simpler))
    simpler = remove_dominated(simpler)
    print(len(simpler))
    print([(el[0], el[1], el[2]) for el in simpler])
    json_object = json.dumps(simpler, indent=4)
    with open("resp2/" + problem_name + "_pysim.json", "w") as outfile:
        outfile.write(json_object)
