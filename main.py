from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math, random

# Camera-related variables
camera_pos = (0,500, 1000)
BOUND_RADIUS = 700

fovY = 60  # Field of view
GRID_LENGTH = 600  # Length of grid lines
rand_var = 423

class Planet():
    planets = []
    def __init__(self, radius, slices, stacks, color, pos, speed, radius_of_rotation, center_of_rotation):
        self.radius = radius
        self.slices = slices
        self.stacks = stacks
        self.color = color
        self.pos = pos
        self.speed = speed
        self.angle = 0
        self.center_of_rotation = center_of_rotation
        self.radius_of_rotation = radius_of_rotation
    def update_pos(self):
        #print(self.pos[0])
        self.angle += self.speed
        x = self.center_of_rotation[0] + math.cos(math.radians(self.angle)) * self.radius_of_rotation
        z = self.center_of_rotation[2] + (-math.sin(math.radians(self.angle))) * self.radius_of_rotation
        self.pos = (x, self.pos[1], z)
    @classmethod     
    def draw(self):
        for planet in Planet.planets:
            glPushMatrix()
            glColor3f(planet.color[0], planet.color[1], planet.color[2])
            glTranslatef(planet.pos[0], planet.pos[1], planet.pos[2]) 
            gluSphere(gluNewQuadric(), planet.radius, planet.slices, planet.stacks)
            #glutSolidSphere(self.radius, self.slices, self.stacks)
            glPopMatrix()    


class Player:
    def __init__(self, speed, pos):
        self.speed = speed
        self.pos = pos

    def update_pos(self):
        x, y, z = self.pos
        # WASD movement (XZ-plane)
        if key_states[b'w']:  # Forward
            z -= self.speed
            key_states[b'w'] = False
        if key_states[b's']:  # Backward
            z += self.speed
            key_states[b's'] = False
        if key_states[b'a']:  # Left
            x -= self.speed
            key_states[b'a'] = False
        if key_states[b'd']:  # Right
            x += self.speed
            key_states[b'd'] = False

        # Arrow keys (Y-axis)
        if key_states[GLUT_KEY_UP]:  # Up
            y += self.speed
            key_states[GLUT_KEY_UP] = False
        if key_states[GLUT_KEY_DOWN]:  # Down
            y -= self.speed
            key_states[GLUT_KEY_DOWN] = False
        

        dx, dy, dz = x, y, z
        distance = math.sqrt(dx*dx + dy*dy + dz*dz)

        if distance > BOUND_RADIUS:
            scale = BOUND_RADIUS / distance
            x *= scale
            y *= scale
            z *= scale
        self.pos = (x, y, z)    
        

#planet = Planet(40, 100, 100, (1.0, 0.0, 0.0), (200, 0, 0), 0.2, 500, (0, 0, 0))
#planet2 = Planet(80, 100, 100, (0.0, 1.0, 0.0), (planet.center_of_rotation[0], planet.center_of_rotation[1], planet.center_of_rotation[2]), 0, 0, (0, 0, 0))
#Planet.planets.append(planet)
#Planet.planets.append(planet2)


 #Massive central stars (stationary)
star1 = Planet(120, 100, 100, (0.9, 0.8, 0.1), (0, 0, 0), 0, 0, (0, 0, 0))
Planet.planets.append(star1)
star2 = Planet(80, 100, 100, (0.1, 0.8, 0.9), (800, 0, 0), 0, 0, (0, 0, 0))
Planet.planets.append(star2)
star3 = Planet(60, 100, 100, (0.9, 0.3, 0.5), (-600, 400, 0), 0, 0, (0, 0, 0))
Planet.planets.append(star3)

# Star1 planetary system
planet1 = Planet(40, 100, 100, (0.7, 0.2, 0.1), (300, 0, 0), 0.3, 300, star1.center_of_rotation)
Planet.planets.append(planet1)
planet2 = Planet(20, 100, 100, (0.3, 0.7, 0.2), (0, 400, 0), 0.25, 400, star1.center_of_rotation)
Planet.planets.append(planet2)
planet3 = Planet(30, 100, 100, (0.1, 0.3, 0.8), (-350, -350, 0), 0.35, 350, star1.center_of_rotation)
Planet.planets.append(planet3)
planet4 = Planet(15, 100, 100, (0.5, 0.5, 0.9), (0, -500, 0), 0.2, 500, star1.center_of_rotation)
Planet.planets.append(planet4)

