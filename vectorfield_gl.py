from manim import *
from manim.opengl import *
from manim.mobject import *
import numpy as np
#from jax import grad
from scipy.integrate import nquad

# in terminal (c:\)
# manim -qm -p --renderer=opengl vectorfield_gl.py VecField

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

# Newtonian gravitational vector field
def F_gravity(point, m1=2e6, m2=2e6):
    G = 6.674e-11
    num_co = m1 * m2 * G

    x = point[0]
    y = point[1]
    z = point[2]

    den_co = pow((x**2+y**2+z**2),1.5)
    
    if den_co == 0:
        return np.array([0.0,0.0,0.0])
    
    grav_co = num_co/den_co
    i = -grav_co * x
    j = -grav_co * y
    k = -grav_co * z

    return np.array([i,j,k])

def func(point,i_func=lambda x,y,z:x,j_func=lambda x,y,z:y, k_func=lambda x,y,z:z):
    i = i_func(point[0],point[1],point[2])
    j = j_func(point[0],point[1],point[2])
    k = k_func(point[0],point[1],point[2])

    return np.array([i,j,k])

def length(size):
    return size/20

def dot_p(point1, point2):
    return point1[0]*point2[0] + point1[1]*point2[1]

def div_f(func, point):
    return 1
    

class VecField(ThreeDScene):
    def construct(self):
        axes = ThreeDAxes(x_range=(-4,4,0.5),
                          y_range=(-4,4,0.5),
                          z_range=(-4,4,0.5),
                          x_length=8,
                          y_length=8,
                          z_length=8)

        self.axes = axes
        self.play(Create(axes))
        self.play(self.camera.animate.set_euler_angles(
            theta=-10*DEGREES, phi=50*DEGREES))
        
        #surface = lambda u, v: (u,v,u*np.sin(v) + v*np.sin(u))
        #self.create_surface(surface)
        radius = 1.0
        height = 2.0
        density_r = 10.0
        density_h = 4.0

        # create vector field
        i_func = lambda x,y,z: z * x - 3*y
        j_func = lambda x,y,z: y * z + 4*x
        k_func = lambda x,y,z: x

        def vector(point): return np.array([i_func(point[0],point[1],point[2]),
                                            j_func(point[0],point[1],point[2]),
                                            k_func(point[0],point[1],point[2])])

        self.create_vector_field(vector, 
                                 [-radius,radius,(2*radius)/density_r],
                                 [-radius,radius,(2*radius)/density_r],
                                 [0,height,height/density_h],[0,0,height/2],sf=1)
       
        '''
        # Calculate divergence (triple integral over volume)
        dfi_dx = grad(i_func,argnums=0)
        dfj_dy = grad(j_func,argnums=1)
        dfk_dz = grad(k_func,argnums=2)

        div = lambda r,theta,h: r * (dfi_dx(r*np.cos(theta), r*np.sin(theta),h) + \
                                dfj_dy(r*np.cos(theta), r*np.sin(theta),h) + \
                                dfk_dz(r*np.cos(theta), r*np.sin(theta),h))

        # bounds of integral
        r_bounds = [0,radius]
        t_bounds = [0,2*np.pi]
        h_bounds = [0,height]

        result,error = nquad(div, [r_bounds,t_bounds,h_bounds])
        print(result)
        '''
        result = 12.56637
        functext = MathTex(f"F(x,y,z) = (xz-3x)i + (yz+4y)j + (x)k").scale(0.55).to_edge(UL)
        divtext = MathTex(f"Net \ \ Flux = {result:.2f}").scale(0.55).to_edge(DR)
        cyltext = MathTex(f"Cylinder \ \ C: x^2 + y^2 = {radius}, 0 \leq z \leq {height}").scale(0.55).to_edge(UR)
        theoremtext = MathTex("Net \ \ outward \ \ flux: \int_0^h \int_0^{2 \pi} \int_0^r \\nabla \cdot \mathbf{F} \ \ rdrd\\theta dh").scale(0.55).to_edge(DL)
        
        self.add_fixed_in_frame_mobjects(functext, divtext,cyltext, theoremtext)

        # cylindrical surface
        cyl_surface = lambda u,v: (radius*np.cos(v), 1*np.sin(v), u)
        self.create_surface(cyl_surface,(0,2),(0,2*np.pi))
        # Linear number slider
        # slider = LinearNumberSlider()
        
        self.wait(10)
        # for interactivity
        #self.interactive_embed()

    def create_surface(self, para_func, u_r=(0,1), v_r=(0,1)):
        surface = OpenGLSurface( # create a parameterised surface
            para_func,
            u_range=u_r,
            v_range=v_r 
        )
        surface_mesh = OpenGLSurfaceMesh(surface)
        self.axes.add(surface_mesh)
        
    def create_vector_field(self, vec_func, x_r, y_r, z_r,field_centre=ORIGIN,sf=0.5):
        # Sample points over the incoming ranges
        x_vals = np.arange(*x_r)  # e.g. [-5, 5, 2]
        y_vals = np.arange(*y_r)
        z_vals = np.arange(*z_r)

        magnitudes = []

        for x in x_vals:
            for y in y_vals:
                for z in z_vals:
                    v = vec_func(np.array([x, y, z]))
                    magnitudes.append(np.linalg.norm(v))

        # dynamically determine color range
        vmin = min(magnitudes)
        vmax = max(magnitudes)

        # Avoid issues if they're equal (flat field)
        if vmin == vmax:
            vmin = 0

        field = ArrowVectorField(vec_func,min_color_scheme_value=vmin,
                                 max_color_scheme_value=vmax, length_func=length,
                                 x_range=x_r, y_range=y_r,z_range=z_r)
        
        field.scale(sf)
        field.move_to(field_centre)
        self.add(field)
        