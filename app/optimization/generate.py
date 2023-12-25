from aws.ec2 import generate_aws_dict
from utils.files import get_dot
from optimization.algorithm import run_all
from optimization.problem import invert_maximization, remove_dominated

def generate_solutions(dot_path, full_name_regions, seed=None, verbose=False):
    number_of_tasks = get_dot(dot_path)
    dccv, regions = generate_aws_dict(full_name_regions)
    all_regions_pop = run_all(number_of_tasks, regions, dccv, seed, verbose)
    non_dominated_population = remove_dominated(all_regions_pop)
    associate_aws_data_with_solution(non_dominated_population, dccv)
    invert_maximization(non_dominated_population)
    return non_dominated_population

def associate_aws_data_with_solution(PF, dccv):
  for sol in PF:
    region_machines = dccv[sol.region]
    ndv = [(name, region_machines[name]) for name in sol.x_aws]
    for name, data in ndv:
      data['flop'] = data['ecu'] * 4.4
    sol.x_aws = ndv

