from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math, random
import numpy as np

# Camera-related variables
BOUND_RADIUS = 700
fovY = 60  # Field of view
GRID_LENGTH = 600  # Length of grid lines
rand_var = 423

# Camera control variables
camera_yaw = -90  # Initial yaw to look along negative Z
camera_pitch = 0
mouse_sensitivity = 0.1
window_center_x, window_center_y = 0, 0

# Game state variables
score = 0
lives = 5
game_over = False
last_time = 0
bullet_cooldown = 0.2  
last_bullet_time = 0
spawn_interval = 5  
last_spawn_time = 0

menu_active = True
menu_option = 0  # 0: Start Game, 1: Settings, 2: Quit
settings_menu = False
difficulty = 1  # 1: Easy, 2: Medium, 3: Hard

class Planet:
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
        self.angle += self.speed
        x = self.center_of_rotation[0] + math.cos(math.radians(self.angle)) * self.radius_of_rotation
        z = self.center_of_rotation[2] + (-math.sin(math.radians(self.angle))) * self.radius_of_rotation
        self.pos = (x, self.pos[1], z)
        
    @classmethod     
    def draw(cls):
        for planet in cls.planets:
            glPushMatrix()
            glColor3f(*planet.color)
            glTranslatef(*planet.pos) 
            gluSphere(gluNewQuadric(), planet.radius, planet.slices, planet.stacks)
            glPopMatrix()

class Enemy:
    enemies = []
    def __init__(self, pos):
        self.pos = pos
        self.speed = 20
        self.fire_rate = 2  # seconds between shots
        self.last_shot_time = 0
        self.radius = 30

    def update(self, delta_time, player_pos):
        # Move towards player
        direction = np.array(player_pos) - np.array(self.pos)
        distance = np.linalg.norm(direction)
        if distance > 0:
            direction = direction / distance
            self.pos = tuple(np.array(self.pos) + direction * self.speed * delta_time)
        
        # Fire missiles
        current_time = glutGet(GLUT_ELAPSED_TIME) / 1000.0
        if current_time - self.last_shot_time >= self.fire_rate:
            self.last_shot_time = current_time
            Missile.missiles.append(Missile(self.pos))
    @classmethod
    def draw(cls):
        for enemy in Enemy.enemies:
            glPushMatrix()
            glTranslatef(*enemy.pos)
            glColor3f(1, 0, 0)
            glScalef(1.0, 0.3, 0.3)
            gluSphere(gluNewQuadric(), enemy.radius, 20, 20)
            glPopMatrix()

class Missile:
    missiles = []
    def __init__(self, start_pos):
        self.pos = start_pos
        self.speed = 50
        self.radius = 5
        self.outline_radius = 8  # Radius of the circular outline
        self.outline_thickness = 0.5  # Thickness of the outline ring

    def update(self, delta_time, target_pos):
        direction = np.array(target_pos) - np.array(self.pos)
        distance = np.linalg.norm(direction)
        if distance > 0:
            direction = direction / distance
            self.pos = tuple(np.array(self.pos) + direction * self.speed * delta_time)
            
    @classmethod
    def draw(cls):
        for missile in Missile.missiles:
            glPushMatrix()
            glTranslatef(*missile.pos)
            glColor3f(1, 1, 0) 
            gluSphere(gluNewQuadric(), missile.radius, 10, 10)
            glColor3f(1, 0, 0) 
            modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
            # Reset rotation components to make it face camera
            for i in range(3):
                for j in range(3):
                    if i == j:
                        modelview[i][j] = 1.0
                    else:
                        modelview[i][j] = 0.0
            
            glPushMatrix()
            glLoadMatrixd(modelview)
            quad = gluNewQuadric()
            gluDisk(quad, missile.outline_radius - missile.outline_thickness, 
                   missile.outline_radius, 32, 1)
            
            glPopMatrix()
            glPopMatrix()


