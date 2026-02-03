from manim import *
import numpy as np
from scipy.integrate import odeint
from scipy.integrate import solve_ivp

def lorzenz_system(t, state, sigma=10, rho=28, beta=8/3):
    x,y,z = state
    dxdt = sigma * (y-x)
    dydt = x * (rho-z) -y
    dzdt = x * y - beta*z
    return [dxdt, dydt, dzdt]

def ode_solution_points(function, state0, time, dt=0.01):
    solution = solve_ivp(
        function, 
        t_span=(0,time),
        y0=state0,
        t_eval=np.arrange(0,time,dt)
    )
    return solution.y.T

class HelloWorld(Scene):
    def construct(self):
        circle = Circle()
        square = Square()
        self.add(circle)
        self.add(square)

        text = Text("hello dumbass")

        self.play(Write(text, run_time=3))

        # transform one element into another
        # default rate_func=smooth
        self.play(Transform(text[0], circle),run_time=5,rate_func=linear)
        
        self.add(ThreeDAxes())

class LorentzChaos(Scene):
    def construct(self):
        axes = ThreeDAxes(
            x_range=(-50,50,5),
            y_range=(-50,50,5),
            z_range=(-0,50,5),
        )
        axes.set_width(config.frame_width)
        axes.center()

        #axes.reorient(43,76,1,IN,10)
        self.add(axes)

        # start displaying lorenz solutions
        state0 = [0,0,0]
