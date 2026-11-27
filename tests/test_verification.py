"""Substantive analytic identities and numerical convergence checks.

Test methods are counted once; sampled coordinates are not counted as tests.
"""
import math
import unittest

from vortex_thread import model as m
from vortex_thread.diagnostics import (POINTS, decay_samples,
                                        finite_difference_convergence,
                                        trajectory_convergence)


class AnalyticChecks(unittest.TestCase):
    def test_pressure_cancels_advection_with_required_sign(self):
        # Differentiate the velocity explicitly, without using model.gradient.
        for x,y in POINTS:
            a = math.exp(-2*0.25*0.7)
            u,v = m.velocity(x,y,0.7,0.25)
            adv = (u*(-a*math.sin(x)*math.sin(y))+v*a*math.cos(x)*math.cos(y),
                   u*(-a*math.cos(x)*math.cos(y))+v*a*math.sin(x)*math.sin(y))
            dp = (a*a*math.sin(2*x)/2,a*a*math.sin(2*y)/2)
            self.assertLess(max(abs(adv[i]+dp[i]) for i in (0,1)),1e-15)
            h = 1e-5
            numerical_dp = ((m.pressure(x+h,y,.7,.25)-m.pressure(x-h,y,.7,.25))/(2*h),
                            (m.pressure(x,y+h,.7,.25)-m.pressure(x,y-h,.7,.25))/(2*h))
            self.assertLess(max(abs(numerical_dp[i]-dp[i]) for i in (0,1)),1e-10)

    def test_divergence_and_vorticity_from_velocity_differences(self):
        h = 1e-5
        for x,y in POINTS:
            xp,xm = m.velocity(x+h,y,.7,.25),m.velocity(x-h,y,.7,.25)
            yp,ym = m.velocity(x,y+h,.7,.25),m.velocity(x,y-h,.7,.25)
            self.assertLess(abs((xp[0]-xm[0]+yp[1]-ym[1])/(2*h)),1e-10)
            curl = (xp[1]-xm[1]-yp[0]+ym[0])/(2*h)
            self.assertAlmostEqual(curl,m.vorticity(x,y,.7,.25),delta=1e-10)

    def test_periodicity_and_zero_mean_pressure(self):
        for x,y in POINTS:
            self.assertLess(math.dist(m.velocity(x,y,.7,.25),m.velocity(x+2*math.pi,y-2*math.pi,.7,.25)),1e-15)
        n = 32
        pmean = sum(m.pressure(2*math.pi*i/n,2*math.pi*j/n,.7,.25)
                    for i in range(n) for j in range(n))/n**2
        self.assertLess(abs(pmean),1e-15)

    def test_amplitude_decay_and_effective_time_including_zero_viscosity(self):
        for nu in (0,.01,.25,2):
            for t in (0,.7,2):
                self.assertAlmostEqual(m.amplitude(t,nu),math.exp(-2*nu*t))
            # A numerical derivative of effective time must recover A.
            t,h = .7,1e-5
            dsdt = (m.effective_time(t+h,nu)-m.effective_time(t-h,nu))/(2*h)
            self.assertAlmostEqual(dsdt,m.amplitude(t,nu),delta=1e-9)
        self.assertEqual(m.effective_time(3,0),3)
        self.assertAlmostEqual(m.effective_time(2*math.log(2),.25),1)
        self.assertAlmostEqual(m.effective_time(1,1e-12),1,delta=2e-12)

    def test_first_integral_has_zero_material_derivative(self):
        for x,y in POINTS:
            u,v = m.velocity(x,y,.7,.25)
            self.assertLess(abs(-u*math.sin(x)*math.cos(y)-v*math.cos(x)*math.sin(y)),1e-15)

    def test_strain_is_trace_free_and_saddle_has_opposite_rates(self):
        a = m.amplitude(.7,.25)
        for x,y in POINTS:
            g = m.gradient(x,y,.7,.25)
            self.assertEqual(g[0][0]+g[1][1],0)
            self.assertEqual(g[0][1]+g[1][0],0)
        g = m.gradient(math.pi/2,math.pi/2,.7,.25)
        self.assertAlmostEqual(g[0][0],-a)
        self.assertAlmostEqual(g[1][1],a)
        # Local material factors have product one; finite segment width ratios
        # elsewhere are not a substitute for a material-area calculation.
        s = m.effective_time(2*math.log(2),.25)
        self.assertAlmostEqual(math.exp(-s)*math.exp(s),1)

    def test_segment_formula_initial_condition_and_short_time_rate(self):
        delta = .10
        for expanding in (False,True):
            self.assertAlmostEqual(m.segment_width(delta,0,.25,expanding),2*delta)
            h = 1e-6
            rate = (m.segment_width(delta,h,.25,expanding)-2*delta)/h
            expected = 2*math.sin(delta)*(1 if expanding else -1)
            self.assertAlmostEqual(rate,expected,delta=2e-7)

    def test_exact_paper_segment_values(self):
        t = 2*math.log(2)
        # The paper quotes six decimals; do not invent extra reference digits.
        self.assertAlmostEqual(m.segment_width(.10,t,.25),.073629,delta=.5e-6)
        self.assertAlmostEqual(m.segment_width(.10,t,.25,True),.540791,delta=.5e-6)

    def test_energy_enstrophy_and_dissipation(self):
        data = decay_samples()
        for row in data["rows"]:
            self.assertAlmostEqual(row["energy_sampled_mean"],row["energy_exact_mean"],delta=1e-13)
            self.assertAlmostEqual(row["enstrophy_sampled_mean"],row["enstrophy_exact_mean"],delta=1e-13)
        t,nu,h = .7,.25,1e-5
        dedt = (m.energy(t+h,nu)-m.energy(t-h,nu))/(2*h)
        self.assertAlmostEqual(dedt,-2*nu*m.enstrophy(t,nu),delta=1e-10)
        self.assertEqual(m.energy(100,0),.25)

    def test_invalid_physical_and_integrator_inputs_raise(self):
        for t,nu in ((-1,.25),(1,-.1),(float("nan"),1),(1,float("inf"))):
            with self.assertRaises(ValueError): m.amplitude(t,nu)
        for steps in (0,-1,True,1.5):
            with self.assertRaises(ValueError): m.integrate(0,0,1,.25,steps)
        for delta in (0,-1,math.pi,float("nan")):
            with self.assertRaises(ValueError): m.segment_width(delta,1,.25)


class NumericalChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fd = finite_difference_convergence()
        cls.paths = trajectory_convergence()

    def test_centered_derivatives_converge_at_second_order(self):
        for row in self.fd[1:]:
            for name in ("gradient","laplacian","time_derivative"):
                self.assertGreater(row["observed_orders"][name],1.95)
                self.assertLess(row["observed_orders"][name],2.05)

    def test_momentum_residual_converges_and_divergence_stays_small(self):
        for row in self.fd[1:]:
            self.assertGreater(row["observed_orders"]["momentum_residual"],1.95)
            self.assertLess(row["observed_orders"]["momentum_residual"],2.05)
        self.assertLess(max(row["max_absolute_errors"]["divergence"] for row in self.fd),1e-12)

    def test_rk4_converges_on_exact_contracting_and_expanding_segments(self):
        for row in self.paths["rows"][1:]:
            for name in ("contracting","expanding"):
                self.assertGreater(row["observed_orders"][name],3.7)
        for segment in self.paths["rows"][-1]["segments"].values():
            self.assertLess(segment["absolute_error"],1e-8)
            self.assertLess(segment["max_transverse_drift"],1e-14)

    def test_rk4_generic_trajectory_convergence_and_first_integral(self):
        for row in self.paths["rows"][1:]:
            self.assertGreater(row["observed_orders"]["generic_trajectory"],3.7)
        last = self.paths["rows"][-1]
        self.assertLess(last["generic_error_against_refined_rk4"],1e-8)
        self.assertLess(last["first_integral_max_absolute_drift"],1e-8)

    def test_deformation_preserves_area_and_agrees_with_particle_map(self):
        x,y,t,nu,steps = .23,.71,2*math.log(2),.25,128
        q,f = m.integrate_deformation(x,y,t,nu,steps)
        self.assertLess(math.dist(q,m.integrate(x,y,t,nu,steps)),1e-14)
        eps = 1e-5
        xp,xm = m.integrate(x+eps,y,t,nu,steps),m.integrate(x-eps,y,t,nu,steps)
        yp,ym = m.integrate(x,y+eps,t,nu,steps),m.integrate(x,y-eps,t,nu,steps)
        for i in (0,1):
            self.assertAlmostEqual(f[i][0],(xp[i]-xm[i])/(2*eps),delta=1e-8)
            self.assertAlmostEqual(f[i][1],(yp[i]-ym[i])/(2*eps),delta=1e-8)
        self.assertLess(self.paths["rows"][-1]["deformation_max_absolute_determinant_error"],1e-8)


if __name__ == "__main__":
    unittest.main()
