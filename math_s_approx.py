# method of successive approximations visualised
from manim import *
import numpy as np
import scipy.integrate as integrate

def F(x, y):
    return 2 * x * (y + 1)

def phi_n_calc(phi_n_p):
    def phi_n(x):
        return integrate.quad(lambda t: F(t, phi_n_p(t)), 0, x)[0]
    return phi_n

class SApprox(Scene):
    def construct(self):
        axes = Axes(x_range=(-2,2,0.5),
                    y_range=(-2,60,5))
        
        # move axes down a bit
        axes.scale(0.8)
        axes.move_to(DOWN*0.5)

        # plot functions
        odetex = MathTex("\dot{y}=2x(y+1), \ \ y(0)=0")
        self.play(Write(odetex), run_time=4)
        self.play(odetex.animate.move_to(UP*3))

        

        # outline process
        algotex = MathTex("\phi_n(x) = \int_0^x{\dot{y}(x,\phi_{n-1}(x))}\ \ dx")
        self.play(Write(algotex), run_time=4)
        self.play(algotex.animate.move_to(UP*2))

        self.play(algotex.animate.move_to(LEFT*3.5+UP*2.5), odetex.animate.move_to(LEFT*3.5+UP*3.3))
        self.play(algotex.animate.scale(0.7), odetex.animate.scale(0.7))

        self.play(Create(axes))

        solution = lambda x: np.exp(x**2)-1
        sol_curve = axes.plot(solution)

        phi_p = lambda x: 0*x

        phi_p_funcs = ["0","x^2","x^2+0.5x^4","x^2+0.5x^4+0.167x^6","x^2+0.5x^4+0.167x^6+0.0417x^8","e^{x^2}+1"]

        for i in range(0,5):
            phitex = MathTex(rf"\phi_{i}(x) = {phi_p_funcs[i]}", color=YELLOW)
            phitex.move_to(RIGHT*3.5+UP*3.2)
            phitex.scale(0.8)
            self.play(Write(phitex), run_time=3)
            phi_curve = axes.plot(phi_p,color=YELLOW)
            self.play(Create(phi_curve))
            if i<4:
                phi_n = phi_n_calc(phi_p)
                phi_p = phi_n

            self.play(Unwrite(phitex))
        
        phitex = MathTex(rf"y(x) = {phi_p_funcs[5]}", color=WHITE)
        phitex.move_to(RIGHT*3.5+UP*3.2)
        phitex.scale(0.8)
        self.play(Write(phitex), run_time=3)
        self.play(Create(sol_curve))
        self.wait(2)


class SuccessiveApprox(ThreeDScene):
    def construct(self):
        self.axes = ThreeDAxes(
            x_range=(-2,2,0.5),
            y_range=(-2,2,5),
            z_range=(-20,20,10),
            x_length = 10,
            y_length = 10,
            z_length = 10
            )
        
        # for axes aspect ratio such that the different ranges are scaled
        self.axes.set_aspect("equal")
        
        self.set_camera_orientation(phi=45*DEGREES, theta=-45*DEGREES, distance=10)
        
        surface = lambda x: np.array([x,x,2*x*(x+1)])
        phi_0 = lambda x: 0 * x

        #phi_1 = phi_n_calc(phi_0, surface)

        surface = ParametricFunction(surface, color=RED, t_range=(-2,2))

        self.play(Create(self.axes))
        #self.begin_ambient_camera_rotation(0.9)
        self.play(Create(surface), run_time=8)
        self.wait(2)



        #self.begin_ambient_camera_rotation(rate=2)
        #self.wait(5)
        #self.stop_ambient_camera_rotation()
        