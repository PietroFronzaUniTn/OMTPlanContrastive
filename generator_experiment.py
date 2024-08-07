import os
import random
from driver import arguments

from planner import encoder
from planner import modifier
from planner import search
import argparse

from unified_planning.io import PDDLReader
from unified_planning.shortcuts import *

import networkx as nx

from unified_planning.plans import SequentialPlan
from unified_planning.plans import PartialOrderPlan
from unified_planning.plans import ActionInstance
#from graphviz import Source
from pprint import pprint
from unified_planning.plot import plot_partial_order_plan

def parse_args():
    """
    Specifies valid arguments for OMTPlan
    """

    parser = argparse.ArgumentParser(description = arguments.DESCRIPTION,formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('problem', metavar='problem.pddl', help='Path to PDDL problem file', type=arguments._is_valid_file)

    # Optional arguments

    parser.add_argument('-domain', help='Path to PDDL domain file', type=arguments._is_valid_file)
    
    parser.add_argument('-linear', action='store_true', help='Builds a sequential encoding.')

    parser.add_argument('-parallel', action='store_true', help='Builds a parallel encoding.')
    #parser.add_argument('-b', type=int, default=100, help='Upper bound for OMTPlan search.')
    
    parser.add_argument('-plan', help='Path to PDDL plan file', type=arguments._is_valid_file)

    parser.add_argument('-partial', action='store_true', help='Show partial order graph')
    
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
        r_plan = s.do_linear_search()
        if r_plan.validate():
            return r_plan.plan.actions, r_plan.plan
        else:
            return [], None
    else:
        plan_actions = []
        plan_list = []
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
            actions = e.getActionsList()
            for action in plan_actions:
                for g_a in actions:
                    if g_a.name == action:
                        plan_list.append(ActionInstance(g_a))
            r_plan = SequentialPlan(plan_list, e.ground_problem.environment)
        return plan_actions, r_plan

def get_random_commands(command_list):
    commands = []
    for i in range(NUM_EXPERIMENTS):
        rand_index = random.randint(0, len(command_list)-1)
        commands.append(command_list[rand_index])
    return commands

def retrieve_max_depth(graph):
    starting_nodes = [n for n, d in graph.in_degree() if d==0]
    leaves = {n for n, d in graph.out_degree() if d == 0}
    all_paths = []
    for root in starting_nodes:
        for leaf in leaves:
            paths = list(nx.all_simple_paths(graph, root, leaf))
            if len(paths) == 0 and root == leaf:
                all_paths.append([root])
            all_paths.extend(paths)

    max_depth = 0
    for path in all_paths:
        if len(path)>max_depth:
            max_depth = len(path)
    return max_depth, all_paths

    # in generazione path per i comandi, gli starting node non serve cercarli negli altri paths, perché non possono essere parte di un altro path in quanto non hanno archi in ingresso

def paths_to_str(paths):
    all_paths = []
    for pt in paths:
        path = []
        for a in pt:
            path.append(a.action.name)
        all_paths.append(path)
    return all_paths

def fix_paths_length(paths, max_depth):
    new_paths = []
    for path in paths:
        if len(path) < max_depth and len(path)!=1:
            new_path = [None for _ in range(max_depth)]
            curr_ind = 0
            already_moved = False
            jump = False
            for action in path:
                if curr_ind >= max_depth:
                    break
                index = -1
                for pt in paths:
                    if len(pt) < max_depth:
                        # search only in paths that is long originally max length
                        continue
                    try:
                        index = pt.index(action)
                        # if index found break the cycle
                        break
                    except ValueError:
                        continue
                if index == -1:
                    # if index not found, use the index of the original path
                    index = path.index(action)
                if curr_ind<index:
                    # The index found is greater than the current index
                    if(not already_moved):
                        # If we do not have moved already an action, we adjust the path to all actions closer together
                        new_path[index] = action
                        for i in range(curr_ind):
                            new_path[index-1-i] = new_path[curr_ind-1-i]
                            new_path[curr_ind-1-i] = None
                        curr_ind = index
                        already_moved = True
                    else:
                        jump = True
                        break
                else:
                    # If the current index is greater than the index of the action or is equal, simply put the action in the current index place
                    new_path[curr_ind] = action
                curr_ind = curr_ind+1
            if not jump:
                new_paths.append(new_path)
            else:
                new_paths.append(path)
        else:
            new_paths.append(path)
    return new_paths

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
NUM_EXPERIMENTS = 3

args = parse_args()

# Parse PDDL problem
reader = PDDLReader()
task = reader.parse_problem(args.domain, args.problem)

problem_name = task.name

e = encoder.EncoderSMT(task, modifier.LinearModifier())

plan_actions, plan = get_plan_action(args.plan, e)
if len(plan_actions) == 0:
    raise Exception("Plan is not valid")

print("Finished search")

if not isinstance(plan, SequentialPlan):
    plan = SequentialPlan()
partial_order = plan.convert_to(unified_planning.plans.PlanKind.PARTIAL_ORDER_PLAN, task)
max_depth, paths = retrieve_max_depth(partial_order._graph)
partial_paths = paths_to_str(paths)

print("Finished max depth search")

if args.partial:
    plot_partial_order_plan(partial_order)

plan_actions = [str(item) for item in plan_actions]

partial_paths = fix_paths_length(partial_paths, max_depth)

layered_actions = [[None] for _ in range(max_depth)]
for path in partial_paths:
    for step in range(len(path)):
        if path[step] != None and step<max_depth:
            layered_actions[step].append(path[step])

e.encode(len(plan_actions))

print("Finished encoding")

# Get list of action variables
action_variables = get_set_action_variables(e)

base_linear_command = "time python3 omtplan.py -smt -{} -translate {} -domain {} {}".format('linear',len(plan_actions), args.domain, args.problem)
base_parallel_command = "time python3 omtplan.py -smt -{} -translate {} -domain {} {}".format('parallel',max_depth, args.domain, args.problem)
base_axiom_args = " -contrastive -axiom {} -first_action {}"
optional_axiom_args = " -second_action {} -step {}"

linear_commands = []
parallel_commands = []
axiom_linear_commands = []
axiom_parallel_commands = []

# Save commands for axiom 1
# Only actions not present in the plan
for action in action_variables:
    if action not in plan_actions:
        axiom_linear_commands.append(base_linear_command + base_axiom_args.format(1, action))
        axiom_parallel_commands.append(base_parallel_command + base_axiom_args.format(1, action))

if len(axiom_linear_commands) > 0:
    linear_commands.extend(get_random_commands(axiom_linear_commands))
    parallel_commands.extend(get_random_commands(axiom_parallel_commands))
    axiom_linear_commands.clear()
    axiom_parallel_commands.clear()

# Save commands for axiom 2
for action in action_variables:
    if action in plan_actions:
        axiom_linear_commands.append(base_linear_command + base_axiom_args.format(2, action))
        axiom_parallel_commands.append(base_parallel_command + base_axiom_args.format(2, action))
        
if len(axiom_linear_commands) > 0:
    linear_commands.extend(get_random_commands(axiom_linear_commands))
    parallel_commands.extend(get_random_commands(axiom_parallel_commands))
    axiom_linear_commands.clear()
    axiom_parallel_commands.clear()

# Save commands for axiom 3
for step in range(len(plan_actions)):
    action1 = plan_actions[step]
    for action2 in action_variables: 
        if action1!=action2:
            axiom_linear_commands.append(base_linear_command + base_axiom_args.format(3, action1) + optional_axiom_args.format(action2, step))

for step in range(len(layered_actions)):
    step_actions = layered_actions[step]
    for action1 in step_actions:
        for action2 in action_variables:
            if action1!=action2 and not (action2 in step_actions):
                axiom_parallel_commands.append(base_parallel_command + base_axiom_args.format(3, action1) + optional_axiom_args.format(action2, step))

if len(axiom_linear_commands) > 0:
    linear_commands.extend(get_random_commands(axiom_linear_commands))
    axiom_linear_commands.clear()

if len(axiom_parallel_commands) > 0:
    parallel_commands.extend(get_random_commands(axiom_parallel_commands))
    axiom_parallel_commands.clear()
else:
    parallel_commands.append("Axiom 3 encoding not supported since all actions are parallelized and are used in the plan")
    print("Axiom 3 encoding not supported since all actions are parallelized and are used in the plan")

# Save commands for axiom 4
for step in range(len(plan_actions)-1):
    action1 = plan_actions[step]
    action2 = plan_actions[step+1]
    if action1 != action2:
        axiom_linear_commands.append(base_linear_command + base_axiom_args.format(4, action1) + optional_axiom_args.format(action2, step)) 

single_action_path = []
for path in partial_paths:
    if len(path) == 1:
        single_action_path.append(path[0])

for path in partial_paths:
    if len(path) == max_depth:
        for step in range(max_depth-1):
            action1 = path[step]
            if action1 == None:
                continue
            action2 = path[step+1]
            if action2 == None:
                continue
            if action1!=action2:
                axiom_parallel_commands.append(base_parallel_command + base_axiom_args.format(4, action1) + optional_axiom_args.format(action2, step))
            else:
                for action in single_action_path:
                    if action!=action1:
                        axiom_parallel_commands.append(base_parallel_command + base_axiom_args.format(4, action1) + optional_axiom_args.format(action, step))

if len(axiom_linear_commands) > 0:
    linear_commands.extend(get_random_commands(axiom_linear_commands))
    axiom_linear_commands.clear()
else:
    linear_commands.append("Axiom 4 encoding not supported since the plan is made of one action repeated over multiple steps")
    print("Axiom 4 encoding not supported since the plan is made of one action repeated over multiple steps")

if len(axiom_parallel_commands) > 0:
    parallel_commands.extend(get_random_commands(axiom_parallel_commands))
    axiom_parallel_commands.clear()
else:
    parallel_commands.append("Axiom 4 encoding not supported since the plan is either made of one action repeated over multiple steps or all the actions in the plan are parallelizable")
    print("Axiom 4 encoding not supported since the plan is either made of one action repeated over multiple steps or all the actions in the plan are parallelizable")

with open(os.path.join(BASE_DIR,'{}_contrastive_commands.txt').format(problem_name),'w') as fo:
    fo.write("================LINEAR EXPERIMENTS================\n")
    for command in linear_commands:
        fo.write("------------------------\n")
        fo.write("echo \"%s\"\n" % command)
        fo.write("%s\n" % command)
    fo.write("------------------------\n")
    fo.write("================PARALLEL EXPERIMENTS================\n")
    for command in parallel_commands:
        fo.write("------------------------\n")
        fo.write("echo \"%s\"\n" % command)
        fo.write("%s\n" % command)