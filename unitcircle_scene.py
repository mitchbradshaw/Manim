from manim import *
import numpy as np
from scipy.integrate import odeint
from scipy.integrate import solve_ivp

class unitcircle1(MovingCameraScene):
    def construct(self):
        axes = Axes(x_range=[-1.3,1.3], y_range=[-1.3,1.3],x_length=7.8,y_length=7.8)
        self.play(Create(axes), run_time=2)
        
        # unit circle as parametric curve
        circle_func = lambda t: np.array([np.cos(t), np.sin(t), 0])
        circle = axes.plot_parametric_curve(circle_func,t_range=[0,TAU],color=BLUE)       
        self.play(Create(circle), run_time=2)
        axes.add_coordinates()
        # add origin coordinates
        ogtext = Tex("(0, 0)").next_to(ORIGIN,RIGHT+DOWN)
        self.play(Write(ogtext), run_time=2)

        # add character
        theta = ValueTracker(0)
        token = always_redraw(
            lambda: Dot(
                circle.get_point_from_function(theta.get_value()),
                color=RED
            )
        )
        token_cd = always_redraw(
            lambda: Tex(f"({np.cos(theta.get_value()):.2f}, {(np.sin(theta.get_value())):.2f})")
                    .next_to(token, UP+RIGHT)
        )

        self.play(Create(token),Create(token_cd),run_time=4)
        radius = axes.c2p(1,1)[0] - axes.c2p(0,0)[0]

        # Add angle indicator
        angle_text = always_redraw(
            lambda: Tex(f"{round(theta.get_value() * (1/DEGREES))}\\textdegree")
            .next_to(ORIGIN,RIGHT*1.3+0.8*UP)
        )

        # Add angle sweep
        sweep = always_redraw(
            lambda: Sector(arc_center = axes.c2p(0,0),
                           radius=radius,
                           start_angle = 0,
                           angle=theta.get_value(),
                           color="YELLOW",
                           fill_opacity=0.3)
        )

        
        self.play(Create(sweep))
        self.play(Create(angle_text))

        # Move character
        self.play(theta.animate.set_value(230*DEGREES),run_time=8)

        # Reset to (1,0)
        # Change coordinates to (?,?)
        self.play(theta.animate.set_value(0*DEGREES),run_time=4)
        self.remove(token_cd)
        token_cd = always_redraw(
            lambda:Tex("(?, ?)").next_to(token, UP+RIGHT)
        )
        self.play(Create(token_cd))
        self.play(theta.animate.set_value(60*DEGREES),run_time=4)
        self.wait(4)
        # zoom into first quadrant:
        # axes.c2p converts axes coords to scene coords
        self.play(self.camera.frame.animate.scale(0.5).move_to(axes.c2p(0.5,0.5)),run_time=3)