# Star2 planetary system
planet5 = Planet(35, 100, 100, (0.2, 0.9, 0.7), (900, 200, 0), 0.4, 200, star2.center_of_rotation)
Planet.planets.append(planet5)
planet6 = Planet(25, 100, 100, (0.8, 0.1, 0.4), (700, -300, 0), 0.3, 300, star2.center_of_rotation)
Planet.planets.append(planet6)
planet7 = Planet(18, 100, 100, (0.4, 0.4, 0.4), (1100, 0, 0), 0.25, 100, star2.center_of_rotation)
Planet.planets.append(planet7)

# Star3 planetary system
planet8 = Planet(28, 100, 100, (0.6, 0.0, 0.6), (-550, 600, 0), 0.35, 200, star3.center_of_rotation)
Planet.planets.append(planet8)
planet9 = Planet(22, 100, 100, (0.0, 0.6, 0.6), (-700, 300, 0), 0.3, 300, star3.center_of_rotation)
Planet.planets.append(planet9)

# Moons around planets
# Planet1 moons
moon1 = Planet(8, 100, 100, (0.8, 0.8, 0.8), (340, 40, 0), 0.5, 40, planet1.center_of_rotation)
Planet.planets.append(moon1)
moon2 = Planet(6, 100, 100, (0.6, 0.6, 0.6), (260, -60, 0), 0.6, 60, planet1.center_of_rotation)
Planet.planets.append(moon2)

# Planet2 moons
moon3 = Planet(5, 100, 100, (0.7, 0.7, 0.5), (30, 430, 0), 0.7, 30, planet2.center_of_rotation)
Planet.planets.append(moon3)
moon4 = Planet(7, 100, 100, (0.5, 0.7, 0.7), (-30, 370, 0), 0.65, 30, planet2.center_of_rotation)
Planet.planets.append(moon4)

# Planet3 moons
moon5 = Planet(4, 100, 100, (0.9, 0.5, 0.5), (-380, -320, 0), 0.8, 30, planet3.center_of_rotation)
Planet.planets.append(moon5)
moon6 = Planet(5, 100, 100, (0.5, 0.9, 0.5), (-320, -380, 0), 0.75, 30, planet3.center_of_rotation)
Planet.planets.append(moon6)

# Planet5 moons
moon7 = Planet(6, 100, 100, (0.3, 0.3, 0.9), (930, 230, 0), 0.5, 30, planet5.center_of_rotation)
Planet.planets.append(moon7)
moon8 = Planet(4, 100, 100, (0.9, 0.3, 0.3), (870, 170, 0), 0.6, 30, planet5.center_of_rotation)
Planet.planets.append(moon8)

# Planet8 moons
moon9 = Planet(5, 100, 100, (0.8, 0.4, 0.8), (-570, 630, 0), 0.55, 20, planet8.center_of_rotation)
Planet.planets.append(moon9)
moon10 = Planet(3, 100, 100, (0.4, 0.8, 0.8), (-530, 570, 0), 0.65, 30, planet8.center_of_rotation)
Planet.planets.append(moon10)

# Additional planets in the system
# More planets around star1
for i in range(11, 30):
    angle = (i * 137.5) % 360  # Golden angle distribution
    dist = 550 + (i * 20)
    size = 10 + (i % 7)
    speed = 0.15 + (0.02 * (i % 5))
    color = (0.5 + 0.5*math.sin(i), 0.5 + 0.5*math.sin(i+2), 0.5 + 0.5*math.sin(i+4))
    pos = (dist * math.cos(math.radians(angle)), dist * math.sin(math.radians(angle)), 0)
    planet = Planet(size, 100, 100, color, pos, speed, dist, star1.center_of_rotation)
    Planet.planets.append(planet)

# More planets around star2
for i in range(31, 50):
    angle = (i * 137.5) % 360
    dist = 400 + (i * 15)
    size = 8 + (i % 6)
    speed = 0.2 + (0.03 * (i % 4))
    color = (0.3 + 0.7*math.sin(i*0.5), 0.3 + 0.7*math.sin(i*0.5+1), 0.3 + 0.7*math.sin(i*0.5+2))
    pos = (star2.center_of_rotation[0] + dist * math.cos(math.radians(angle)), 
           star2.center_of_rotation[1] + dist * math.sin(math.radians(angle)), 0)
    planet = Planet(size, 100, 100, color, pos, speed, dist, star2.center_of_rotation)
    Planet.planets.append(planet)