class Bullet:
    bullets = []
    def __init__(self, start_pos, velocity):
        self.pos = start_pos
        self.velocity = velocity
        self.speed = 200
        self.radius = 1

    def update(self, delta_time):
        self.pos = tuple(np.array(self.pos) + np.array(self.velocity) * delta_time)
    @classmethod
    def draw(cls):
        for bullet in Bullet.bullets:
            glPushMatrix()
            glTranslatef(*bullet.pos)
            glColor3f(1, 1, 1)
            gluSphere(gluNewQuadric(), bullet.radius, 10, 10)
            glPopMatrix()
            

class Player:
    def __init__(self, speed, pos):
        self.speed = speed
        self.pos = pos
        self.front = (0, 0, -1)
        self.right = (1, 0, 0)
        self.up = (0, 1, 0)
        self.radius = 10
        # Gun barrel parameters
        self.barrel_length = 30
        self.barrel_radius = 1.5
        self.camera_offset = 2.0  

    def update_vectors(self):
        front_x = math.cos(math.radians(camera_yaw)) * math.cos(math.radians(camera_pitch))
        front_y = math.sin(math.radians(camera_pitch))
        front_z = math.sin(math.radians(camera_yaw)) * math.cos(math.radians(camera_pitch))
        self.front = (front_x, front_y, front_z)
        
        front = np.array(self.front)
        world_up = np.array([0, 1, 0])
        right = np.cross(front, world_up)
        right /= np.linalg.norm(right)
        up = np.cross(right, front)
        up /= np.linalg.norm(up)
        
        self.right = tuple(right)
        self.up = tuple(up)
    
    def update_pos(self):
        x, y, z = self.pos
        
        if key_states[b'w']:
            x += self.front[0] * self.speed
            y += self.front[1] * self.speed
            z += self.front[2] * self.speed
        if key_states[b's']:
            x -= self.front[0] * self.speed
            y -= self.front[1] * self.speed
            z -= self.front[2] * self.speed
        if key_states[b'a']:
            x -= self.right[0] * self.speed
            y -= self.right[1] * self.speed
            z -= self.right[2] * self.speed
        if key_states[b'd']:
            x += self.right[0] * self.speed
            y += self.right[1] * self.speed
            z += self.right[2] * self.speed

        if key_states[GLUT_KEY_UP]:
            y += self.speed
        if key_states[GLUT_KEY_DOWN]:
            y -= self.speed
        
        distance = math.sqrt(x*x + y*y + z*z)
        if distance > BOUND_RADIUS:
            scale = BOUND_RADIUS / distance
            x *= scale
            y *= scale
            z *= scale
            
        self.pos = (x, y, z)
    
    def draw(self):
        glPushMatrix()
        
        # Position the barrel slightly below the camera
        barrel_pos = (
            self.pos[0] - self.front[0] * 5 - self.up[0] * self.camera_offset,
            self.pos[1] - self.front[1] * 5 - self.up[1] * self.camera_offset,
            self.pos[2] - self.front[2] * 5 - self.up[2] * self.camera_offset
        )
        glTranslatef(*barrel_pos)
        
        # Align the barrel with the camera direction
        rot_angle = math.degrees(math.atan2(self.front[0], self.front[2]))
        glRotatef(rot_angle, 0, 1, 0)
        
        pitch_angle = math.degrees(math.asin(-self.front[1]))
        glRotatef(pitch_angle, 1, 0, 0)
        
        # Draw the main barrel
        glColor3f(0.3, 0.3, 0.3)  # Dark gray color
        quad = gluNewQuadric()
        gluCylinder(quad, self.barrel_radius, self.barrel_radius, self.barrel_length, 20, 5)
        
        # Draw the muzzle at the end of the barrel
        glTranslatef(0, 0, self.barrel_length)
        glColor3f(0.5, 0.5, 0.5)  # Lighter gray
        gluDisk(quad, 0, self.barrel_radius, 20, 1)
        
        # Draw a smaller inner barrel
        glColor3f(0.2, 0.2, 0.2)  # Very dark gray
        gluCylinder(quad, self.barrel_radius*0.6, self.barrel_radius*0.6, self.barrel_length*0.2, 20, 5)
        
        glPopMatrix()

# Initialize planets (existing code remains the same)
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



