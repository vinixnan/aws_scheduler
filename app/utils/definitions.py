from collections import namedtuple

Machine = namedtuple("Machine", "name data link")
Config = namedtuple(
    "Config",
    "seed algorithm_name heuristic_name n_gen pop_size problem_name problem_file_path verbose eager_aws execution_id starting_region",
)
