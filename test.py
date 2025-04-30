from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random
import time

# Camera and player variables
camera_pos = [0, 0, 200]
camera_front = [0, 0, -1]
camera_up = [0, 1, 0]
camera_speed = 5
yaw = -90
pitch = 0
first_mouse = True
last_x, last_y = 400, 400

# Game state
player_lives = 5
score = 0
game_over = False
cheat_mode = False
cheat_vision = False

# Planets and enemies
planets = []
enemies = []
lasers = []
enemy_lasers = []

# Timing
last_time = time.time()
enemy_spawn_time = 3  # seconds
last_enemy_spawn = time.time()

fovY = 60  # Field of view
GRID_LENGTH = 600  # Length of grid lines

class Planet:
    def __init__(self, radius, distance, color, rotation_speed, orbit_speed, parent=None):
        self.radius = radius
        self.distance = distance
        self.color = color
        self.rotation = 0
        self.rotation_speed = rotation_speed
        self.orbit_angle = random.uniform(0, 360)
        self.orbit_speed = orbit_speed
        self.parent = parent
        self.children = []
        
    def update(self, delta_time):
        self.rotation += self.rotation_speed * delta_time
        self.orbit_angle += self.orbit_speed * delta_time
        
        for child in self.children:
            child.update(delta_time)
            
    def draw(self):
        glPushMatrix()
        
        if self.parent:
            # Orbit around parent
            glRotatef(self.parent.orbit_angle, 0, 0, 1)
            glTranslatef(self.distance, 0, 0)
        
        # Rotate around own axis
        glRotatef(self.rotation, 0, 1, 0)
        
        glColor3f(*self.color)
        gluSphere(gluNewQuadric(), self.radius, 32, 32)
        
        for child in self.children:
            child.draw()
            
        glPopMatrix()

class Enemy:
    def __init__(self):
        self.radius = 10
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(100, 300)
        self.x = distance * math.cos(angle)
        self.y = distance * math.sin(angle)
        self.z = random.uniform(-50, 50)
        self.speed = random.uniform(0.5, 2)
        self.color = (1, 0, 0)
        self.last_shot = time.time()
        self.shot_delay = random.uniform(1, 3)
        
    def update(self, delta_time):
        # Move towards player (simple AI)
        dx = -self.x * self.speed * delta_time
        dy = -self.y * self.speed * delta_time
        dz = (0 - self.z) * self.speed * delta_time
        
        self.x += dx
        self.y += dy
        self.z += dz
        
        # Shoot at player
        current_time = time.time()
        if current_time - self.last_shot > self.shot_delay:
            self.shoot()
            self.last_shot = current_time
            self.shot_delay = random.uniform(1, 3)
    
    def shoot(self):
        # Calculate direction to player
        dir_x = -self.x
        dir_y = -self.y
        dir_z = -self.z
        length = math.sqrt(dir_x**2 + dir_y**2 + dir_z**2)
        if length > 0:
            dir_x /= length
            dir_y /= length
            dir_z /= length
        
        enemy_lasers.append({
            'x': self.x,
            'y': self.y,
            'z': self.z,
            'dx': dir_x * 10,
            'dy': dir_y * 10,
            'dz': dir_z * 10,
            'color': (1, 0, 0)
        })

