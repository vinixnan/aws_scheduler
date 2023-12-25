from main.generate import generate_solutions
import pytest

def test_generate_solutions():
    arr = generate_solutions("")
    assert len(arr) > 0