# More planets around star3
for i in range(51, 70):
    angle = (i * 137.5) % 360
    dist = 300 + (i * 10)
    size = 7 + (i % 5)
    speed = 0.25 + (0.04 * (i % 3))
    color = (0.2 + 0.8*math.cos(i*0.3), 0.2 + 0.8*math.cos(i*0.3+1), 0.2 + 0.8*math.cos(i*0.3+2))
    pos = (star3.center_of_rotation[0] + dist * math.cos(math.radians(angle)), 
           star3.center_of_rotation[1] + dist * math.sin(math.radians(angle)), 0)
    planet = Planet(size, 100, 100, color, pos, speed, dist, star3.center_of_rotation)
    Planet.planets.append(planet)

# Binary system between star1 and star2
binary_planet1 = Planet(25, 100, 100, (0.9, 0.6, 0.1), (400, 0, 0), 0.18, 400, (400, 0, 0))
Planet.planets.append(binary_planet1)
binary_planet2 = Planet(20, 100, 100, (0.1, 0.6, 0.9), (400, 100, 0), 0.22, 100, binary_planet1.center_of_rotation)
Planet.planets.append(binary_planet2)

# Rogue planets (moving through the system)
rogue1 = Planet(12, 100, 100, (0.4, 0.4, 0.4), (-1000, 300, 0), 0.1, 2000, (0, 0, 0))
Planet.planets.append(rogue1)
rogue2 = Planet(15, 100, 100, (0.5, 0.5, 0.5), (500, 800, 0), 0.08, 1500, (0, 0, 0))
Planet.planets.append(rogue2)

# Asteroid belts (many small objects)
for i in range(71, 100):
    angle = random.uniform(0, 360)
    dist = random.uniform(650, 750)
    size = random.uniform(2, 5)
    color = (random.uniform(0.3, 0.7), random.uniform(0.3, 0.7), random.uniform(0.3, 0.7))
    pos = (dist * math.cos(math.radians(angle)), dist * math.sin(math.radians(angle)), 0)
    speed = random.uniform(0.1, 0.2)
    planet = Planet(size, 50, 50, color, pos, speed, dist, star1.center_of_rotation)
    Planet.planets.append(planet)


