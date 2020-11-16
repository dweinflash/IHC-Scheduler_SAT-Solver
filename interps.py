#!/usr/bin/env python3
import json
from statistics import median
from ortools.sat.python import cp_model

# This program tries to find an optimal assignment of interpreters to teacher mtg requests.
# Each interpreter includes their availability in a bit map for each day of week (1 = available).
# Each teacher includes their meeting requests in a bit map for each day of week (1 = meeting request).
# The optimal assignment maximizes the number of filled meeting requests subject so some practical and fair constraints.

MIN_WEEKLY_MTGS = 1
MAX_DAILY_MTGS = 2

class PartialSolutionPrinter(cp_model.CpSolverSolutionCallback):
    """Print intermediate solutions."""

    def __init__(self, shifts, interp_avails, mtg_reqs, num_interps, num_teachers, num_days, num_shifts, sols):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self._shifts = shifts
        self._interp_avails = interp_avails
        self._mtg_reqs = mtg_reqs
        self._num_interps = num_interps
        self._num_teachers = num_teachers
        self._num_days = num_days
        self._num_shifts = num_shifts
        self._solutions = set(sols)
        self._solution_count = 0

    def on_solution_callback(self):
        if self._solution_count in self._solutions:
            print('Solution %i' % self._solution_count)
            for i in range(self._num_interps):
                for t in range(self._num_teachers):
                    for d in range(self._num_days):
                        for s in range(self._num_shifts):
                            if self.Value(self._shifts[(i, t, d, s)]) == 1 and self._interp_avails[i][d][s] == 1 and self._mtg_reqs[t][d][s] == 1:
                                temp = "Interpreter: %s Teacher: %s Day: %s Shift: %s\n"%(i+1, t+1, d+1, s+1) 
                                print(temp)
            print()
        self._solution_count += 1

    def solution_count(self):
        return self._solution_count

def model(interp_avails, mtg_reqs, min_weekly_mtgs=MIN_WEEKLY_MTGS, max_daily_mtgs=MAX_DAILY_MTGS):
    if max_daily_mtgs <= 0: return ""

    num_interps = len(interp_avails)
    num_teachers = len(mtg_reqs)
    num_days = len(mtg_reqs[0])
    num_shifts = len(mtg_reqs[0][0])
    
    all_interps = range(num_interps)
    all_teachers = range(num_teachers)
    all_days = range(num_days)
    all_shifts = range(num_shifts)
    
    tot_interp_avails = sum(interp_avails[i][d][s] for i in all_interps for d in all_days for s in all_shifts)
    tot_mtg_reqs = sum(mtg_reqs[t][d][s] for t in all_teachers for d in all_days for s in all_shifts)

    # Create the model
    model = cp_model.CpModel()

    # Create shift variables
    # shifts[(i, t, d, s)]: interpreter 'i' paired with teacher 't' works shift 's' on day 'd'
    shifts = {}
    for i in all_interps:
        for t in all_teachers:
            for d in all_days:
                for s in all_shifts:
                    shifts[(i, t, d, s)] = model.NewBoolVar('shift_i%it%id%is%i' % (i, t, d, s))

    # Each shift is assigned at most one interpreter
    for t in all_teachers:
        for d in all_days:
            for s in all_shifts:
                model.Add(sum(shifts[(i, t, d, s)] for i in all_interps) <= 1)

    # Interpreters cannot be booked with multiple teachers at the same time
    for i in all_interps:
        for d in all_days:
            for s in all_shifts:
                model.Add(sum(shifts[(i, t, d, s)] for t in all_teachers) <= 1)

    # Interpreters work at most max_daily_mtgs per day
    for i in all_interps:
        for d in all_days:
            model.Add(sum(shifts[(i, t, d, s)] for t in all_teachers for s in all_shifts) <= max_daily_mtgs)

    # Get min number of weekly meetings an interpreter able to fill
    min_shifts_worked_weekly = float('inf')
    for i in all_interps:
        shifts_worked_weekly = [[0 for s in all_shifts] for d in all_days]
        for t in all_teachers:
            for d in all_days:
                for s in all_shifts:
                    if (interp_avails[i][d][s] == 1 and mtg_reqs[t][d][s] == 1):
                        shifts_worked_today = sum(shifts_worked_weekly[d])
                        if (shifts_worked_today < max_daily_mtgs):
                            shifts_worked_weekly[d][s] = 1
        sum_shifts_worked_weekly = sum(shifts_worked_weekly[d][s] for d in all_days for s in all_shifts)
        min_shifts_worked_weekly = min(min_shifts_worked_weekly, sum_shifts_worked_weekly)

    # Determine number of weekly meetings for each interpreter
    avg_weekly_mtgs = tot_mtg_reqs // num_interps
    num_weekly_mtgs = min(avg_weekly_mtgs, min_shifts_worked_weekly)

    # Determine number of weekly meetings for each teacher
    if (tot_mtg_reqs > tot_interp_avails or num_teachers > num_interps): 
        num_weekly_mtgs = num_weekly_mtgs // num_teachers
        
    num_weekly_mtgs = max(num_weekly_mtgs, min_weekly_mtgs)

    # Interpreters work a fair amount of shifts
    for i in all_interps:
        model.Add(sum(shifts[(i, t, d, s)] for t in all_teachers for d in all_days for s in all_shifts) >= num_weekly_mtgs)
        if (num_interps > 1):
            model.Add(sum(shifts[(i, t, d, s)] for t in all_teachers for d in all_days for s in all_shifts) <= 
                max(num_weekly_mtgs+1, tot_mtg_reqs - (num_interps-1)*num_weekly_mtgs))

    # Teachers get a fair amount of interpreters
    for t in all_teachers:
        model.Add(sum(shifts[(i, t, d, s)] for i in all_interps for d in all_days for s in all_shifts) >= num_weekly_mtgs)
        if (num_teachers > 1):
            model.Add(sum(shifts[(i, t, d, s)] for i in all_interps for d in all_days for s in all_shifts) <= 
                max(num_weekly_mtgs+1, tot_mtg_reqs - (num_interps-1)*num_weekly_mtgs))

    # Optimize the objective function
    # pylint: disable=g-complex-comprehension
    model.Maximize(
        sum(interp_avails[i][d][s] * mtg_reqs[t][d][s] * shifts[(i, t, d, s)] for i in all_interps
            for t in all_teachers for d in all_days for s in all_shifts))
    
    # Create the solver and solve
    solver = cp_model.CpSolver()
    solver.Solve(model)

    # Determine if model is INFEASIBLE or OPTIMAL
    status = solver.StatusName()
    res = ""
    if (status == 'INFEASIBLE'):
        res = status
        return res

    # Get model results
    for i in all_interps:
        for d in all_days:
            for s in all_shifts:
                for t in all_teachers:
                    if solver.Value(shifts[(i, t, d, s)]) == 1 and interp_avails[i][d][s] == 1 and mtg_reqs[t][d][s] == 1:
                        res += "Interpreter: %2s Teacher: %2s Day: %2s Shift: %2s\n"%(i+1, t+1, d+1, s+1)
        res += "\n"

    return res.rstrip()

