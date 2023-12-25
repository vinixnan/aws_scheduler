from aws.ec2 import generate_aws_dict
from utils.files import get_dot, generate_simgrid_xml
from optimization.algorithm import invert_maximization, remove_dominated, associate_aws_data_with_solution, run_all

def generate_solutions(dot_path):
    number_of_tasks = get_dot(dot_path)
    _, dccv, regions = generate_aws_dict()
    all_regions_pop = run_all(number_of_tasks, regions, dccv)
    non_dominated_population = remove_dominated(all_regions_pop)
    associate_aws_data_with_solution(non_dominated_population, dccv)
    invert_maximization(non_dominated_population)
    return non_dominated_population

non_dominated_population = generate_solutions("")
for sol in non_dominated_population:
    print(generate_simgrid_xml(sol))