player = Player(20, (0, 0, 200))
key_states = {
    b'w': False, b'a': False, b's': False, b'd': False,
    GLUT_KEY_UP: False, GLUT_KEY_DOWN: False,
    b' ': False
}

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1,1,1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_shapes():
    Planet.draw()
    Enemy.draw()
    Missile.draw()
    Bullet.draw()
    player.draw()

def menuKeyboard(key, x, y):
    global menu_active, menu_option, settings_menu, difficulty, lives, spawn_interval
    
    if settings_menu:
        if key == b'\x1b':  # ESC to go back
            settings_menu = False
        elif key == b'1':
            difficulty = 1
            lives = 5
            spawn_interval = 5
        elif key == b'2':
            difficulty = 2
            lives = 3
            spawn_interval = 3
        elif key == b'3':
            difficulty = 3
            lives = 2
            spawn_interval = 2
    else:
        if key == b'\r' or key == b' ':  # Enter or Space to select
            if menu_option == 0:  # Start Game
                menu_active = False
                reset_game()
            elif menu_option == 1:  # Settings
                settings_menu = True
            elif menu_option == 2:  # Quit
                glutLeaveMainLoop()
        elif key == b'w' or key == GLUT_KEY_UP:
            menu_option = (menu_option - 1) % 3
        elif key == b's' or key == GLUT_KEY_DOWN:
            menu_option = (menu_option + 1) % 3
        elif key == b'\x1b':  # ESC to quit
            glutLeaveMainLoop()

# Add this function to reset the game state
def reset_game():
    global score, lives, game_over, Enemy, Missile, Bullet, player
    
    score = 0
    game_over = False
    Enemy.enemies = []
    Missile.missiles = []
    Bullet.bullets = []
    player.pos = (0, 0, 200)
    camera_yaw = -90
    camera_pitch = 0
    player.update_vectors()

def draw_menu():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    
    width, height = glutGet(GLUT_WINDOW_WIDTH), glutGet(GLUT_WINDOW_HEIGHT)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, width, 0, height)
    glMatrixMode(GL_MODELVIEW)
    
    # Draw title
    title = "SPACE SHOOTER"
    title_width = sum(glutBitmapWidth(GLUT_BITMAP_TIMES_ROMAN_24, ord(c)) for c in title)
    glColor3f(1, 1, 1)
    glRasterPos2f((width - title_width) / 2, height * 0.8)
    for c in title:
        glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(c))
    
    if settings_menu:
        # Draw settings menu
        options = [
            "DIFFICULTY SETTING",
            "1. Easy (5 lives, slow spawn)",
            "2. Medium (3 lives, normal spawn)",
            "3. Hard (2 lives, fast spawn)",
            "Current: " + ["Easy", "Medium", "Hard"][difficulty-1],
            "Press ESC to go back"
        ]
        
        for i, option in enumerate(options):
            option_width = sum(glutBitmapWidth(GLUT_BITMAP_HELVETICA_18, ord(c)) for c in option)
            glColor3f(1, 1, 1)
            if i == 0:  # Title
                glColor3f(0.8, 0.8, 1)
            glRasterPos2f((width - option_width) / 2, height * 0.6 - i * 30)
            for c in option:
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(c))
    else:
        # Draw main menu
        options = ["START GAME", "SETTINGS", "QUIT"]
        
        for i, option in enumerate(options):
            option_width = sum(glutBitmapWidth(GLUT_BITMAP_HELVETICA_18, ord(c)) for c in option)
            if i == menu_option:
                glColor3f(1, 1, 0)  # Highlight selected option
            else:
                glColor3f(1, 1, 1)
            glRasterPos2f((width - option_width) / 2, height * 0.6 - i * 30)
            for c in option:
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(c))
    
    # Draw controls info
    controls = [
        "CONTROLS:",
        "WASD - Move",
        "Arrow Keys - Move Up/Down",
        "Mouse - Look",
        "Space - Shoot"
    ]
    
    for i, control in enumerate(controls):
        glColor3f(0.7, 0.7, 0.7)
        glRasterPos2f(width * 0.1, height * 0.3 - i * 20)
        for c in control:
            glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(c))
    
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glutSwapBuffers()


