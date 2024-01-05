from aws.ec2 import generate_aws_dict
from utils.files import get_dot
from optimization.algorithm import run_all
from optimization.problem import remove_dominated
from utils.files import generate_simgrid_xml, save_xml
import subprocess
import tempfile

def generate_solutions(dot_path, full_name_regions, seed=None, verbose=False):
    number_of_tasks = get_dot(dot_path)
    dccv, regions = generate_aws_dict(full_name_regions)
    all_regions_pop = run_all(number_of_tasks, regions, dccv, seed, verbose)
    non_dominated_population = remove_dominated(all_regions_pop)
    associate_aws_data_with_solution(non_dominated_population, dccv)
    return non_dominated_population

def associate_aws_data_with_solution(PF, dccv):
  for sol in PF:
    region_machines = dccv[sol.region]
    ndv = [(name, region_machines[name]) for name in sol.x_aws]
    for name, data in ndv:
      data['flop'] = data['ecu'] * 4.4
    sol.x_aws = ndv

def get_pysim_data(solution, problem, alg="HEFT"):
  tf = tempfile.NamedTemporaryFile()
  xml_data = generate_simgrid_xml(solution)
  save_xml(xml_data, tf.name)
  p = subprocess.Popen("pysim --conf "+tf.name+' -p '+ problem+' -a '+alg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
  retval = p.wait()
  total_time = None
  if retval==0:
      returned_str = p.stdout.readlines()[0].decode("utf-8").rstrip().split(' ')
      returned = [float(s) for s in returned_str]
      total_time = returned[-1]
  else:
      print(xml_data)
      print(p.stdout.readlines())

  return total_time
      

