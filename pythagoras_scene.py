from manim import *
import numpy as np
from scipy.integrate import odeint
from scipy.integrate import solve_ivp

config.background_color = BLACK

class PythagScene1(Scene):
    def construct(self):
        # create initial triangle and right angle
        A = ORIGIN + 1.5*LEFT + 3*DOWN
        B = A + RIGHT * 3
        C = A + UP * 4

        tricolor = GREEN
        
        h_len = ValueTracker(3)
        v_len = ValueTracker(4)

        def get_B():
            return A + RIGHT*h_len.get_value()
        
        def get_C():
            return A + UP*v_len.get_value()

        horiz = always_redraw(lambda: Line(A,get_B(),color=tricolor))
        vert = always_redraw(lambda: Line(A,get_C(),color=tricolor))
        hyp = always_redraw(lambda:Line(get_B(), get_C(),color=tricolor))

        rightangle = always_redraw(lambda: RightAngle(
            Line(A, get_B()), Line(A, get_C()), length=0.5, color=RED
        ))

        triangle = VGroup(horiz, vert, hyp, rightangle)
        
        self.wait(10)
        self.play(Write(triangle), run_time=16)

        # highlight hypotenuse
        self.play(hyp.animate.set_color(YELLOW), run_time=3)
        self.wait(1)
        
        # animate movement of horizontal side
        self.play(h_len.animate.set_value(6), run_time=1.5)
        self.play(h_len.animate.set_value(1), run_time=1.5)
        self.play(h_len.animate.set_value(3), run_time=0.5)

        # animate movement of vertical side
        self.play(v_len.animate.set_value(6), run_time=1.5)
        self.play(v_len.animate.set_value(2), run_time=1.5)
        self.play(v_len.animate.set_value(4), run_time=1)

        # animate movement of both sides
        self.play(h_len.animate.set_value(6), v_len.animate.set_value(6), run_time=2)
        self.play(h_len.animate.set_value(2), run_time=2)
        self.play(v_len.animate.set_value(1), run_time=2)
        self.play(v_len.animate.set_value(4), h_len.animate.set_value(3), run_time=1)
        self.wait(3)
        self.remove(triangle)

class PythagScene2(Scene):
    def construct(self):
        # create initial triangle and right angle
        A = ORIGIN + 0.75*LEFT + 1*DOWN
        B = A + RIGHT * 1.5
        C = A + UP * 2
        tricolor = GREEN
        triangle = Polygon(A,B,C,color=tricolor)
        rightangle = RightAngle(Line(A,B), Line(A,C), length=0.3, color=RED)
        
        triruntime = 0.2
        squareruntime = 0.2

        self.play(Write(triangle), Write(rightangle), run_time=7)
        self.wait(4)
        # Create squares
        horizsquare = Square(1.5).move_to(DOWN*1.75)
        self.play(Create(horizsquare), run_time=4)
        vertsquare = Square(2).move_to(LEFT*1.75)
        self.play(Create(vertsquare), run_time=4)

        # Draw c^2 square
        cSquare = Square(2.5).move_to(1*RIGHT + 0.75*UP).rotate(-53.13*DEGREES)
        self.play(Create(cSquare),run_time=4)

        # Break into little squares
        lilsquarecol = BLUE
        hsquares = VGroup()
        for i in range(3):
            for j in range(3):
                x = 0.5*LEFT + i*0.5*RIGHT
                y = 1.25*DOWN + j*0.5*DOWN
                sq = Square(0.5).move_to(x+y)
                sq.set_stroke(lilsquarecol)
                sq.set_fill(YELLOW)
                hsquares.add(sq)

        vsquares = VGroup()
        for i in range(4):
            for j in range(4):
                x = 2.5*LEFT + i*0.5*RIGHT
                y = 0.75*UP + j*0.5*DOWN
                sq = Square(0.5).move_to(x+y)
                sq.set_stroke(lilsquarecol)
                sq.set_fill(YELLOW)
                vsquares.add(sq)

        self.play(LaggedStartMap(FadeIn, hsquares, lag_ratio=0.1))
        self.play(LaggedStartMap(FadeIn, vsquares, lag_ratio=0.1))

        # Animate the little squares moving to c^2
        
        # move hsquares to csquares
        # create an array of target squares and an array of animations
        cSquares = VGroup()
        for i in range(5):
            for j in range(5):
                x = i * RIGHT * 0.5
                y = 1.75 * UP + j * 0.5*DOWN
                sq = Square(0.5).move_to(x+y)
                sq.set_stroke(lilsquarecol)
                cSquares.add(sq)
     
        cSquares.rotate(-53.13*DEGREES)
        animations = []
        
        for i, sq in enumerate(hsquares):
            target = cSquares[i].get_center()
            animations.append(sq.animate.move_to(target).rotate(-53.13*DEGREES))
        for i, sq in enumerate(vsquares):
            target = cSquares[i+len(hsquares)].get_center()
            animations.append(sq.animate.move_to(target).rotate(-53.13*DEGREES))

        
        self.play(*animations, run_time=3)
        self.wait(5)
        self.remove(*hsquares,*vsquares,triangle,rightangle,horizsquare,vertsquare,cSquare,*cSquares)
        self.wait(2)

