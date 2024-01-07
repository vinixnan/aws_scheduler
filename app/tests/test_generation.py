from optimization.generate import generate_solutions, get_pysim_data
import pytest
from dotenv import load_dotenv

load_dotenv()


def test_generate_solutions():
    arr = generate_solutions("", ["US East (N. Virginia)"], 1, True)
    assert len(arr) > 50
    dot_file = "/home/pysimgrid/dots/basic_graph.dot"
    resp = get_pysim_data(arr[0], dot_file)
    assert resp != None
