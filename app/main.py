
from aws.ec2 import get_aws_regions_full
from utils.files import generate_simgrid_xml
from optimization.generate import generate_solutions, get_pysim_data
from optimization.problem import invert_maximization, remove_dominated
from dotenv import load_dotenv
import numpy as np

load_dotenv()

dot_file = "/home/pysimgrid/dots/basic_graph.dot"
full_name_regions=get_aws_regions_full()
full_name_regions=[full_name_regions[0]]
print("Generating solutions for "+str(full_name_regions))
non_dominated_population = generate_solutions("", full_name_regions, 1, False)
non_dominated_population_n = []
print(len(non_dominated_population))
print("Running scheduler")
for sol in non_dominated_population:
    data = get_pysim_data(sol, dot_file)
    if data:
        total_time = data['makespan']
        tasks = data['tasks']
        sol.F = np.append(sol.F, total_time)
        sol.x_aws_tasks = tasks
        non_dominated_population_n.append(sol)
    
non_dominated_population = non_dominated_population_n  
print("Removing non-dominated")
print(len(non_dominated_population))
non_dominated_population = remove_dominated(non_dominated_population)
print(len(non_dominated_population))
invert_maximization(non_dominated_population)

for s in non_dominated_population:
    print([el[0] for el in s.x_aws], s.F, s.region, s.x_aws_tasks)