class unitcircle2(MovingCameraScene):
    def construct(self):
        axes = Axes(x_range=[-1.3,1.3], y_range=[-1.3,1.3],x_length=7.8,y_length=7.8)
        # unit circle as parametric curve
        circle_func = lambda t: np.array([np.cos(t), np.sin(t), 0])
        circle = axes.plot_parametric_curve(circle_func,t_range=[0,TAU],color=BLUE)

        # add character
        theta = ValueTracker(60*DEGREES)
        token = always_redraw(
            lambda: Dot(
                circle.get_point_from_function(theta.get_value()),
                color=RED
            )
        )  
        token_cd = always_redraw(
            lambda:Tex("(?, ?)").next_to(token, UP+RIGHT)
        )

        radius = axes.c2p(1,1)[0] - axes.c2p(0,0)[0]

        # Add angle indicator
        angle_text = always_redraw(
            lambda: Tex(f"{round(theta.get_value() * (1/DEGREES))}\\textdegree")
            .next_to(ORIGIN,RIGHT*1.3+0.8*UP)
        )

        # Add angle sweep
        sweep = always_redraw(
            lambda: Sector(arc_center = axes.c2p(0,0),
                           radius=radius,
                           start_angle = 0,
                           angle=theta.get_value(),
                           color="YELLOW",
                           fill_opacity=0.3)
        )

        self.camera.frame.scale(0.5).move_to(axes.c2p(0.5,0.5))
        self.add(axes,circle,token_cd,token,angle_text,sweep)
        self.remove(token_cd)
        token_tex = Tex("(?,?)")
        token_cd = always_redraw(
            lambda:token_tex.next_to(token, UP*0.5+RIGHT)
        )
        
        self.play(Create(token_cd))

        # vertical line down
        vLine = Line(axes.c2p(0.5,0),axes.c2p(0.5,0.87),color="PINK")
        vTex = always_redraw(
            lambda: Tex("$y$").next_to(vLine,RIGHT)
        )
        
        self.play(Create(vLine),Write(vTex),run_time=3)
        token_tex = Tex("(?,$y$)")
        hLine = Line(axes.c2p(0,0.87),axes.c2p(0.5,0.87),color="PINK")
        hTex = always_redraw(
            lambda: Tex("$x$").next_to(hLine,DOWN)
        )
        
        self.play(Create(hLine),Write(hTex),run_time=3)
        token_tex = Tex("($x$,$y$)")
        self.play(hLine.animate.move_to(axes.c2p(0.25,0)),run_time=2)
        # hypotenuse
        hyp = Line(axes.c2p(0,0),axes.c2p(0.5,0.87),color="PINK")
        hypTex = always_redraw(
            lambda: Tex("1").move_to(axes.c2p(0.15,0.53))
        )
        rangle = RightAngle(hLine,vLine,0.3,color="GREEN",quadrant=(-1,1))
        self.wait(2)
        self.play(Create(hyp),Create(rangle),Write(hypTex),run_time=7)

        # fade out all others, centre on triangle
        self.play(FadeOut(circle),FadeOut(axes),FadeOut(sweep),FadeOut(token_cd),FadeOut(token),run_time=3)
        
        angle_tex_copy = angle_text.copy()
        angle_tex_copy.clear_updaters()

        hyp_tex_copy = hypTex.copy()
        hyp_tex_copy.clear_updaters()

        token_cpy = token.copy()
        token_cpy.clear_updaters()

        self.remove(angle_text)
        self.remove(hypTex)
        self.add(angle_tex_copy,hyp_tex_copy)
        
        triangle = VGroup(vLine,hLine,hyp,rangle,angle_tex_copy,hyp_tex_copy,token_cpy)
        og_coords = triangle.get_center()
        self.play(triangle.animate.move_to(ORIGIN+0.3*LEFT+1.5*UP),run_time=4)

        xTex = MathTex("\cos (60\\textdegree) = \\frac{x}{1} = x").move_to(UP*2+RIGHT*3).scale(0.7)
        yTex = MathTex("\sin (60\\textdegree) = \\frac{y}{1} = y").move_to(UP*1+RIGHT*3).scale(0.7)
        self.wait(6)
        self.play(Write(xTex),run_time=5)
        self.remove(xTex)
        xTex = MathTex("\cos (60\\textdegree) = x").move_to(UP*2+RIGHT*3).scale(0.7)
        self.play(Write(xTex),run_time=3)
        self.play(Write(yTex),run_time=4)
        self.remove(yTex)
        yTex = MathTex("\sin (60\\textdegree) = y").move_to(UP*1+RIGHT*3).scale(0.7)
        self.play(Write(yTex),run_time=1)

        cords = MathTex("(\cos(60),\sin(60))").scale(0.5).next_to(token_cpy)
        self.play(Write(cords),run_time=3)
        self.wait(5)
        self.remove(cords,token_cpy)
        self.remove(xTex,yTex)
        self.play(triangle.animate.move_to(og_coords),run_time=3)
        token_tex = MathTex("(\cos(60),\sin(60))").scale(0.5)
        token_cd =  always_redraw(
            lambda:token_tex.next_to(token, UP*0.5+RIGHT)
        )
        self.play(FadeIn(axes),FadeIn(circle),FadeIn(token),FadeIn(token_cd),run_time=3)
        self.remove(angle_tex_copy)
        self.add(angle_text)
        self.play(FadeOut(hTex),FadeOut(vTex),FadeOut(hyp_tex_copy),FadeOut(rangle),FadeOut(hLine),FadeOut(vLine),FadeIn(sweep),run_time=2)

