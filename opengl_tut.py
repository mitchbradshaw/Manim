from manim import *
from manim.opengl import *

# in terminal (c:\)
# manim -qm -p --renderer=opengl opengl_tut.py GLIntro

# -p flag opens live render preview
#--write_to_movie passed to obtain a file

# preview window is pyglet window, suppports interaction

# Useful interactive methods
# Scene.on_mouse_motion
# Scene.on_mouse_scroll
# Scene.on_mouse_drag

# Useful Mobjects
# Scene.mouse_point
# Scene.mouse_drag_point

# Middle top of window is [0,4,0], regardless of camera

# Keyboard methods
# Scene.on_key_press
# Scene.on_key_release

class GLIntro(Scene):
    def construct(self):
        hellow = Tex("hello again dumbass")
        self.play(Write(hellow))

        self.play(self.camera.animate.set_euler_angles(
            theta=-10*DEGREES, phi=50*DEGREES))
        
        self.play(FadeOut(hellow ))

        surface = OpenGLSurface( # create a parameterised surface
            lambda u, v: (u,v,u*np.sin(v) + v*np.sin(u)),
            u_range=(-3,3),
            v_range=(-3,3) 
        )
        surface_mesh = OpenGLSurfaceMesh(surface)
        self.play(Create(surface_mesh))
        self.play(FadeTransform(surface_mesh, surface)) # fade between mesh object and surface object
        #self.wait()

        # messing with light source
        light = self.camera.light_source
        self.play(light.animate.shift([0,0,-20])) # move light source down
        self.play(light.animate.shift([0,0,10]))
        self.play(self.camera.animate.set_euler_angles(
            theta=10*DEGREES, phi=-50*DEGREES))
        
        # for interactivity
        self.interactive_embed()



# new interactive circle example
class interCircle(Scene):
    def construct(self):
        plane = NumberPlane()
        cursor_dot = Dot().move_to(3*RIGHT+2*UP)
        red_circle = Circle(
            radius=np.linalg.norm(cursor_dot.get_center()),
            color=RED
        )

        # np.linalg.norm -> length of a vector

        # to make the radius update, use updater function
        red_circle.add_updater(
            lambda mob: mob.become(
                Circle(
                    radius=np.linalg.norm(cursor_dot.get_center()),
                    color=RED
                )
            )
        )

        self.play(Create(plane), Create(red_circle), FadeIn(cursor_dot))
        # create attribute to self -> cursor dot object
        self.cursor_dot = cursor_dot
        self.interactive_embed()

    def on_key_press(self, symbol, modifiers):
        from pyglet.window import key as pyglet_key
        if symbol == pyglet_key.G:
            self.play(
                self.cursor_dot.animate.move_to(self.mouse_point.get_center())
            )

        super().on_key_press(symbol, modifiers)


def n_derivative(f, x, dx):
    return (f(x+dx) - f(x)) / (dx)


# iteration for finding roots of a function
class iterationExample(Scene):
    def construct(self):
        self.axes = Axes()
        self.f = lambda x: (x+5.7)*(x+4) * (x-3) * x * (x+3.5) * (x-4.6) / 400
        curve = self.axes.plot(self.f, color=BLUE)
        self.cursor_dot = Dot(color=RED)
        self.play(Create(self.axes), Create(curve), FadeIn(self.cursor_dot))
        functex = MathTex("f(x) = \\frac{x^6}{400} + \\frac{7x^5}{500} \
                          - \\frac{2977x^4}{40000} - \\frac{8467x^3}{20000} \
                          + \\frac{17667x^2}{40000} + \\frac{27531x}{10000}").scale(0.6).move_to(3.6*UP)
        self.add(functex)
        instruction_P = Text("Click 'P' to move dot").scale(0.2).to_edge(DR)
        instruction_I = Text("Click 'I' to calculate x-intercept of tangent").scale(0.2).to_edge(DL)
        self.add(instruction_I)
        self.add(instruction_P)

        self.label = MathTex("x = ")
        self.number = DecimalNumber(self.cursor_dot.get_x(), num_decimal_places=2)
        self.group = VGroup(self.label, self.number).arrange(RIGHT).next_to(self.cursor_dot, UP)
        self.add(self.group)
        self.wait(10)
        #self.interactive_embed()

    def on_key_press(self, symbol, modifiers):
        from pyglet.window import key as pyglet_key
        # for derivative calcs
        from scipy.differentiate import derivative
        if symbol == pyglet_key.P:
            x, y = self.axes.point_to_coords(self.mouse_point.get_center())
            self.play(
                # coordinates to point c2p
                self.cursor_dot.animate.move_to(self.axes.c2p(x, self.f(x)))
            )
           


        if symbol == pyglet_key.I:
            x , y = self.axes.point_to_coords(self.cursor_dot.get_center())
            # iteration algorithm
            fdot = n_derivative(self.f,x,0.01)
            x_new = x - self.f(x) / fdot
            curve_point = self.cursor_dot.get_center()
            axes_point = self.axes.c2p(x_new, 0)
            tangent = Line (
                curve_point  + (curve_point - axes_point)*0.25, # LEFT
                axes_point + (axes_point - curve_point)*0.25, # RIGHT
                color = GREEN,
                stroke_width = 2,
                stroke_type="--"
            )
            self.play(Create(tangent))
            self.play(self.cursor_dot.animate.move_to(axes_point))
            self.play(
                self.cursor_dot.animate.move_to(self.axes.c2p(x_new, self.f(x_new))),
                FadeOut(tangent)
                )

        self.remove(self.group)   
        self.number = DecimalNumber(self.cursor_dot.get_x(), num_decimal_places=2)
        self.group = VGroup(self.label, self.number).arrange(RIGHT).next_to(self.cursor_dot, UP)
        self.add(self.group)
        super().on_key_press(symbol, modifiers)