def statistics(results, interp_avails, mtg_reqs):
    stats = ""
    
    # Total meeting requests
    teachers = range(len(mtg_reqs))
    days = range(len(mtg_reqs[0]))
    shifts = range(len(mtg_reqs[0][0]))
    tot_mtg_reqs = sum(mtg_reqs[t][d][s] for t in teachers for d in days for s in shifts)
    stats += "Total Meeting Requests: %s\n" % tot_mtg_reqs

    # Meetings matched
    mtgs_matched = res.count('Shift')
    stats += "Total Meetings Matched: %s\n\n" % mtgs_matched

    # Global variables
    stats += "Min Weekly Meetings: %s\n" % MIN_WEEKLY_MTGS
    stats += "Max Daily Meetings:  %s\n\n" % MAX_DAILY_MTGS

    # Count meetings per interpreter
    num_interpreters = len(interp_avails)
    interp_mtgs = [0] * num_interpreters
    
    for i in range(num_interpreters):
        interp_mtgs[i] = res.count("Interpreter: %2s"%str(i+1))

    # Meetings per interpreter stats
    min_mtgs = min(interp_mtgs)
    med_mtgs = median(interp_mtgs)
    avg_mtgs = round(sum(interp_mtgs) / float(num_interpreters), 1)
    max_mtgs = max(interp_mtgs)

    stats += "Min Meetings per Interpreter: %s\n" % min_mtgs
    stats += "Med Meetings per Interpreter: %s\n" % med_mtgs
    stats += "Avg Meetings per Interpreter: %s\n" % avg_mtgs
    stats += "Max Meetings per Interpreter: %s\n\n" % max_mtgs

    return stats

if __name__ == '__main__':
    interp_avails = None
    mtg_reqs = None

    with open('interps_map.txt', 'r') as file:
        interp_avails = file.read().replace('\n', '')
        interp_avails = json.loads(interp_avails)
    
    with open('mtg_reqs.txt', 'r') as file:
        mtg_reqs = file.read().replace('\n', '')
        mtg_reqs = json.loads(mtg_reqs)

    if (not interp_avails or not mtg_reqs):
        res = "Missing input files"
        stats = ""
    else:
        res = model(interp_avails, mtg_reqs)
        stats = statistics(res, interp_avails, mtg_reqs)

    with open("match_results.txt", "w") as file:
        file.write(stats)
        file.write(res)