from optimization.generate import generate_solutions
import pytest
from dotenv import load_dotenv

load_dotenv()

def test_generate_solutions():
    arr = generate_solutions("", ['US East (N. Virginia)'], 1, True)
    assert len(arr) > 50