class PythagScene3(Scene):
    def construct(self):
        # create initial triangle and right angle
        A = ORIGIN + 0.75*LEFT + 1*DOWN
        B = A + RIGHT * 1.5
        C = A + UP * 2
        tricolor = GREEN
        triangle = Polygon(A,B,C,color=tricolor)
        rightangle = RightAngle(Line(A,B), Line(A,C), length=0.3, color=RED)
        
        triruntime = 0.2
        squareruntime = 0.2
        textruntime = 0.2

        self.play(Write(triangle), Write(rightangle), run_time=5)
        atext = MathTex("a").move_to(DOWN*1.3)
        btext = MathTex("b").move_to(1.05*LEFT)
        ctext = MathTex("c").move_to(0.3*RIGHT+0.2*UP)
        
        aLine = NumberLine(x_range=[0,1],length=1.5).move_to(DOWN*1.1)
        bLine = NumberLine(x_range=[0,1],length=2).move_to(0.85*LEFT).rotate(90*DEGREES)
        cLine = NumberLine(x_range=[0,1],length=2.5).move_to(0.1*RIGHT+0.1*UP).rotate(-53.13*DEGREES)

        self.play(Create(aLine),Write(atext),run_time=2)
        self.play(Create(bLine),Write(btext),run_time=2)
        self.play(Create(cLine),Write(ctext),run_time=2)
        self.wait(1)
        self.remove(aLine,bLine,cLine)
        self.wait(1)        # Create squares
        horizsquare = Square(1.5).move_to(DOWN*1.75)
        vertsquare = Square(2).move_to(LEFT*1.75)
        # Draw c^2 square
        cSquare = Square(2.5).move_to(1*RIGHT + 0.75*UP).rotate(-53.13*DEGREES)
        self.play(Create(cSquare),Create(vertsquare),Create(horizsquare),run_time=2)


        self.remove(triangle,atext,btext,ctext,rightangle)
        self.play(horizsquare.animate.move_to(4.5*LEFT),
                  vertsquare.animate.move_to(1*LEFT),
                  cSquare.animate.move_to(RIGHT*4.5).rotate(53.13*DEGREES),run_time=3)

        # Break into little squares
        lilsquarecol = BLUE
        hsquares = VGroup()
        for i in range(3):
            for j in range(3):
                x = 5*LEFT + i*0.5*RIGHT
                y = 0.5*UP + j*0.5*DOWN
                sq = Square(0.5).move_to(x+y)
                sq.set_stroke(lilsquarecol)
                sq.set_fill(YELLOW)
                hsquares.add(sq)

        vsquares = VGroup()
        for i in range(4):
            for j in range(4):
                x = 1.75*LEFT + i*0.5*RIGHT
                y = 0.75*UP + j*0.5*DOWN
                sq = Square(0.5).move_to(x+y)
                sq.set_stroke(lilsquarecol)
                sq.set_fill(YELLOW)
                vsquares.add(sq)

        asText = MathTex("a^2").move_to(LEFT*4.5 + DOWN*2)
        bsText = MathTex("b^2").move_to(LEFT*1 + DOWN*2)
        csText = MathTex("c^2").move_to(RIGHT*4.5+DOWN*2)
        self.play(LaggedStartMap(FadeIn, hsquares, lag_ratio=0.1),Write(asText),run_time=1.5)
        self.play(LaggedStartMap(FadeIn, vsquares, lag_ratio=0.1),Write(bsText),run_time=1.5)

        self.play(Write(csText),run_time=1.5)

        # Animate the little squares moving to c^2
        # move hsquares to csquares
        # create an array of target squares and an array of animations
        cSquares = VGroup()
        for i in range(5):
            for j in range(5):
                x = 3.5*RIGHT + i * RIGHT * 0.5
                y = 1 * UP + j * 0.5*DOWN
                sq = Square(0.5).move_to(x+y)
                sq.set_stroke(lilsquarecol)
                cSquares.add(sq)
     
        animations = []
        
        for i, sq in enumerate(hsquares):
            target = cSquares[i].get_center()
            animations.append(sq.animate.move_to(target))
        for i, sq in enumerate(vsquares):
            target = cSquares[i+len(hsquares)].get_center()
            animations.append(sq.animate.move_to(target))
        
        pText = MathTex("+").move_to(LEFT*2.88)
        eText = MathTex("=").move_to(RIGHT*1.62)

        self.play(*animations, Write(pText), Write(eText), run_time=10)

        self.wait(2)
        self.remove(horizsquare, vertsquare, cSquare, *hsquares,*vsquares,*cSquares)
        self.play(asText.animate.move_to(2*LEFT).scale(1.5),
                  pText.animate.move_to(1*LEFT).scale(1.5),
                  bsText.animate.move_to(ORIGIN).scale(1.5),
                  eText.animate.move_to(1*RIGHT).scale(1.5),
                  csText.animate.move_to(2*RIGHT).scale(1.5),run_time=5)