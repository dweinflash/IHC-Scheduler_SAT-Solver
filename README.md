# IHC-Scheduler_SAT-Solver
- This program tries to find an optimal assignment of interpreters to teacher mtg requests.
- Each interpreter includes their availability in a bit map for each day of week (1 = available).
- Each teacher includes their meeting requests in a bit map for each day of week (1 = meeting request).
- The optimal assignment maximizes the number of filled meeting requests subject to availability, fairness and practicality constraints.
