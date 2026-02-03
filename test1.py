from manim import *

class createCircle(Scene):
    def construct(self):
        circle = Circle()
        circle.set_fill(PINK, opacity=0.5)
        self.play(Create(circle))

class manimLogo(Scene):
    def construct(self):
        color1 = "#ece6e2"
        self.camera.background_color = color1

        square = Square(3,color=RED_C)
        logotxt = MathTex("\frac{dx}{dt}(e^{x^2} + \int_0^x17\sin{x} \ \dx)", fill_color=LOGO_BLACK).scale(7)

        groupofshapes = VGroup(square, logotxt)
        self.add(groupofshapes)