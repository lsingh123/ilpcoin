import unittest
import random
import pytest
from ilpcoin.common.sample_ilps.knapsack import knapsack
from ilpcoin.common.sample_ilps.traveling_salesman import traveling_salesman
from ilpcoin.common.ilp import *


def ilp_solve_and_check(input_ilp): 
    soln = input_ilp.solve()
    return input_ilp.check(soln)

def ilp_solve_post_serialization(input_ilp): 
    reconstructed = Ilp.deserialize(input_ilp.serialize())
    return ilp_solve_and_check(reconstructed)

def ilp_serialization_basic_properties(input_ilp): 
    reconstructed = Ilp.deserialize(input_ilp.serialize())
    return reconstructed.k == input_ilp.k and reconstructed.uid == input_ilp.uid

def solution_serialization_check(input_soln): 
    return IlpSolution.deserialize(input_soln.serialize()) == input_soln

def pipe_solve_pipe_check(input_ilp):
    reconstructed = Ilp.deserialize(input_ilp.serialize())
    soln = reconstructed.solve()
    reconstructed_soln = IlpSolution.deserialize(soln.serialize())
    return input_ilp.check(soln)


class KnapsackTests(unittest.TestCase):
    def test_ilp_solve_and_check_knapsack(self): 
        self.assertTrue(ilp_solve_and_check(knapsack()))

    def test_ilp_solve_post_serialization_knapsack(self): 
        self.assertTrue(ilp_solve_post_serialization(knapsack()))

    def test_ilp_serialization_basic_properties_knapsack(self): 
        self.assertTrue(ilp_serialization_basic_properties(knapsack()))

    def test_solution_serialization(self): 
        soln = knapsack().solve()
        self.assertTrue(solution_serialization_check(soln))
    
    def test_pipe_solve_pipe_check_knapsack(self): 
        self.assertTrue(pipe_solve_pipe_check(knapsack()))

class TsmTests(unittest.TestCase):
    def test_ilp_solve_and_check_tsm(self): 
        self.assertTrue(ilp_solve_and_check(traveling_salesman()))

    def test_ilp_solve_post_serialization_tsm(self): 
        self.assertTrue(ilp_solve_post_serialization(traveling_salesman()))

    def test_ilp_serialization_basic_properties_tsm(self): 
        self.assertTrue(ilp_serialization_basic_properties(traveling_salesman()))

    def test_solution_serialization(self): 
        soln = traveling_salesman().solve()
        self.assertTrue(solution_serialization_check(soln))
    
    def test_pipe_solve_pipe_check_tsm(self): 
        self.assertTrue(pipe_solve_pipe_check(traveling_salesman()))