# Massive central stars (stationary)
#star1 = Planet(120, 100, 100, (0.9, 0.8, 0.1), (0, 0, 0), 0, 0, (0, 0, 0))
#Planet.planets.append(star1)
#star2 = Planet(80, 100, 100, (0.1, 0.8, 0.9), (800, 0, 0), 0, 0, (0, 0, 0))
#Planet.planets.append(star2)
#star3 = Planet(60, 100, 100, (0.9, 0.3, 0.5), (-600, 400, 0), 0, 0, (0, 0, 0))
#Planet.planets.append(star3)
#
## Star1 planetary system
#planet1 = Planet(40, 100, 100, (0.7, 0.2, 0.1), (300, 0, 0), 0.75, 300, star1.center_of_rotation)
#Planet.planets.append(planet1)
#planet2 = Planet(20, 100, 100, (0.3, 0.7, 0.2), (0, 400, 0), 0.625, 400, star1.center_of_rotation)
#Planet.planets.append(planet2)
#planet3 = Planet(30, 100, 100, (0.1, 0.3, 0.8), (-350, -350, 0), 0.875, 350, star1.center_of_rotation)
#Planet.planets.append(planet3)
#planet4 = Planet(15, 100, 100, (0.5, 0.5, 0.9), (0, -500, 0), 0.5, 500, star1.center_of_rotation)
#Planet.planets.append(planet4)
#
## Star2 planetary system
#planet5 = Planet(35, 100, 100, (0.2, 0.9, 0.7), (900, 200, 0), 1.0, 200, star2.center_of_rotation)
#Planet.planets.append(planet5)
#planet6 = Planet(25, 100, 100, (0.8, 0.1, 0.4), (700, -300, 0), 0.75, 300, star2.center_of_rotation)
#Planet.planets.append(planet6)
#planet7 = Planet(18, 100, 100, (0.4, 0.4, 0.4), (1100, 0, 0), 0.625, 100, star2.center_of_rotation)
#Planet.planets.append(planet7)
#
## Star3 planetary system
#planet8 = Planet(28, 100, 100, (0.6, 0.0, 0.6), (-550, 600, 0), 0.875, 200, star3.center_of_rotation)
#Planet.planets.append(planet8)
#planet9 = Planet(22, 100, 100, (0.0, 0.6, 0.6), (-700, 300, 0), 0.75, 300, star3.center_of_rotation)
#Planet.planets.append(planet9)
#
## Moons around planets
#moon1 = Planet(8, 100, 100, (0.8, 0.8, 0.8), (340, 40, 0), 1.25, 40, planet1.center_of_rotation)
#Planet.planets.append(moon1)
#moon2 = Planet(6, 100, 100, (0.6, 0.6, 0.6), (260, -60, 0), 1.5, 60, planet1.center_of_rotation)
#Planet.planets.append(moon2)
#
#moon3 = Planet(5, 100, 100, (0.7, 0.7, 0.5), (30, 430, 0), 1.75, 30, planet2.center_of_rotation)
#Planet.planets.append(moon3)
#moon4 = Planet(7, 100, 100, (0.5, 0.7, 0.7), (-30, 370, 0), 1.625, 30, planet2.center_of_rotation)
#Planet.planets.append(moon4)
#
#moon5 = Planet(4, 100, 100, (0.9, 0.5, 0.5), (-380, -320, 0), 2.0, 30, planet3.center_of_rotation)
#Planet.planets.append(moon5)
#moon6 = Planet(5, 100, 100, (0.5, 0.9, 0.5), (-320, -380, 0), 1.875, 30, planet3.center_of_rotation)
#Planet.planets.append(moon6)
#
#moon7 = Planet(6, 100, 100, (0.3, 0.3, 0.9), (930, 230, 0), 1.25, 30, planet5.center_of_rotation)
#Planet.planets.append(moon7)
#moon8 = Planet(4, 100, 100, (0.9, 0.3, 0.3), (870, 170, 0), 1.5, 30, planet5.center_of_rotation)
#Planet.planets.append(moon8)
#
#moon9 = Planet(5, 100, 100, (0.8, 0.4, 0.8), (-570, 630, 0), 1.375, 20, planet8.center_of_rotation)
#Planet.planets.append(moon9)
#moon10 = Planet(3, 100, 100, (0.4, 0.8, 0.8), (-530, 570, 0), 1.625, 30, planet8.center_of_rotation)
#Planet.planets.append(moon10)
#
## Additional planets around star1
#for i in range(11, 30):
#    angle = (i * 137.5) % 360
#    dist = 550 + (i * 20)
#    size = 10 + (i % 7)
#    speed = 2.5 * (0.15 + (0.02 * (i % 5)))
#    color = (0.5 + 0.5*math.sin(i), 0.5 + 0.5*math.sin(i+2), 0.5 + 0.5*math.sin(i+4))
#    pos = (dist * math.cos(math.radians(angle)), dist * math.sin(math.radians(angle)), 0)
#    planet = Planet(size, 100, 100, color, pos, speed, dist, star1.center_of_rotation)
#    Planet.planets.append(planet)
#
## Additional planets around star2
#for i in range(31, 50):
#    angle = (i * 137.5) % 360
#    dist = 400 + (i * 15)
#    size = 8 + (i % 6)
#    speed = 2.5 * (0.2 + (0.03 * (i % 4)))
#    color = (0.3 + 0.7*math.sin(i*0.5), 0.3 + 0.7*math.sin(i*0.5+1), 0.3 + 0.7*math.sin(i*0.5+2))
#    pos = (star2.center_of_rotation[0] + dist * math.cos(math.radians(angle)), 
#           star2.center_of_rotation[1] + dist * math.sin(math.radians(angle)), 0)
#    planet = Planet(size, 100, 100, color, pos, speed, dist, star2.center_of_rotation)
#    Planet.planets.append(planet)
#
## Additional planets around star3
#for i in range(51, 70):
#    angle = (i * 137.5) % 360
#    dist = 300 + (i * 10)
#    size = 7 + (i % 5)
#    speed = 2.5 * (0.25 + (0.04 * (i % 3)))
#    color = (0.2 + 0.8*math.cos(i*0.3), 0.2 + 0.8*math.cos(i*0.3+1), 0.2 + 0.8*math.cos(i*0.3+2))
#    pos = (star3.center_of_rotation[0] + dist * math.cos(math.radians(angle)), 
#           star3.center_of_rotation[1] + dist * math.sin(math.radians(angle)), 0)
#    planet = Planet(size, 100, 100, color, pos, speed, dist, star3.center_of_rotation)
#    Planet.planets.append(planet)
#
## Binary system between star1 and star2
#binary_planet1 = Planet(25, 100, 100, (0.9, 0.6, 0.1), (400, 0, 0), 0.45, 400, (400, 0, 0))
#Planet.planets.append(binary_planet1)
#binary_planet2 = Planet(20, 100, 100, (0.1, 0.6, 0.9), (400, 100, 0), 0.55, 100, binary_planet1.center_of_rotation)
#Planet.planets.append(binary_planet2)
#
## Rogue planets
#rogue1 = Planet(12, 100, 100, (0.4, 0.4, 0.4), (-1000, 300, 0), 0.25, 2000, (0, 0, 0))
#Planet.planets.append(rogue1)
#rogue2 = Planet(15, 100, 100, (0.5, 0.5, 0.5), (500, 800, 0), 0.2, 1500, (0, 0, 0))
#Planet.planets.append(rogue2)
#
## Asteroid belt
#for i in range(71, 100):
#    angle = random.uniform(0, 360)
#    dist = random.uniform(650, 750)
#    size = random.uniform(2, 5)
#    color = (random.uniform(0.3, 0.7), random.uniform(0.3, 0.7), random.uniform(0.3, 0.7))
#    pos = (dist * math.cos(math.radians(angle)), dist * math.sin(math.radians(angle)), 0)
#    speed = 2.5 * random.uniform(0.1, 0.2)
#    planet = Planet(size, 50, 50, color, pos, speed, dist, star1.center_of_rotation)
#    Planet.planets.append(planet)





