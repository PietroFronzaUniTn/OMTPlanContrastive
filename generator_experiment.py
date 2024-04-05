import sys
import os
from driver import arguments

import subprocess
import utils
from copy import deepcopy
from planner import encoder
from planner import modifier
from planner import search
import argparse

from unified_planning.io import PDDLReader
from unified_planning.shortcuts import *

def parse_args():
    """
    Specifies valid arguments for OMTPlan
    """

    parser = argparse.ArgumentParser(description = arguments.DESCRIPTION,formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('problem', metavar='problem.pddl', help='Path to PDDL problem file', type=arguments._is_valid_file)

    # Optional arguments

    parser.add_argument('-domain', help='Path to PDDL domain file', type=arguments._is_valid_file)
    
    #parser.add_argument('-linear', action='store_true', help='Builds a sequential encoding.')

    #parser.add_argument('-parallel', action='store_true', help='Builds a parallel encoding.')
    #parser.add_argument('-b', type=int, default=100, help='Upper bound for OMTPlan search.')
    
    parser.add_argument('-plan', help='Path to PDDL plan file', type=arguments._is_valid_file)
    
    args = parser.parse_args()
    
    return args

def get_set_action_variables(encoder):
    action_set= set()
    #print(encoder.action_variables)
    for _, action in encoder.action_variables.items():
        action_set.update(list(action.keys()))
    return list(action_set)

# TODO: create function to extract plan actions. If args.plan is not set use the solver (pass encoder, solve and validate). If args.plan is set extract list of actions    
def get_plan_action(plan, encoder):
    if not plan:
        s = search.SearchSMT(encoder, 100)
        plan = s.do_linear_search()
        if plan.validate():
            return plan.plan.actions
        else:
            return []
    else:
        # Open file
        # Get list of actions
        # For all action in plan
            # name of action + list of parameters in parenthesis with _ between object
        # return list
        return []

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

args = parse_args()

# Parse PDDL problem
reader = PDDLReader()
task = reader.parse_problem(args.domain, args.problem)

problem_name = task.name

e = encoder.EncoderSMT(task, modifier.LinearModifier())

plan_actions = get_plan_action(args.plan, e)
if len(plan_actions) == 0:
    raise Exception("Plan is not valid")

plan_actions = [str(item) for item in plan_actions]

# Get list of action variables
action_variables = get_set_action_variables(e)
#print(plan_actions)
#print(action_variables)

base_command = "time python omtplan.py -smt -linear -translate {} -pprint -domain {} {}".format(len(plan_actions), args.domain, args.problem)
commands = []

base_axiom_args = " -contrastive -axiom {} -first_action {}"
optional_axiom_args = " -second_action {} -step {}"

#for action in plan_actions:
    #print(action)

# Save commands for axiom 1
# Only actions not present in the plan
for action in action_variables:
    if action not in plan_actions:
        commands.append(base_command + base_axiom_args.format(1, action))


# Save commands for axiom 2
for action in action_variables:
    if action in plan_actions:
        commands.append(base_command + base_axiom_args.format(2, action))

# Save commands for axiom 3
for action1 in action_variables:
    if action1 in plan_actions:
        for action2 in action_variables: 
            if action1!=action2:
                for step in range(len(plan_actions)):
                    commands.append(base_command + base_axiom_args.format(3, action1) + optional_axiom_args.format(action2, step))

# Save commands for axiom 4
for action1 in action_variables:
    if action1 in plan_actions:
        for action2 in action_variables: 
            if action2 in plan_actions:
                if action1!=action2:
                    for step in range(len(plan_actions)-1):
                        commands.append(base_command + base_axiom_args.format(4, action1) + optional_axiom_args.format(action2, step))
                        
with open(os.path.join(BASE_DIR,'{}_contrastive_commands.txt').format(problem_name),'w') as fo:
    for command in commands:
        fo.write("%s\n" % command)