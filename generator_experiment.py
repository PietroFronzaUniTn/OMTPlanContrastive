import os
import random
from driver import arguments

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

    for _, action in encoder.action_variables.items():
        action_set.update(list(action.keys()))
    return list(action_set)

def get_plan_action(plan, encoder):
    if not plan:
        s = search.SearchSMT(encoder, 100)
        plan = s.do_linear_search()
        if plan.validate():
            return plan.plan.actions
        else:
            return []
    else:
        plan_actions = []
        # Open file
        with open(os.path.join(BASE_DIR,plan),'r') as fo:
            for line in fo:
                line = line.replace("(", " ")
                line = line.replace(")", "")
                line = line.strip()
                action_line = line.split(" ")
                action = ""
                for i in range(len(action_line)):
                    if i==0:
                       action += action_line[i]
                    else:
                        action += "_"+action_line[i] 
                plan_actions.append(action)
        return plan_actions

def get_random_commands(command_list):
    commands = []
    for i in range(NUM_EXPERIMENTS):
        rand_index = random.randint(0, len(command_list)-1)
        commands.append(command_list[rand_index])
    return commands

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
NUM_EXPERIMENTS = 3

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

e.encode(len(plan_actions))

# Get list of action variables
action_variables = get_set_action_variables(e)

base_command = "time python omtplan.py -smt -linear -translate {} -pprint -domain {} {}".format(len(plan_actions), args.domain, args.problem)
base_axiom_args = " -contrastive -axiom {} -first_action {}"
optional_axiom_args = " -second_action {} -step {}"

commands = []
axiom_commands = []

# Save commands for axiom 1
# Only actions not present in the plan
for action in action_variables:
    if action not in plan_actions:
        axiom_commands.append(base_command + base_axiom_args.format(1, action))

if len(axiom_commands) > 0:
    commands.extend(get_random_commands(axiom_commands))
    axiom_commands.clear()

# Save commands for axiom 2
for action in action_variables:
    if action in plan_actions:
        axiom_commands.append(base_command + base_axiom_args.format(2, action))
        
if len(axiom_commands) > 0:
    commands.extend(get_random_commands(axiom_commands))
    axiom_commands.clear()

# Save commands for axiom 3
for step in range(len(plan_actions)):
    action1 = plan_actions[step]
    for action2 in action_variables: 
        if action1!=action2:
            axiom_commands.append(base_command + base_axiom_args.format(3, action1) + optional_axiom_args.format(action2, step))

if len(axiom_commands) > 0:
    commands.extend(get_random_commands(axiom_commands))
    axiom_commands.clear()

# Save commands for axiom 4
for step in range(len(plan_actions)-1):
    action1 = plan_actions[step]
    action2 = plan_actions[step+1]
    if action1 != action2:
        axiom_commands.append(base_command + base_axiom_args.format(4, action1) + optional_axiom_args.format(action2, step))                        
                        
if len(axiom_commands) > 0:
    commands.extend(get_random_commands(axiom_commands))
    axiom_commands.clear()
else:
    commands.append("Axiom 4 encoding not supported since the plan is made of one action repeated over multiple steps")
    print("Axiom 4 encoding not supported since the plan is made of one action repeated over multiple steps")
                        
with open(os.path.join(BASE_DIR,'{}_contrastive_commands.txt').format(problem_name),'w') as fo:
    for command in commands:
        fo.write("------------------------\n")
        fo.write("echo \"%s\"\n" % command)
        fo.write("%s\n" % command)