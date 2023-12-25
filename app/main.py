
from aws.ec2 import get_aws_regions_full
from utils.files import generate_simgrid_xml
from optimization.generate import generate_solutions
from dotenv import load_dotenv

load_dotenv()

if __file__ == "main":
    full_name_regions=get_aws_regions_full()
    non_dominated_population = generate_solutions("", full_name_regions)
    for sol in non_dominated_population:
       print(generate_simgrid_xml(sol))