class Laser:
    def __init__(self, x, y, z, dx, dy, dz):
        self.x = x
        self.y = y
        self.z = z
        self.dx = dx
        self.dy = dy
        self.dz = dz
        self.speed = 15
        self.color = (0, 1, 1)
        
    def update(self, delta_time):
        self.x += self.dx * self.speed * delta_time
        self.y += self.dy * self.speed * delta_time
        self.z += self.dz * self.speed * delta_time
        
    def draw(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        glColor3f(*self.color)
        glutSolidSphere(2, 8, 8)
        glPopMatrix()

def init_planets():
    global planets
    
    # Sun (center of the solar system)
    sun = Planet(30, 0, (1, 1, 0), 0.5, 0)
    planets = [sun]
    
    # Planet 1
    planet1 = Planet(10, 80, (0, 0.5, 1), 1, 0.3, sun)
    sun.children.append(planet1)
    
    # Planet 2
    planet2 = Planet(15, 150, (0.8, 0.2, 0.2), 0.7, 0.2, sun)
    sun.children.append(planet2)
    
    # Planet 3
    planet3 = Planet(8, 200, (0.2, 0.8, 0.2), 1.2, 0.15, sun)
    sun.children.append(planet3)
    
    # Moon of planet 3
    moon = Planet(3, 30, (0.7, 0.7, 0.7), 1.5, 1, planet3)
    planet3.children.append(moon)

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

def keyboardListener(key, x, y):
    global camera_pos, camera_speed, cheat_mode, cheat_vision, player_lives, score, game_over
    
    if game_over and key == b'r':
        # Reset game
        player_lives = 5
        score = 0
        game_over = False
        enemies.clear()
        lasers.clear()
        enemy_lasers.clear()
        return
    
    # Movement controls (WASD)
    if key == b'w':
        camera_pos[0] += camera_front[0] * camera_speed
        camera_pos[1] += camera_front[1] * camera_speed
        camera_pos[2] += camera_front[2] * camera_speed
    if key == b's':
        camera_pos[0] -= camera_front[0] * camera_speed
        camera_pos[1] -= camera_front[1] * camera_speed
        camera_pos[2] -= camera_front[2] * camera_speed
    if key == b'a':
        # Strafe left
        right = [camera_front[1] * camera_up[2] - camera_front[2] * camera_up[1],
                 camera_front[2] * camera_up[0] - camera_front[0] * camera_up[2],
                 camera_front[0] * camera_up[1] - camera_front[1] * camera_up[0]]
        camera_pos[0] -= right[0] * camera_speed
        camera_pos[1] -= right[1] * camera_speed
        camera_pos[2] -= right[2] * camera_speed
    if key == b'd':
        # Strafe right
        right = [camera_front[1] * camera_up[2] - camera_front[2] * camera_up[1],
                 camera_front[2] * camera_up[0] - camera_front[0] * camera_up[2],
                 camera_front[0] * camera_up[1] - camera_front[1] * camera_up[0]]
        camera_pos[0] += right[0] * camera_speed
        camera_pos[1] += right[1] * camera_speed
        camera_pos[2] += right[2] * camera_speed
    
    # Cheat modes
    if key == b'c':
        cheat_mode = not cheat_mode
    if key == b'v':
        cheat_vision = not cheat_vision

def mouse_motion(x, y):
    global yaw, pitch, last_x, last_y, first_mouse, camera_front
    
    if first_mouse:
        last_x = x
        last_y = y
        first_mouse = False
    
    x_offset = x - last_x
    y_offset = last_y - y  # Reversed since y-coordinates range from bottom to top
    last_x = x
    last_y = y
    
    sensitivity = 0.1
    x_offset *= sensitivity
    y_offset *= sensitivity
    
    yaw += x_offset
    pitch += y_offset
    
    # Constrain pitch to avoid screen flip
    if pitch > 89:
        pitch = 89
    if pitch < -89:
        pitch = -89
    
    # Update camera front vector
    front = [
        math.cos(math.radians(yaw)) * math.cos(math.radians(pitch)),
        math.sin(math.radians(pitch)),
        math.sin(math.radians(yaw)) * math.cos(math.radians(pitch))
    ]
    length = math.sqrt(front[0]**2 + front[1]**2 + front[2]**2)
    camera_front = [front[0]/length, front[1]/length, front[2]/length]

def mouseListener(button, state, x, y):
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN and not game_over:
        # Fire laser
        lasers.append(Laser(
            camera_pos[0], camera_pos[1], camera_pos[2],
            camera_front[0], camera_front[1], camera_front[2]
        ))

def specialKeyListener(key, x, y):
    global camera_pos
    
    # Move camera up/down with arrow keys
    if key == GLUT_KEY_UP:
        camera_pos[1] += camera_speed
    if key == GLUT_KEY_DOWN:
        camera_pos[1] -= camera_speed

def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.25, 0.1, 1500)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    target = [camera_pos[0] + camera_front[0], 
              camera_pos[1] + camera_front[1], 
              camera_pos[2] + camera_front[2]]
    
    gluLookAt(camera_pos[0], camera_pos[1], camera_pos[2],  # Camera position
              target[0], target[1], target[2],  # Look-at target
              camera_up[0], camera_up[1], camera_up[2])  # Up vector