def keyboardListener(key, x, y):
    global menu_active, game_over
    
    if menu_active or game_over:
        if key == b'\x1b' and game_over:  # ESC to return to menu from game over
            menu_active = True
            game_over = False
        menuKeyboard(key, x, y)
    else:
        if key in [b'w', b'a', b's', b'd', b' ']:
            key_states[key] = True
        elif key == b'\x1b':  # ESC to pause/menu
            menu_active = True

def keyboardUpListener(key, x, y):
    global key_states
    if key in [b'w', b'a', b's', b'd', b' ']:
        key_states[key] = False

def specialKeyListener(key, x, y):
    if menu_active or game_over:
        menuKeyboard(key, x, y)
    else:
        if key in [GLUT_KEY_UP, GLUT_KEY_DOWN]:
            key_states[key] = True


def specialKeyUpListener(key, x, y):
    global key_states
    if key in [GLUT_KEY_UP, GLUT_KEY_DOWN]:
        key_states[key] = False

def mouseMotion(x, y):
    global camera_yaw, camera_pitch, window_center_x, window_center_y
    
    x_offset = x - window_center_x
    y_offset = window_center_y - y
    
    x_offset *= mouse_sensitivity
    y_offset *= mouse_sensitivity
    
    camera_yaw += x_offset
    camera_pitch += y_offset
    
    if camera_pitch > 89: camera_pitch = 89
    if camera_pitch < -89: camera_pitch = -89
    
    player.update_vectors()
    glutWarpPointer(window_center_x, window_center_y)


