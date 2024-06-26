import os
import sys
from pathlib import Path

from geophires_x.Economics import CalculateFinancialPerformance
from geophires_x.Model import Model
from tests.base_test_case import BaseTestCase


class EconomicsTestCase(BaseTestCase):
    def test_irr(self):
        """
        Test cases adapted from https://numpy.org/numpy-financial/latest/irr.html
        """

        def cumm_revenue(total_revenue):
            cumm_revenue = [total_revenue[0]] * len(total_revenue)
            cumm_revenue[1] = total_revenue[1]
            for i in range(2, len(total_revenue)):
                cumm_revenue[i] = cumm_revenue[i - 1] + total_revenue[i]
            return cumm_revenue

        def calc_irr(total_revenue):
            NPV, IRR, VIR, MOIC = CalculateFinancialPerformance(
                30, 5, total_revenue, cumm_revenue(total_revenue), 1000, 10
            )

            return IRR

        self.assertAlmostEqual(28.095, calc_irr([-100, 39, 59, 55, 20]), places=3)
        self.assertAlmostEqual(-9.55, calc_irr([-100, 0, 0, 74]), places=2)
        self.assertAlmostEqual(-8.33, calc_irr([-100, 100, 0, -7]), places=2)
        self.assertAlmostEqual(6.21, calc_irr([-100, 100, 0, 7]), places=2)
        self.assertAlmostEqual(8.86, calc_irr([-5, 10.5, 1, -8, 1]), places=2)

    def test_well_drilling_cost_correlation_tooltiptext(self):
        ec = self._new_model().economics
        self.assertEqual(
            ec.wellcorrelation.ToolTipText,
            'Select the built-in well drilling and completion cost correlation: '
            + '1: vertical small diameter, baseline; '
            + '2: deviated small diameter, baseline; '
            + '3: vertical large diameter, baseline; '
            + '4: deviated large diameter, baseline; '
            + '5: Simple; '
            + '6: vertical small diameter, intermediate1; '
            + '7: vertical small diameter, intermediate2; '
            + '8: deviated small diameter, intermediate1; '
            + '9: deviated small diameter, intermediate2; '
            + '10: vertical large diameter, intermediate1; '
            + '11: vertical large diameter, intermediate2; '
            + '12: deviated large diameter, intermediate1; '
            + '13: deviated large diameter, intermediate2; '
            + '14: vertical open-hole, small diameter, ideal; '
            + '15: deviated liner, small diameter, ideal; '
            + '16: vertical open-hole, large diameter, ideal; '
            + '17: deviated liner, large diameter, ideal',
        )

    def _new_model(self) -> Model:
        stash_cwd = Path.cwd()
        stash_sys_argv = sys.argv

        sys.argv = ['']

        m = Model(enable_geophires_logging_config=False)

        sys.argv = stash_sys_argv
        os.chdir(stash_cwd)

        return m
