#!/usr/bin/env python3
from ortools.sat.python import cp_model


def main():
    MIN_WEEKLY_MTGS = 1
    MAX_DAILY_MTGS = 1

    # This program tries to find an optimal assignment of interpreters to teacher mtg requests.
    # Each interpreter includes their availability in a bit map for each day. (1 = available)
    # Each teacher includes their meeting requests in a bit map for each day. (1 = meeting request)
    # The optimal assignment maximizes the number of filled meeting requests.
    mtg_reqs = [[[1, 1], [0, 1], [0, 1], [0, 1], [0, 1], [0, 1], [0, 1]]]
    interp_avails = [[[1,1],[0,1],[0,1],[0,1],[0,1],[0,1],[0,1]],
                [[0,1],[0,1],[0,0],[0,0],[0,1],[0,1],[0,1]]]
    
    num_interps = len(interp_avails)
    num_teachers = len(mtg_reqs)
    num_days = len(mtg_reqs[0])
    num_shifts = len(mtg_reqs[0][0])
    
    all_interps = range(num_interps)
    all_teachers = range(num_teachers)
    all_days = range(num_days)
    all_shifts = range(num_shifts)
    
    # Creates the model.
    model = cp_model.CpModel()

    # Creates shift variables.
    # shifts[(i, t, d, s)]: interpreter 'i' paired with teacher 't' works shift 's' on day 'd'.
    # Each interpter has a shift-map for every teacher, which provides a boolean variable for each shift of each day.
    shifts = {}
    for i in all_interps:
        for t in all_teachers:
            for d in all_days:
                for s in all_shifts:
                    shifts[(i, t, d, s)] = model.NewBoolVar('shift_i%it%id%is%i' % (i, t, d, s))

    # Each shift is assigned at most one interpreter.
    for t in all_teachers:
        for d in all_days:
            for s in all_shifts:
                model.Add(sum(shifts[(i, t, d, s)] for i in all_interps) <= 1)

    # Interpreters cannot be booked with multiple teachers at the same time
    for i in all_interps:
        for d in all_days:
            for s in all_shifts:
                model.Add(sum(shifts[(i, t, d, s)] for t in all_teachers) <= 1)

    # Get min number of weekly meetings an interpreter able to fill
    min_shifts_worked_weekly = float('inf')
    for i in all_interps:
        shifts_worked_weekly = 0
        for t in all_teachers:
            for d in all_days:
                shifts_worked_today = 0
                for s in all_shifts:
                    if (interp_avails[i][d][s] == 1 and mtg_reqs[t][d][s] == 1):
                        if (shifts_worked_today < MAX_DAILY_MTGS):
                            shifts_worked_today += 1
                            shifts_worked_weekly += 1
        min_shifts_worked_weekly = min(min_shifts_worked_weekly, shifts_worked_weekly)

    # Get average meeting requests per interpreter
    tot_mtg_reqs = sum(mtg_reqs[t][d][s] for t in all_teachers for d in all_days for s in all_shifts)
    avg_weekly_mtgs = tot_mtg_reqs // num_interps

    # Determine number of weekly meetings for each interpreter
    num_weekly_mtgs = min(avg_weekly_mtgs, min_shifts_worked_weekly)
    num_weekly_mtgs = max(num_weekly_mtgs, MIN_WEEKLY_MTGS)
    num_weekly_mtgs = min(num_weekly_mtgs, MAX_DAILY_MTGS*7)

    # Try to distribute interpreters evenly
    # Partial constraint - Model infeasible if no interpreter able to work num_weekly_mtgs.
    for i in all_interps:
        if (num_weekly_mtgs == avg_weekly_mtgs):
            model.Add(sum(shifts[(i, t, d, s)] for t in all_teachers for d in all_days for s in all_shifts) == num_weekly_mtgs)
        else:
            model.Add(sum(shifts[(i, t, d, s)] for t in all_teachers for d in all_days for s in all_shifts) >= num_weekly_mtgs)


    # Interpreters work at most MAX_DAILY_MTGS per day.
    for i in all_interps:
        for d in all_days:
            model.Add(sum(shifts[(i, t, d, s)] for t in all_teachers for s in all_shifts) <= MAX_DAILY_MTGS)

    # Try to distribute the shifts evenly, so that each nurse works
    # min_shifts_per_nurse shifts. If this is not possible, because the total
    # number of shifts is not divisible by the number of nurses, some nurses will
    # be assigned one more shift.
    '''
    min_shifts_per_nurse = (num_shifts * num_days) // num_nurses
    if num_shifts * num_days % num_nurses == 0:
        max_shifts_per_nurse = min_shifts_per_nurse
    else:
        max_shifts_per_nurse = min_shifts_per_nurse + 1
    for n in all_nurses:
        num_shifts_worked = 0
        for d in all_days:
            for s in all_shifts:
                num_shifts_worked += shifts[(n, d, s)]
        model.Add(min_shifts_per_nurse <= num_shifts_worked)
        model.Add(num_shifts_worked <= max_shifts_per_nurse)
    '''

    # Optimize the following objective function.
    # pylint: disable=g-complex-comprehension
    model.Maximize(
        sum(interp_avails[i][d][s] * mtg_reqs[t][d][s] * shifts[(i, t, d, s)] for i in all_interps
            for t in all_teachers for d in all_days for s in all_shifts))
    
    # Creates the solver and solve.
    solver = cp_model.CpSolver()
    solver.Solve(model)

    # Determine if model is infeasible or optimal
    #print(solver.StatusName())

    for i in all_interps:
        for t in all_teachers:
            for d in all_days:
                for s in all_shifts:
                    try:
                        if solver.Value(shifts[(i, t, d, s)]) == 1 and interp_avails[i][d][s] == 1 and mtg_reqs[t][d][s] == 1:
                            print('Interpreter:', i+1, 'Teacher:', t+1, 'Day:', d+1, 'Shift:', s+1)
                    except IndexError:
                        print('Index Error', i, t, d, s)
        print()

    # Statistics
    '''
    print()
    print('Statistics')
    print('  - Number of shift requests met = %i' % solver.ObjectiveValue(),
          '(out of', num_nurses * min_shifts_per_nurse, ')')
    print('  - wall time       : %f s' % solver.WallTime())
    '''


if __name__ == '__main__':
    main()