def idle():
    global last_time, last_enemy_spawn, player_lives, score, game_over
    
    current_time = time.time()
    delta_time = current_time - last_time
    last_time = current_time
    
    # Update planets
    for planet in planets:
        planet.update(delta_time)
    
    # Spawn enemies
    if current_time - last_enemy_spawn > enemy_spawn_time and len(enemies) < 10 and not game_over:
        enemies.append(Enemy())
        last_enemy_spawn = current_time
    
    # Update enemies
    for enemy in enemies[:]:
        enemy.update(delta_time)
        
        # Check if enemy is too close to player
        dist = math.sqrt((enemy.x - camera_pos[0])**2 + 
                         (enemy.y - camera_pos[1])**2 + 
                         (enemy.z - camera_pos[2])**2)
        if dist < 20 and not cheat_mode:  # Collision with player
            player_lives -= 1
            enemies.remove(enemy)
            if player_lives <= 0:
                game_over = True
    
    # Update lasers
    for laser in lasers[:]:
        laser.update(delta_time)
        
        # Check if laser is out of bounds
        if (abs(laser.x) > 500 or abs(laser.y) > 500 or abs(laser.z) > 500):
            lasers.remove(laser)
            continue
            
        # Check laser-enemy collisions
        for enemy in enemies[:]:
            dist = math.sqrt((laser.x - enemy.x)**2 + 
                             (laser.y - enemy.y)**2 + 
                             (laser.z - enemy.z)**2)
            if dist < enemy.radius + 2:  # Collision
                score += 1
                enemies.remove(enemy)
                if laser in lasers:
                    lasers.remove(laser)
                break
    
    # Update enemy lasers
    for laser in enemy_lasers[:]:
        laser['x'] += laser['dx']
        laser['y'] += laser['dy']
        laser['z'] += laser['dz']
        
        # Check if laser is out of bounds
        if (abs(laser['x']) > 500 or abs(laser['y']) > 500 or abs(laser['z']) > 500):
            enemy_lasers.remove(laser)
            continue
            
        # Check laser-player collision
        dist = math.sqrt((laser['x'] - camera_pos[0])**2 + 
                         (laser['y'] - camera_pos[1])**2 + 
                         (laser['z'] - camera_pos[2])**2)
        if dist < 10 and not cheat_mode:  # Collision with player
            player_lives -= 1
            enemy_lasers.remove(laser)
            if player_lives <= 0:
                game_over = True
    
    glutPostRedisplay()

def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)
    
    setupCamera()
    
    # Enable depth testing
    glEnable(GL_DEPTH_TEST)
    
    # Draw planets
    for planet in planets:
        planet.draw()
    
    # Draw enemies
    for enemy in enemies:
        glPushMatrix()
        glTranslatef(enemy.x, enemy.y, enemy.z)
        glColor3f(*enemy.color)
        glutSolidSphere(enemy.radius, 16, 16)
        glPopMatrix()
    
    # Draw lasers
    for laser in lasers:
        laser.draw()
    
    # Draw enemy lasers
    for laser in enemy_lasers:
        glPushMatrix()
        glTranslatef(laser['x'], laser['y'], laser['z'])
        glColor3f(*laser['color'])
        glutSolidSphere(2, 8, 8)
        glPopMatrix()
    
    # Draw HUD
    draw_text(10, 770, f"Lives: {player_lives} | Score: {score}")
    draw_text(10, 740, f"Position: {int(camera_pos[0])}, {int(camera_pos[1])}, {int(camera_pos[2])}")
    
    if cheat_mode:
        draw_text(10, 710, "CHEAT MODE ENABLED", GLUT_BITMAP_HELVETICA_12)
    if cheat_vision:
        draw_text(10, 690, "CHEAT VISION ENABLED", GLUT_BITMAP_HELVETICA_12)
    
    if game_over:
        draw_text(400, 400, "GAME OVER", GLUT_BITMAP_TIMES_ROMAN_24)
        draw_text(380, 370, "Press R to restart", GLUT_BITMAP_HELVETICA_18)
    
    glutSwapBuffers()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    wind = glutCreateWindow(b"3D Planet Shooter")
    
    init_planets()
    
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutMotionFunc(mouse_motion)
    glutPassiveMotionFunc(mouse_motion)
    glutIdleFunc(idle)
    
    glutMainLoop()

if __name__ == "__main__":
    main()