class unitcircle3(MovingCameraScene):
    def construct(self):
        axes = Axes(x_range=[-1.3,1.3], y_range=[-1.3,1.3],x_length=7.8,y_length=7.8)
        # unit circle as parametric curve
        circle_func = lambda t: np.array([np.cos(t), np.sin(t), 0])
        circle = axes.plot_parametric_curve(circle_func,t_range=[0,TAU],color=BLUE)

        # add character
        theta = ValueTracker(60*DEGREES)
        token = always_redraw(
            lambda: Dot(
                circle.get_point_from_function(theta.get_value()),
                color=RED
            )
        )  
        
        token_cd = always_redraw(
            lambda:MathTex(f"(\cos({round(theta.get_value()*(1/DEGREES))}),\sin({round(theta.get_value()*(1/DEGREES))}))").scale(0.5).next_to(token, UP*0.5+RIGHT)
        )

        radius = axes.c2p(1,1)[0] - axes.c2p(0,0)[0]

        # Add angle indicator
        angle_text = always_redraw(
            lambda: Tex(f"{round(theta.get_value() * (1/DEGREES))}\\textdegree")
            .next_to(ORIGIN,RIGHT*1.3+0.8*UP)
        )

        # Add angle sweep
        sweep = always_redraw(
            lambda: Sector(arc_center = axes.c2p(0,0),
                           radius=radius,
                           start_angle = 0,
                           angle=theta.get_value(),
                           color="YELLOW",
                           fill_opacity=0.3)
        )

        self.camera.frame.scale(0.5).move_to(axes.c2p(0.5,0.5))
        hyp = always_redraw(
            lambda: Line(axes.c2p(0,0),circle.get_point_from_function(theta.get_value()),
                         color="PINK"))
        
        self.add(axes,circle,token_cd,token,angle_text,sweep,hyp)
        self.play(self.camera.frame.animate.scale(2).move_to(axes.c2p(0,0)),run_time=2)
        
        self.play(theta.animate.set_value(172*DEGREES),run_time=2)
        self.play(theta.animate.set_value(-47*DEGREES),run_time=2)
        self.play(theta.animate.set_value(0),run_time=2)

        self.play(theta.animate.set_value(90*DEGREES),run_time=5)
        cds = MathTex("(0,1)").move_to(axes.c2p(0,1)+0.5*UP+RIGHT)
        self.play(Create(cds),run_time=2)
        self.wait(5)
        self.play(theta.animate.set_value(180*DEGREES),run_time=3)
        cds = MathTex("(-1, 0)").move_to(axes.c2p(-1,0)+LEFT+UP*0.5)
        self.play(Create(cds),run_time=2)
        self.wait(3)
        self.play(theta.animate.set_value(270*DEGREES),run_time=4)
        cds = MathTex("(0,-1)").move_to(axes.c2p(0,-1)+0.5*DOWN+RIGHT)
        self.play(Create(cds),run_time=4)

        self.play(theta.animate.set_value(720*DEGREES),run_time=19)
        
