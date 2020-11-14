#!/usr/bin/env python3
from ortools.sat.python import cp_model

# This program tries to find an optimal assignment of interpreters to teacher mtg requests.
# Each interpreter includes their availability in a bit map for each day. (1 = available)
# Each teacher includes their meeting requests in a bit map for each day. (1 = meeting request)
# The optimal assignment maximizes the number of filled meeting requests.

MIN_WEEKLY_MTGS = 1
MAX_DAILY_MTGS = 4

def model(interp_avails, mtg_reqs, min_weekly_mtgs=MIN_WEEKLY_MTGS, max_daily_mtgs=MAX_DAILY_MTGS):
    num_interps = len(interp_avails)
    num_teachers = len(mtg_reqs)

    if not num_interps: return "No interpreter schedules found"
    if not num_teachers: return "No teacher schedules found"
    if max_daily_mtgs <= 0: return ""

    num_days = len(mtg_reqs[0])
    num_shifts = len(mtg_reqs[0][0])
    
    all_interps = range(num_interps)
    all_teachers = range(num_teachers)
    all_days = range(num_days)
    all_shifts = range(num_shifts)
    
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
        shifts_worked_weekly = 0
        for t in all_teachers:
            for d in all_days:
                shifts_worked_today = 0
                for s in all_shifts:
                    if (interp_avails[i][d][s] == 1 and mtg_reqs[t][d][s] == 1):
                        if (shifts_worked_today < max_daily_mtgs):
                            shifts_worked_today += 1
                            shifts_worked_weekly += 1
            min_shifts_worked_weekly = min(min_shifts_worked_weekly, shifts_worked_weekly)

    # Get average meeting requests per interpreter
    tot_mtg_reqs = sum(mtg_reqs[t][d][s] for t in all_teachers for d in all_days for s in all_shifts)
    avg_weekly_mtgs = tot_mtg_reqs // num_interps

    # Determine number of weekly meetings for each interpreter
    num_weekly_mtgs = min(avg_weekly_mtgs, min_shifts_worked_weekly)
    num_weekly_mtgs = max(num_weekly_mtgs, min_weekly_mtgs)
    #num_weekly_mtgs = min(num_weekly_mtgs, max_daily_mtgs*7)

    # Model counts (1,1) and (0,0) as TRUE matches
    num_weekly_mtgs *= 2

    # Interpreters work a fair amount of shifts
    for i in all_interps:
        if (num_weekly_mtgs == avg_weekly_mtgs):
            model.Add(sum(shifts[(i, t, d, s)] for t in all_teachers for d in all_days for s in all_shifts) >= num_weekly_mtgs)
        else:
            model.Add(sum(shifts[(i, t, d, s)] for t in all_teachers for d in all_days for s in all_shifts) >= num_weekly_mtgs)

    # Determine number of weekly meetings for each teacher
    tot_interp_avails = sum(interp_avails[i][d][s] for i in all_interps for d in all_days for s in all_shifts)
    
    if (tot_mtg_reqs > tot_interp_avails): 
        num_weekly_mtgs = 0

    # Teachers get a fair amount of interpreters
    for t in all_teachers:
        if (num_weekly_mtgs == avg_weekly_mtgs):
            model.Add(sum(shifts[(i, t, d, s)] for i in all_interps for d in all_days for s in all_shifts) >= num_weekly_mtgs)
        else:
            model.Add(sum(shifts[(i, t, d, s)] for i in all_interps for d in all_days for s in all_shifts) >= num_weekly_mtgs)

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
        for t in all_teachers:
            for d in all_days:
                for s in all_shifts:
                    if solver.Value(shifts[(i, t, d, s)]) == 1 and interp_avails[i][d][s] == 1 and mtg_reqs[t][d][s] == 1:
                        temp = "Interpreter: %s Teacher: %s Day: %s Shift: %s\n"%(i+1, t+1, d+1, s+1) 
                        res += temp
        res += "\n"

    return res.rstrip()


if __name__ == '__main__':
    # Set MIN_WEEKLY_MTGS and MAX_DAILY_MTGS
    # Read interp_avails and mtg_reqs from file
    # res = model(interp_avails, mtg_reqs)
    # Write res to file
    
    interp_avails = []
    mtg_reqs = []
    res = model(interp_avails, mtg_reqs)