def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    width, height = glutGet(GLUT_WINDOW_WIDTH), glutGet(GLUT_WINDOW_HEIGHT)
    gluPerspective(fovY, width/height, 0.1, 3000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    # Calculate camera position (slightly above the barrel)
    camera_pos = (
        player.pos[0] + player.up[0] * player.camera_offset,
        player.pos[1] + player.up[1] * player.camera_offset,
        player.pos[2] + player.up[2] * player.camera_offset
    )
    
    target_x = camera_pos[0] + player.front[0]
    target_y = camera_pos[1] + player.front[1]
    target_z = camera_pos[2] + player.front[2]
    
    gluLookAt(*camera_pos, target_x, target_y, target_z, *player.up)




def check_collisions():
    global lives, score, game_over
    
    # Check missile-player collisions
    for missile in Missile.missiles[:]:
        distance = np.linalg.norm(np.array(missile.pos) - np.array(player.pos))
        if distance < missile.radius + player.radius:
            lives -= 1
            Missile.missiles.remove(missile)
            if lives <= 0:
                game_over = True
    
    # Check bullet-enemy collisions
    for bullet in Bullet.bullets[:]:
        hit = False
        for enemy in Enemy.enemies[:]:
            distance = np.linalg.norm(np.array(bullet.pos) - np.array(enemy.pos))
            if distance < bullet.radius + enemy.radius:
                Enemy.enemies.remove(enemy)
                Bullet.bullets.remove(bullet)
                score += 10
                hit = True
                break
        if not hit:
            for missile in Missile.missiles[:]:
                distance = np.linalg.norm(np.array(bullet.pos) - np.array(missile.pos))
                if distance < bullet.radius + missile.radius:
                    Missile.missiles.remove(missile)
                    Bullet.bullets.remove(bullet)
                    hit = True
                    break
    
    # Remove out-of-bound objects
    max_dist = BOUND_RADIUS * 2
    for obj_list in [Enemy.enemies, Missile.missiles, Bullet.bullets]:
        for obj in obj_list[:]:
            if np.linalg.norm(np.array(obj.pos)) > max_dist:
                obj_list.remove(obj)

def idle():
    global last_time, last_spawn_time, last_bullet_time
    
    current_time = glutGet(GLUT_ELAPSED_TIME) / 1000.0
    delta_time = current_time - last_time
    last_time = current_time
    
    if game_over:
        return
    
    # Spawn enemies
    if current_time - last_spawn_time >= spawn_interval:
        theta = random.uniform(0, 2*math.pi)
        phi = math.acos(2*random.uniform(0,1) - 1)
        r = BOUND_RADIUS * random.uniform(0.5, 1.0)
        x = r * math.sin(phi) * math.cos(theta)
        y = r * math.sin(phi) * math.sin(theta)
        z = r * math.cos(phi)
        Enemy.enemies.append(Enemy((x,y,z)))
        last_spawn_time = current_time
    
    # Update game objects
    for planet in Planet.planets:
        planet.update_pos()
    player.update_pos()
    
    for enemy in Enemy.enemies:
        enemy.update(delta_time, player.pos)
    
    for missile in Missile.missiles:
        missile.update(delta_time, player.pos)
    
    for bullet in Bullet.bullets:
        bullet.update(delta_time)
    
    # Fire bullets
    if key_states[b' '] and (current_time - last_bullet_time) >= bullet_cooldown:
        velocity = np.array(player.front) * 200  # bullet speed
        Bullet.bullets.append(Bullet(player.pos, velocity))
        last_bullet_time = current_time
    
    check_collisions()
    glutPostRedisplay()

def showScreen():
    if menu_active:
        draw_menu()
    elif game_over:
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        width, height = glutGet(GLUT_WINDOW_WIDTH), glutGet(GLUT_WINDOW_HEIGHT)
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, width, 0, height)
        glMatrixMode(GL_MODELVIEW)
        
        # Draw game over text
        game_over_text = "GAME OVER"
        text_width = sum(glutBitmapWidth(GLUT_BITMAP_TIMES_ROMAN_24, ord(c)) for c in game_over_text)
        glColor3f(1, 0, 0)
        glRasterPos2f((width - text_width) / 2, height * 0.6)
        for c in game_over_text:
            glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(c))
        
        # Draw score
        score_text = f"Final Score: {score}"
        score_width = sum(glutBitmapWidth(GLUT_BITMAP_HELVETICA_18, ord(c)) for c in score_text)
        glColor3f(1, 1, 1)
        glRasterPos2f((width - score_width) / 2, height * 0.5)
        for c in score_text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(c))
        
        # Draw return to menu prompt
        menu_text = "Press ESC to return to menu"
        menu_width = sum(glutBitmapWidth(GLUT_BITMAP_9_BY_15, ord(c)) for c in menu_text)
        glColor3f(0.7, 0.7, 0.7)
        glRasterPos2f((width - menu_width) / 2, height * 0.4)
        for c in menu_text:
            glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(c))
        
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glutSwapBuffers()
    else:
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        setupCamera()
        draw_text(10, 770, f"Position: {player.pos[0]:.1f}, {player.pos[1]:.1f}, {player.pos[2]:.1f}")
        draw_text(10, 740, f"Yaw: {camera_yaw:.1f}, Pitch: {camera_pitch:.1f}")
        draw_text(10, 710, f"Lives: {lives} Score: {score}")
        draw_text(10, 680, f"Difficulty: {['Easy', 'Medium', 'Hard'][difficulty-1]}")
        
        draw_shapes()
        glutSwapBuffers()

def reshape(width, height):
    global window_center_x, window_center_y
    window_center_x = width // 2
    window_center_y = height // 2
    glutWarpPointer(window_center_x, window_center_y)

def main():
    global last_time, menu_active
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1920, 1080)
    glutCreateWindow(b"3D Space Shooter")
    
    glEnable(GL_DEPTH_TEST)
    glutSetCursor(GLUT_CURSOR_NONE)
    last_time = glutGet(GLUT_ELAPSED_TIME) / 1000.0
    
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutKeyboardUpFunc(keyboardUpListener)
    glutSpecialFunc(specialKeyListener)
    glutSpecialUpFunc(specialKeyUpListener)
    glutPassiveMotionFunc(mouseMotion)
    glutReshapeFunc(reshape)
    glutIdleFunc(idle)
    
    # Start with menu
    menu_active = True
    glutMainLoop()

if __name__ == "__main__":
    main()