player = Player(20, (0, 0, 200))
key_states = {
    b'w': False, b'a': False, b's': False, b'd': False,
    GLUT_KEY_UP: False, GLUT_KEY_DOWN: False
}


player = Player(20, (0, 0, 200))

key_states = {
    b'w': False, b'a': False, b's': False, b'd': False,
    GLUT_KEY_UP: False, GLUT_KEY_DOWN: False
}


def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1,1,1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    
    # Set up an orthographic projection that matches window coordinates
    gluOrtho2D(0, 1000, 0, 800)  # left, right, bottom, top

    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Draw text at (x, y) in screen coordinates
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    
    # Restore original projection and modelview matrices
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def draw_shapes():
    Planet.draw() 

def keyboardListener(key, x, y):
    global key_states
    if key in [b'w', b'a', b's', b'd']:
        key_states[key] = True

def specialKeyListener(key, x, y):
    global key_states
    if key in [GLUT_KEY_UP, GLUT_KEY_DOWN]:
        key_states[key] = True  # Arrow key pressed


def mouseListener(button, state, x, y):
    """
    Handles mouse inputs for firing bullets (left click) and toggling camera mode (right click).
    """
        # # Left mouse button fires a bullet
        # if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:

        # # Right mouse button toggles camera tracking mode
        # if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:


def setupCamera():
    glMatrixMode(GL_PROJECTION)  
    glLoadIdentity()  
    width, height = glutGet(GLUT_WINDOW_WIDTH), glutGet(GLUT_WINDOW_HEIGHT)
    aspect_ratio = width / height
    gluPerspective(fovY, aspect_ratio, 0.1, 3000) 
    glMatrixMode(GL_MODELVIEW)  
    glLoadIdentity()  
    look_x = player.pos[0]
    look_z = player.pos[2] - 1  
    look_y = player.pos[1]     
    gluLookAt(player.pos[0], player.pos[1], player.pos[2],  
              look_x, look_y, look_z,  
              0, 1, 0)  

def idle():
    #planet.update_pos()
    for planet in Planet.planets:
        planet.update_pos()
    player.update_pos()
    glutPostRedisplay()


def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity() 
    width, height = glutGet(GLUT_WINDOW_WIDTH), glutGet(GLUT_WINDOW_HEIGHT)
    glViewport(0, 0, width, height) 


    setupCamera() 
    draw_text(10, 770, f"A Random Fixed Position Text")
    draw_text(10, 740, f"See how the position and variable change?: {rand_var}")

    draw_shapes()
    glutSwapBuffers()


def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH) 
    glutInitWindowSize(1920, 1080) 
    glutInitWindowPosition(0, 0)  
    wind = glutCreateWindow(b"3D OpenGL Intro")  

    glEnable(GL_DEPTH_TEST)

    glutDisplayFunc(showScreen)  
    glutKeyboardFunc(keyboardListener)  
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle) 

    glutMainLoop()  

if __name__ == "__main__":
    main()