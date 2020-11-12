#!/usr/bin/env python3
from ortools.sat.python import cp_model


def main():
    # This program tries to find an optimal assignment of interpreters to teacher mtg requests.
    # Each interpreter includes their availability in a bit map for each day. (1 = available)
    # Each teacher includes their meeting requests in a bit map for each day. (1 = meeting request)
    # The optimal assignment maximizes the number of filled meeting requests.
    interp_avails = [[[1, 0], [1, 0], [1, 0], [1, 0], [1, 0], [1, 0], [1, 0]],
                    [[0, 1], [0, 1], [0, 1], [0, 1], [0, 1], [0, 1], [0, 1]],
                    [[1, 0], [1, 0], [1, 0], [1, 0], [1, 0], [1, 0], [1, 0]]]
    mtg_reqs = [[[0,1],[0,1],[0,1],[0,1],[0,1],[0,1],[0,1]],
                [[1,0],[0,0],[0,0],[0,0],[0,0],[1,0],[1,0]]]

    # TODO: Key error if all_teachers > all_interps
    # TODO: Assign interpreters evenly
    
    num_interps = len(interp_avails)
    num_teachers = len(mtg_reqs)
    num_days = len(mtg_reqs[0])
    num_shifts = len(mtg_reqs[0][0])
    all_interps = range(num_interps)
    all_shifts = range(num_shifts)
    all_teachers = range(num_teachers)
    all_days = range(num_days)

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
                    shifts[(i, t, d, s)] = model.NewBoolVar('shift_n%it%id%is%i' % (i, t, d, s))

    # Each shift is assigned to exactly one interpreter.
    for t in all_teachers:
        for d in all_days:
            for s in all_shifts:
                model.Add(sum(shifts[(i, t, d, s)] for i in all_interps) == 1)

    # Interpreters cannot be booked for the same meeting with different teachers.
    for i in all_interps:
        for d in all_days:
            for s in all_shifts:
                model.Add(sum(shifts[(i, t, d, s)] for t in all_teachers) <= 1)

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

    # pylint: disable=g-complex-comprehension
    model.Maximize(
        sum(interp_avails[i][d][s] * mtg_reqs[t][d][s] * shifts[(i, t, d, s)] for i in all_interps
            for t in all_teachers for d in all_days for s in all_shifts))
    # Creates the solver and solve.
    solver = cp_model.CpSolver()
    solver.Solve(model)
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