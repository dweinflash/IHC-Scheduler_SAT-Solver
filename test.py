#!/usr/bin/env python3

import unittest
from interps import model

MIN_WEEKLY_MTGS = 1
MAX_DAILY_MTGS = 1

class TestModel(unittest.TestCase):
    def group_results_by(self, res, key):
        # Interps or teachers in list grouped according to num 
        # [ [interp1,], [interp2,], ..]
        # [ [teacher1,], [teacher2,], ..]

        group = []
        res = res.split('\n')

        if (key == "Interpreters"):
            idx = 0
        else:
            idx = 12

        for r in res:
            if len(r) == 0: continue
            
            num = r[r.index(':', idx)+2]
            num = int(num)

            if (len(group) < num):
                group.append([])

            temp = group[num-1]
            temp.append(r)
            group[num-1] = temp
        
        return group

    def test_no_interpreters(self):
        """
        Test no interp calendars
        """
        interp_avails = []
        mtg_reqs = [
            [[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0]]
        ]

        res = model(interp_avails, mtg_reqs, MIN_WEEKLY_MTGS, MAX_DAILY_MTGS)
        self.assertEqual(res, "No interpreter schedules found")

    def test_no_teachers(self):
        """
        Test no teacher calendars
        """
        interp_avails = [
            [[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0]]
        ]
        mtg_reqs = []

        res = model(interp_avails, mtg_reqs, MIN_WEEKLY_MTGS, MAX_DAILY_MTGS)
        self.assertEqual(res, "No teacher schedules found")

    def test_no_interpreter_available(self):
        """
        Test interpreter unable to attend any meeting requests
        """
        interp_avails = [
            [[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0]]
        ]
        mtg_reqs = [
            [[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0]]
        ]

        res = model(interp_avails, mtg_reqs, MIN_WEEKLY_MTGS, MAX_DAILY_MTGS)
        self.assertEqual(res, "")
    
    def test_no_meeting_requests(self):
        """
        Test no meeting requests from teacher
        """
        interp_avails = [
            [[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0]]
        ]
        mtg_reqs = [
            [[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0]]
        ]

        res = model(interp_avails, mtg_reqs, MIN_WEEKLY_MTGS, MAX_DAILY_MTGS)
        self.assertEqual(res, "")

    def test_infeasible_weekly_mtgs(self):
        """
        Test model infeasible if min_weekly_mtgs impossible
        """
        interp_avails = [
            [[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0]]
        ]
        mtg_reqs = [
            [[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0]]
        ]

        min_weekly_mtgs = 8
        max_daily_mtgs = 1

        res = model(interp_avails, mtg_reqs, min_weekly_mtgs, max_daily_mtgs)
        self.assertEqual(res, "INFEASIBLE")
    
    def test_zero_max_daily_mtgs(self):
        """
        Test model if max_daily_mtgs is 0
        """
        interp_avails = [
            [[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0]]
        ]
        mtg_reqs = [
            [[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0]]
        ]

        min_weekly_mtgs = 1
        max_daily_mtgs = 0

        res = model(interp_avails, mtg_reqs, min_weekly_mtgs, max_daily_mtgs)
        self.assertEqual(res, "")

    def test_max_daily_mtgs(self):
        """
        Test interpreter unable to work more than max_daily_mtgs per day
        """
        interp_avails = [
            [[1,1],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0]]
        ]
        mtg_reqs = [
            [[1,1],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0]]
        ]

        min_weekly_mtgs = 1
        max_daily_mtgs = 1

        res = model(interp_avails, mtg_reqs, min_weekly_mtgs, max_daily_mtgs)
        res_interps = self.group_results_by(res, "Interpreters")
        res_interps_num = len(res_interps)
        res_shifts_num = len(res_interps[0])
        
        self.assertEqual(res_interps_num, 1)
        self.assertEqual(res_shifts_num, 1)

    def test_meeting_has_at_most_one_interp(self):
        """
        Test model if two interps able to attend same meeting
        """
        interp_avails = [
            [[1,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0]],
            [[1,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0]]
        ]
        mtg_reqs = [
            [[1,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0]]
        ]

        res = model(interp_avails, mtg_reqs)
        res_interps = self.group_results_by(res, "Interpreters")
        res_interps_num = len(res_interps)
        
        self.assertEqual(res_interps_num, 1)
    
    def test_interps_not_over_booked(self):
        """
        Test interpreter not booked at same time with two diff teachers
        """
        interp_avails = [
            [[1,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0]]
        ]
        mtg_reqs = [
            [[1,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0]],
            [[1,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0]]
        ]

        res = model(interp_avails, mtg_reqs)
        res_interps = self.group_results_by(res, "Interpreters")
        res_interps_num = len(res_interps)
        res_shifts_num = len(res_interps[0])
        
        self.assertEqual(res_interps_num, 1)
        self.assertEqual(res_shifts_num, 1)

    def test_interps_share_mtgs(self):
        """
        Test interpreters share meetings
        """
        interp_avails = [
            [[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0]],
            [[0,0],[0,0],[0,0],[0,0],[0,0],[1,0],[1,0]]
        ]
        mtg_reqs = [
            [[1,0],[1,0],[1,0],[1,0],[1,0],[1,0],[1,0]]
        ]

        res = model(interp_avails, mtg_reqs)
        res_interps = self.group_results_by(res, "Interpreters")
        res_interps_num = len(res_interps)
        res_interps1_shifts = len(res_interps[0])
        res_interps2_shifts = len(res_interps[1])

        self.assertEqual(res_interps_num, 2)
        self.assertEqual(res_interps1_shifts, 5)
        self.assertEqual(res_interps2_shifts, 2)


if __name__ == '__main__':
    unittest.main()