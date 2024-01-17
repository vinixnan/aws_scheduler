from aws.ec2 import generate_aws_dict
from utils.files import get_dot
from optimization.algorithm import run_all
from optimization.problem import remove_dominated, get_problems


def generate_solutions(config, full_name_regions):
    print(config)
    number_of_tasks = int(get_dot(config.problem_file_path) / 2)
    dccv, regions = generate_aws_dict(full_name_regions, config.eager_aws)
    problems = get_problems(number_of_tasks, regions, dccv, config.problem_file_path)
    all_regions_pop = run_all(problems, config)
    non_dominated_population = remove_dominated(all_regions_pop)
    return non_dominated_population


def select_one_solution(population):
    qtd_obj = 2
    max_data = []
    min_data = []
    mean_data = []
    for i in range(qtd_obj):
        all_fitness = [s.F[i] for s in population]
        el_max = max(all_fitness)
        el_min = min(all_fitness)
        el_mean = sum(all_fitness) / len(population)
        max_data.append(el_max)
        min_data.append(el_min)
        mean_data.append(el_mean)
    for s in population:
        s.fitness = 0
        for i in range(qtd_obj):
            s.fitness = s.fitness + (
                (s.F[i] - min_data[i]) / (max_data[i] - min_data[i])
            )
            s.valid = True
            if s.F[i] > mean_data[i]:
                s.valid = False
        s.fitness = float(s.fitness)

    filtered = list(filter(lambda s: s.valid, population))
    print(len(filtered))
    return min(filtered, key=lambda s: s.fitness), filtered