class unitcircle4(MovingCameraScene):
    def construct(self):
        axes = Axes(x_range=[-1.3,1.3], y_range=[-1.3,1.3],x_length=7.8,y_length=7.8)
        # unit circle as parametric curve
        circle_func = lambda t: np.array([np.cos(t), np.sin(t), 0])
        circle = axes.plot_parametric_curve(circle_func,t_range=[0,TAU],color=BLUE)

        # add character
        theta = ValueTracker(60*DEGREES)
        token = always_redraw(
            lambda: Dot(
                circle.get_point_from_function(theta.get_value()),
                color=RED
            )
        )  
        
        token_cd = always_redraw(
            lambda:MathTex(f"(\cos({round(theta.get_value()*(1/DEGREES))}),\sin({round(theta.get_value()*(1/DEGREES))}))").scale(0.5).next_to(token, UP*0.5+RIGHT)
        )

        radius = axes.c2p(1,1)[0] - axes.c2p(0,0)[0]

        # Add angle indicator
        angle_text = always_redraw(
            lambda: Tex(f"{round(theta.get_value() * (1/DEGREES))}\\textdegree")
            .move_to(axes.c2p(0.25,0.1))
        )

        # Add angle sweep
        sweep = always_redraw(
            lambda: Sector(arc_center = axes.c2p(0,0),
                           radius=radius,
                           start_angle = 0,
                           angle=theta.get_value(),
                           color="YELLOW",
                           fill_opacity=0.3)
        )

        
        hyp = always_redraw(
            lambda: Line(axes.c2p(0,0),circle.get_point_from_function(theta.get_value()),
                         color="PINK"))
        
        self.add(axes,circle,token_cd,token,angle_text,hyp)
      
        axGroup = VGroup(axes,circle,token,hyp,angle_text)
        self.play(axGroup.animate.scale(0.3).move_to(LEFT*3+UP*2.5),run_time=3)
        
        self.remove(angle_text)
        
        # Add angle indicator
        angle_text = always_redraw(
            lambda: Tex(f"{round(theta.get_value() * (1/DEGREES))}\\textdegree")
            .move_to(LEFT*4.5+UP*2.5)
        )

        self.add(angle_text)

        self.play(theta.animate.set_value(0),run_time=1)    

        sinAx = Axes(x_range=[0,9], y_range=[-1.3,1.3],x_length=4.2,y_length=2.3).move_to(RIGHT*2.5+UP*2.5)
        cosAx = Axes(x_range=[0,9], y_range=[-1.3,1.3],x_length=4.2,y_length=2.3).rotate(-90*DEGREES).move_to(LEFT*3+DOWN)

        costex = MathTex("\cos(\\theta)").set_color(RED).move_to(DOWN+LEFT)
        sintex = MathTex("\sin(\\theta)").set_color(GREEN).move_to(2.5*RIGHT+UP)

        self.play(Create(sinAx), run_time = 5)
        self.play(Write(sintex), run_time = 4)
    
        self.play(Create(cosAx),run_time=4)
        self.play(Write(costex),run_time=4)

        # sin cos waves as parametric curve
        sinwave = always_redraw(
            lambda: sinAx.plot_parametric_curve(lambda t: np.array([t*(1/DEGREES)/45,np.sin(t),0]),
                                                t_range=[0,theta.get_value()],color=GREEN)
        )
        coswave = always_redraw(
            lambda: cosAx.plot_parametric_curve(lambda t: np.array([t*(1/DEGREES)/45,np.cos(t),0]),
                                                t_range=[0,theta.get_value()],color=RED)
        )

        self.add(sinwave,coswave)
        
        self.play(theta.animate.set_value(360*DEGREES),run_time=7)
        self.play(theta.animate.set_value(180*DEGREES),run_time=4)
        self.wait(3)
        self.play(theta.animate.set_value(360*DEGREES),run_time=3)
        self.play(theta.animate.set_value(90*DEGREES),run_time=3)
        self.play(theta.animate.set_value(270*DEGREES),run_time=2)
        self.play(theta.animate.set_value(0),run_time=3)

class unitcircle0(Scene):
    def construct(self):
         
         

         A = Line(2*DOWN+4*LEFT,4*LEFT,color=RED)
         theta = ValueTracker(30*DEGREES)

         O = always_redraw(
             lambda: Line(2*DOWN+4*LEFT, 2*DOWN+4*LEFT+RIGHT*(A.get_length() * np.tan(theta.get_value())),color=RED)
         )

         H = always_redraw(
             lambda: Line(4*LEFT, 2*DOWN+4*LEFT+RIGHT*(A.get_length() * np.tan(theta.get_value())),color=RED)
         )

         cosT = always_redraw(
             lambda: MathTex(f"\cos({round(theta.get_value()*1/DEGREES)}) = \\frac{{O}}{{H}}").move_to(UP*3+LEFT*2)
         )

         sinT = always_redraw(
             lambda: MathTex(f"\sin({round(theta.get_value()*1/DEGREES)}) = \\frac{{A}}{{H}}").move_to(UP*3+RIGHT*2)
         )

         aT = MathTex("A").next_to(A,LEFT)
         oT = always_redraw(
             lambda: MathTex("O").next_to(O,DOWN)
         )
         hT = always_redraw(
             lambda: MathTex("H").move_to(H.get_center()+0.3*RIGHT+0.3*UP)
         )

         angleT = always_redraw(
             lambda: Tex(f"{round(theta.get_value()*1/DEGREES)}\\textdegree").scale(0.7).move_to(3.7*LEFT+0.5*DOWN)
         )

         rangle = RightAngle(A,O)

         self.play(Create(A),Create(O),Create(H),Create(rangle), run_time=2)
         self.play(Write(cosT),Write(sinT),Write(oT),Write(aT),Write(hT),Write(angleT),run_time=2)
         self.play(theta.animate.set_value(60*DEGREES),run_time=4)
         self.play(theta.animate.set_value(88*DEGREES),run_time=8)