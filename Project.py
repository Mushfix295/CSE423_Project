from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random
import time


# --- Global Game State Variables ---
# Player Car
player_car_pos = [0, -200, 10]
player_car_angle = 90
player_car_speed = 3.5
player_car_strafing_speed = 1.2
player_car_turn_speed = 2.5
stars_for_menu = []
NUM_MENU_STARS = 200

# Opponent Cars
opponent_cars = []
NUM_OPPONENT_CARS = 4
OPPONENT_DESPAWN_DISTANCE = 6000
OPPONENT_SPAWN_AHEAD_DISTANCE = 4000


# Camera and View Variables
camera_distance_from_player = 200
camera_rotation_angle = -90
camera_vertical_angle = 35
is_first_person = False

fovY = 85

# Window dimensions for text rendering
window_width = 1000
window_height = 780

# Game variables
cars_passed = 0
game_time = 0
start_time = 0
player_rank = 1
distance_traveled = 0.0
previous_player_y = -200.0

# --- Finish Line Variables ---
FINISH_LINE_DISTANCE = 15000
finished_cars = []
player_finished = False
show_finish_popup = False
player_finish_position = 0

# Environment elements
fixed_trees = []
NUM_FIXED_TREES = 20
TREE_SCROLL_DISTANCE = 4000
TREE_DISPLAY_RANGE = 2000
ROAD_HALF_WIDTH = 240 / 2
TREE_MIN_X = ROAD_HALF_WIDTH + 50
TREE_MAX_X = ROAD_HALF_WIDTH + 200
MOUNTAIN_MIN_X = TREE_MAX_X + 100
MOUNTAIN_MAX_X = MOUNTAIN_MIN_X + 200


# Mountain variables
mountains = []
NUM_MOUNTAINS = 40
MOUNTAIN_SCROLL_DISTANCE = 5000
MOUNTAIN_DISPLAY_RANGE = 3000


# Road dimensions
ROAD_WIDTH = 240
ROAD_LINE_WIDTH = 5
ROAD_SEGMENT_LENGTH = 200
DASH_LENGTH = 120
LANE_MARKER_OFFSET = ROAD_WIDTH / 7
ROAD_CURVE_AMPLITUDE = 80
ROAD_CURVE_FREQUENCY = 1000.0

# Key states dictionary to handle multiple key presses
key_states = {}

# --- Collision Variables ---
CAR_COLLISION_RADIUS = 10
is_crashed = False
crash_timer = 0
CRASH_DURATION = 1.5 # seconds
sparks = []

# --- Nitro Variables ---
nitro_amount = 0
MAX_NITRO_AMOUNT = 100
NITRO_PICKUP_AMOUNT = 30
nitro_pickups = []
NITRO_RADIUS = 8
MAX_NITRO_PICKUPS_ON_SCREEN = 3
NITRO_SPAWN_AHEAD_DISTANCE = 3000
global_rotation_angle = 0 # For animating pickups

is_boosting = False
boost_level = 0
current_boost_speed_multiplier = 1.0
boost_timer = 0

# Boost durations
BOOST_DURATION_SINGLE_TAP = 3.0
BOOST_DURATION_DOUBLE_TAP = 4.0

# Nitro consumption
NITRO_CONSUMPTION_SINGLE_TAP = 18
NITRO_CONSUMPTION_DOUBLE_TAP = 35

# Double tap detection
last_space_press_time = 0
DOUBLE_TAP_THRESHOLD = 0.3

# --- Game State and Countdown ---
game_state = "MENU" # "MENU", "RACING", "FINISHED", "COUNTDOWN", "CRASHED_CHOICE", "TIMED_CHOICE"
countdown_start_time = 0
countdown_text = "3"
menu_options = ["Start Race", "Weather: Summer", "Mode: Competitive", "Exit"]
menu_selection = 0
weather_options = ["Summer", "Winter", "Monsoon"]
weather_selection = 0
mode_options = ["Competitive", "Free Mode", "Timed"]
mode_selection = 0
player_coins = 0
timed_mode_seconds = 60
is_day = True # REMOVED: Automatic day/night cycle timer


# --- Reborn and Time Extend Feature ---
choice_timer_start = 0
CHOICE_DURATION = 5.0
REBORN_COST = 30
TIME_EXTEND_COST = 20
TIME_EXTEND_AMOUNT = 15


# --- Invincibility after respawn ---
is_invincible = False
invincibility_timer = 0.0
INVINCIBILITY_DURATION = 1.5 # seconds

# --- Weather Particles ---
weather_particles = []
NUM_WEATHER_PARTICLES = 300


def draw_stars_for_menu():
    """Draws small, white dots for the starry night effect."""
    glPointSize(1.5)
    glColor3f(1.0, 1.0, 1.0)
    glBegin(GL_POINTS)
    for star in stars_for_menu:
        glVertex2f(star[0], star[1])
    glEnd()
    glPointSize(1.0)


# --- Utility Functions ---
def get_stroke_text_width(text):
    """Calculates the width of a string rendered with stroke font."""
    width = 0
    for ch in text:
        width += glutStrokeWidth(GLUT_STROKE_ROMAN, ord(ch))
    return width


def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18, color=(1,1,1)):
    """Draws 2D text on the screen at specified window coordinates."""
    glColor3f(*color)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, window_width, 0, window_height)


    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()


    # For large countdown text
    if font == "large":
        glLineWidth(5)
        glPushMatrix()
        glTranslatef(x, y, 0)
        glScalef(0.8, 0.8, 0.8)
        for ch in text:
            glutStrokeCharacter(GLUT_STROKE_ROMAN, ord(ch))
        glPopMatrix()
        glLineWidth(1)
    else:
        glRasterPos2f(x, y)
        for ch in text:
            glutBitmapCharacter(font, ord(ch))


    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def draw_colored_quad(v1, v2, v3, v4, color):
    """Draws a quad with a single color."""
    glColor3f(*color)
    glVertex3f(*v1)
    glVertex3f(*v2)
    glVertex3f(*v3)
    glVertex3f(*v4)


# --- Drawing Functions for Game Elements ---
def draw_pixel_car_model(main_color=(0.0, 0.0, 1.0), stripe_color=(1,0,0), accent_color=(1,1,1)):
    """
    Draws a simple car model.
    This function draws the car relative to its local origin (0,0,0).
    """
    car_width = 15
    car_length = 20
    car_height = 10


    # Main Body - rotated 90 degrees clockwise so front faces positive X-axis
    glPushMatrix()
    glColor3f(*main_color)
    glTranslatef(0, 0, car_height / 2 + 8)
    glRotatef(90, 0, 0, 1)  # Rotate 90 degrees clockwise around Z-axis
    glScalef(car_length, car_width, car_height)  # Swap width and length to match rotation
    glutSolidCube(1)
    glPopMatrix()


    # Wheels
    wheel_radius = 4
    wheel_width = 4
    wheel_z = 5


    quadric = gluNewQuadric()
    glColor3f(0.1, 0.1, 0.1)
    # Front Left Wheel (now becomes Front wheel on negative Y side due to rotation)
    glPushMatrix()
    glTranslatef(-car_length/2 + wheel_radius, -car_width/2 - wheel_width/2, wheel_z-3)
    glRotatef(90, 0, 1, 0)
    gluCylinder(quadric, wheel_radius, wheel_radius, wheel_width, 8, 4)
    gluDisk(quadric, 0, wheel_radius, 8, 1)
    glTranslatef(0,0,wheel_width)
    gluDisk(quadric, 0, wheel_radius, 8, 1)
    glPopMatrix()


    # Front Right Wheel (now becomes Front wheel on positive Y side due to rotation)
    glPushMatrix()
    glTranslatef(-car_length/2 + wheel_radius, car_width/2 + wheel_width/2, wheel_z)
    glRotatef(-90, 0, 1, 0)
    gluCylinder(quadric, wheel_radius, wheel_radius, wheel_width, 8, 4)
    gluDisk(quadric, 0, wheel_radius, 8, 1)
    glTranslatef(0,0,wheel_width)
    gluDisk(quadric, 0, wheel_radius, 8, 1)
    glPopMatrix()


    # Rear Left Wheel
    glPushMatrix()
    glTranslatef(car_length/2 - wheel_radius, -car_width/2 - wheel_width/2, wheel_z-3)
    glRotatef(90, 0, 1, 0)
    gluCylinder(quadric, wheel_radius, wheel_radius, wheel_width, 8, 4)
    gluDisk(quadric, 0, wheel_radius, 8, 1)
    glTranslatef(0,0,wheel_width)
    gluDisk(quadric, 0, wheel_radius, 8, 1)
    glPopMatrix()


    # Rear Right Wheel
    glPushMatrix()
    glTranslatef(car_length/2 - wheel_radius, car_width/2 + wheel_width/2, wheel_z)
    glRotatef(-90, 0, 1, 0)
    gluCylinder(quadric, wheel_radius, wheel_radius, wheel_width, 8, 4)
    gluDisk(quadric, 0, wheel_radius, 8, 1)
    glTranslatef(0,0,wheel_width)
    gluDisk(quadric, 0, wheel_radius, 8, 1)
    glPopMatrix()


    gluDeleteQuadric(quadric)


    # MODIFIED: Headlights are now positioned slightly in front of the car
    if not is_day:
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        glColor4f(1.0, 1.0, 0.8, 0.2)
        glBegin(GL_TRIANGLES)


        # Headlight origin points - front is now positive X-axis
        headlight_x_pos = car_length / 2 + 1
        left_light_origin = [headlight_x_pos, -car_width/4, car_height/2 + 5]
        right_light_origin = [headlight_x_pos, car_width/4, car_height/2 + 5]


        # Cone end points - pointing forward (along positive X-axis)
        light_end_x = car_length/2 + 80
        
        # MODIFIED: Make the headlight cones wider and rotate their angle
        cone_width = 15
        cone_height = 20
        angle_spread = 15  # Degrees to spread the lights outward


        # Calculate rotated end points for left headlight
        left_angle = math.radians(angle_spread)
        left_outer_x = light_end_x
        left_outer_y = -car_width/4 - cone_width * math.cos(left_angle)
        left_outer_z = cone_height * math.sin(left_angle)
        
        left_inner_x = light_end_x
        left_inner_y = -car_width/4 + cone_width * math.cos(left_angle)
        left_inner_z = cone_height * math.sin(left_angle)


        # Calculate rotated end points for right headlight
        right_angle = math.radians(-angle_spread)
        right_outer_x = light_end_x
        right_outer_y = car_width/4 + cone_width * math.cos(right_angle)
        right_outer_z = cone_height * math.sin(-right_angle)
        
        right_inner_x = light_end_x
        right_inner_y = car_width/4 - cone_width * math.cos(right_angle)
        right_inner_z = cone_height * math.sin(-right_angle)


        # Left headlight cone - pointing forward along X-axis with outward angle
        glVertex3f(*left_light_origin)
        glVertex3f(left_outer_x, left_outer_y, left_outer_z)
        glVertex3f(left_inner_x, left_inner_y, left_inner_z)


        # Right headlight cone - pointing forward along X-axis with outward angle
        glVertex3f(*right_light_origin)
        glVertex3f(right_outer_x, right_outer_y, right_outer_z)
        glVertex3f(right_inner_x, right_inner_y, right_inner_z)


        glEnd()
        glDisable(GL_BLEND)


def draw_player_car():
    """Draws the player's car, unless in first-person view."""
    global is_crashed, crash_timer, is_invincible
    
    # Don't draw car in first-person mode
    if is_first_person:
        return


    # Blinking effect for invincibility
    if is_invincible:
        # Blink every 0.1 seconds
        if int(time.time() * 10) % 2 == 0:
            return # Skip drawing this frame to create a blink


    glPushMatrix()
    glTranslatef(player_car_pos[0], player_car_pos[1], player_car_pos[2])


    # This spinning effect is now only for visual flair when the choice is presented
    if game_state == "CRASHED_CHOICE":
        spin_angle = (time.time() * 200) % 360
        glRotatef(spin_angle, 0, 0, 1)


    glRotatef(player_car_angle, 0, 0, 1)
    draw_pixel_car_model(main_color=(0.0, 0.0, 1.0))
    glPopMatrix()


def draw_opponent_car(car_data):
    """Draws an opponent car based on its data."""
    x, y, z, angle, speed, color, previous_y, finished = car_data
    glPushMatrix()
    glTranslatef(x, y, z)
    glRotatef(angle, 0, 0, 1)
    draw_pixel_car_model(main_color=color)
    glPopMatrix()


def draw_pixel_tree(x, y, z, scale=1.0):
    """Draws a simple pixelated tree."""
    glPushMatrix()
    glTranslatef(x, y, z)
    glScalef(scale, scale, scale)


    trunk_color = (0.5, 0.3, 0.1)
    foliage_color = (0.1, 0.6, 0.1)


    if weather_options[weather_selection] == "Winter":
        foliage_color = (0.9, 0.9, 1.0)


    # Trunk
    glColor3f(*trunk_color)
    glPushMatrix()
    glTranslatef(0, 0, 20)
    glScalef(10, 10, 40)
    glutSolidCube(1)
    glPopMatrix()


    # Foliage
    glColor3f(*foliage_color)
    glPushMatrix()
    glTranslatef(0, 0, 60)
    glScalef(40, 40, 40)
    glutSolidCube(1)
    glPopMatrix()


    glPopMatrix()


def draw_mountain(x, y, z, width, height, length, color=(0.5, 0.3, 0.1)):
    """Draws a simple mountain using a pyramid shape."""
    glPushMatrix()
    glTranslatef(x, y, z)
    glColor3f(*color)
    
    glBegin(GL_TRIANGLES)
    # Front face
    glVertex3f(0, 0, height)
    glVertex3f(-width/2, -length/2, 0)
    glVertex3f(width/2, -length/2, 0)
    
    # Right face
    glVertex3f(0, 0, height)
    glVertex3f(width/2, -length/2, 0)
    glVertex3f(width/2, length/2, 0)
    
    # Back face
    glVertex3f(0, 0, height)
    glVertex3f(width/2, length/2, 0)
    glVertex3f(-width/2, length/2, 0)
    
    # Left face
    glVertex3f(0, 0, height)
    glVertex3f(-width/2, length/2, 0)
    glVertex3f(-width/2, -length/2, 0)
    glEnd()
    
    glPopMatrix()


def draw_road_segment_surface(segment_y, road_width=ROAD_WIDTH, segment_length=ROAD_SEGMENT_LENGTH):
    """Draws the asphalt surface of a single road segment."""
    glPushMatrix()
    glTranslatef(0, segment_y, 0)


    offset1 = 80 * math.sin((segment_y) / 1000.0)
    offset2 = 80 * math.sin((segment_y + segment_length) / 1000.0)


    road_color = (0.2, 0.2, 0.2)
    if not is_day:
        road_color = (0.1, 0.1, 0.1)


    glBegin(GL_QUADS)
    draw_colored_quad(
        (-road_width/2 + offset1, -segment_length/2, 1),
        (road_width/2 + offset1, -segment_length/2, 1),
        (road_width/2 + offset2, segment_length/2, 1),
        (-road_width/2 + offset2, segment_length/2, 1),
        road_color
    )
    glEnd()


    glPopMatrix()


def draw_curved_ground(segment_y, segment_length, road_width, ground_color):
    """Draws a single curved ground segment."""
    glPushMatrix()
    glTranslatef(0, segment_y, 0)
    
    offset1 = ROAD_CURVE_AMPLITUDE * math.sin((segment_y) / ROAD_CURVE_FREQUENCY)
    offset2 = ROAD_CURVE_AMPLITUDE * math.sin((segment_y + segment_length) / ROAD_CURVE_FREQUENCY)
    
    road_half_width = road_width / 2
    ground_width = 1000
    
    glBegin(GL_QUADS)
    glColor3f(*ground_color)
    
    # Left side
    glVertex3f(-road_half_width + offset1, -segment_length/2, 0)
    glVertex3f(-ground_width + offset1, -segment_length/2, 0)
    glVertex3f(-ground_width + offset2, segment_length/2, 0)
    glVertex3f(-road_half_width + offset2, segment_length/2, 0)
    
    # Right side
    glVertex3f(road_half_width + offset1, -segment_length/2, 0)
    glVertex3f(road_half_width + offset2, segment_length/2, 0)
    glVertex3f(ground_width + offset2, segment_length/2, 0)
    glVertex3f(ground_width + offset1, -segment_length/2, 0)
    
    glEnd()
    glPopMatrix()


def draw_environment():
    """Draws the background sky."""
    if game_state != "MENU":  # Only set sky color for game scenes, not menu
        sky_color = (0.5, 0.7, 1.0)
        if not is_day:
            sky_color = (0.0, 0.0, 0.1)
        elif weather_options[weather_selection] == "Monsoon":
            sky_color = (0.4, 0.4, 0.5)
        elif weather_options[weather_selection] == "Winter":
            sky_color = (0.6, 0.75, 0.85)


        glClearColor(sky_color[0], sky_color[1], sky_color[2], 1.0)


def draw_nitro_pickup(x, y, z, radius):
    """Draws a rotating, semi-transparent green cylinder."""
    glPushMatrix()
    glTranslatef(x, y, z)
    glRotatef(global_rotation_angle, 0, 1, 0)
    
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    glColor4f(0.0, 1.0, 0.0, 0.7)
    
    quadric = gluNewQuadric()
    gluCylinder(quadric, radius * 0.8, radius * 0.8, radius * 2, 10, 2)
    gluDisk(quadric, 0, radius * 0.8, 10, 1)
    glTranslatef(0,0,radius*2)
    gluDisk(quadric, 0, radius * 0.8, 10, 1)
    gluDeleteQuadric(quadric)


    glDisable(GL_BLEND)
    glPopMatrix()


def draw_boost_effect(color):
    """Draws a dynamic flame-like boost effect."""
    glPushMatrix()
    glTranslatef(player_car_pos[0], player_car_pos[1] - 15, player_car_pos[2])
    glRotatef(player_car_angle - 90, 0, 0, 1)


    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glBegin(GL_QUADS)
    for _ in range(5):
        length = random.uniform(20, 50)
        width = random.uniform(3, 8)
        pos_offset = random.uniform(-5, 5)
        alpha = random.uniform(0.4, 0.8)
        
        glColor4f(color[0], color[1], color[2], alpha)
        
        glVertex3f(pos_offset - width/2, 0, 0)
        glVertex3f(pos_offset + width/2, 0, 0)
        glVertex3f(pos_offset + width/2, -length, 0)
        glVertex3f(pos_offset - width/2, -length, 0)
    glEnd()
    glDisable(GL_BLEND)
    
    glPopMatrix()


def draw_finish_line():
    """Draws a checkered finish line with a smooth, creative shimmering effect."""
    # --- FIX: Vanish the finish line in Timed and Free modes ---
    if mode_options[mode_selection] == "Free Mode" or mode_options[mode_selection] == "Timed":
        return


    global FINISH_LINE_DISTANCE, ROAD_WIDTH
    
    line_z = 2.0  # Raised to prevent Z-fighting
    
    num_segments_y = 4
    segment_length = 15  # Smaller segments for a denser line
    start_y = FINISH_LINE_DISTANCE - (num_segments_y * segment_length / 2)
    
    num_squares_x = 24
    square_size_x = ROAD_WIDTH / num_squares_x


    current_time = time.time()


    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    glBegin(GL_QUADS)
    for i in range(num_segments_y):
        segment_center_y = start_y + i * segment_length
        
        offset1 = ROAD_CURVE_AMPLITUDE * math.sin(segment_center_y / ROAD_CURVE_FREQUENCY)
        offset2 = ROAD_CURVE_AMPLITUDE * math.sin((segment_center_y + segment_length) / ROAD_CURVE_FREQUENCY)
        
        for j in range(num_squares_x):
            # Create a wave that travels across the finish line
            wave = math.sin(current_time * 5 + j * 0.5 + i * 0.8) 
            alpha = 0.6 + 0.4 * wave # Modulate alpha between 0.2 and 1.0
            
            color_toggle = (i + j) % 2 == 0
            base_color = (1.0, 1.0, 1.0) if color_toggle else (0.1, 0.1, 0.1)
            glColor4f(base_color[0], base_color[1], base_color[2], alpha)


            x1 = -ROAD_WIDTH/2 + j * square_size_x
            x2 = x1 + square_size_x


            v1 = (x1 + offset1, segment_center_y - segment_length/2, line_z)
            v2 = (x2 + offset1, segment_center_y - segment_length/2, line_z)
            v3 = (x2 + offset2, segment_center_y + segment_length/2, line_z)
            v4 = (x1 + offset2, segment_center_y + segment_length/2, line_z)
            
            glVertex3f(*v1)
            glVertex3f(*v2)
            glVertex3f(*v3)
            glVertex3f(*v4)
    glEnd()
    
    glDisable(GL_BLEND)


def draw_sparks():
    """Draws crash sparks."""
    glPointSize(5.0)
    glBegin(GL_POINTS)
    for spark in sparks:
        glColor3f(1.0, random.uniform(0.5, 1.0), 0.0)
        glVertex3f(spark[0], spark[1], spark[2])
    glEnd()
    glPointSize(1.0)

def draw_weather_particles():
    """Draws rain or snow particles."""
    if weather_options[weather_selection] == "Summer":
        return


    glPushMatrix()
    glTranslatef(player_car_pos[0], player_car_pos[1], 0)


    if weather_options[weather_selection] == "Monsoon":
        glLineWidth(1.5)
        glColor3f(0.6, 0.7, 0.8)
        glBegin(GL_LINES)
        for p in weather_particles:
            glVertex3f(p[0], p[1], p[2])
            glVertex3f(p[0], p[1] - 5, p[2] - 10)
        glEnd()
    
    elif weather_options[weather_selection] == "Winter":
        glPointSize(3.0)
        glColor3f(1.0, 1.0, 1.0)
        glBegin(GL_POINTS)
        for p in weather_particles:
            glVertex3f(p[0], p[1], p[2])
        glEnd()


    glPopMatrix()


# --- Input Handlers ---
def specialKeyListener(key, x, y):
    """Handles special key inputs (arrow keys)."""
    global key_states, menu_selection
    if game_state == "MENU":
        if key == GLUT_KEY_UP:
            menu_selection = (menu_selection - 1) % len(menu_options)
        elif key == GLUT_KEY_DOWN:
            menu_selection = (menu_selection + 1) % len(menu_options)
    elif game_state == "RACING":
        key_states[key] = True


def specialKeyUpListener(key, key_x, y):
    """Handles special key releases."""
    global key_states
    key_states[key] = False


def keyboardListener(key, x, y):
    """Handles standard keyboard inputs."""
    global key_states, last_space_press_time, is_boosting, boost_level, nitro_amount, boost_timer
    global current_boost_speed_multiplier, player_finished, game_state, menu_selection
    global weather_selection, mode_selection, player_coins, timed_mode_seconds, is_first_person, is_day
    global choice_timer_start, is_crashed, show_finish_popup, is_invincible, invincibility_timer


    key_int = ord(key)
    key_char = key.lower()


    if game_state == "MENU":
        if key_int == 13: # Enter key
            handle_menu_selection()
        elif key_int == 27: # Escape key
             glutLeaveMainLoop()
             
    elif game_state == "RACING":
        if not player_finished:
            # Nitro (Spacebar)
            if key_int == 32:
                current_time = time.time()
                if (current_time - last_space_press_time) < DOUBLE_TAP_THRESHOLD and not is_boosting:
                    if nitro_amount >= NITRO_CONSUMPTION_DOUBLE_TAP:
                        is_boosting = True
                        boost_level = 2
                        current_boost_speed_multiplier = 2.5
                        boost_timer = BOOST_DURATION_DOUBLE_TAP
                        nitro_amount = max(0, nitro_amount - NITRO_CONSUMPTION_DOUBLE_TAP)
                    last_space_press_time = 0
                elif not is_boosting and nitro_amount >= NITRO_CONSUMPTION_SINGLE_TAP:
                    is_boosting = True
                    boost_level = 1
                    current_boost_speed_multiplier = 1.8
                    boost_timer = BOOST_DURATION_SINGLE_TAP
                    nitro_amount = max(0, nitro_amount - NITRO_CONSUMPTION_SINGLE_TAP)
                    last_space_press_time = current_time
            # Timed Mode - Extend Time
            elif key_char == b'c' and mode_options[mode_selection] == "Timed":
                if player_coins >= 10:
                    player_coins -= 10
                    timed_mode_seconds += 15
            # NEW: Camera and Day/Night Toggle
            elif key_char == b'v':
                is_first_person = not is_first_person
            elif key_char == b'x':
                is_day = not is_day
                
        key_states[key_int] = True
        
    elif game_state == "FINISHED":
        if key_int == 13: # Enter key to return to menu
            reset_game()
            
    # --- Handle choices for reborn and time extend ---
    elif game_state == "CRASHED_CHOICE":
        if key_char == b'y':
            if player_coins >= REBORN_COST:
                player_coins -= REBORN_COST
                is_crashed = False
                current_boost_speed_multiplier = 1.0 # Restore speed
                is_invincible = True 
                invincibility_timer = INVINCIBILITY_DURATION 
                game_state = "RACING"
            else: # Not enough coins, end the race
                game_state = "FINISHED"
                show_finish_popup = True
        elif key_char == b'n':
            game_state = "FINISHED"
            show_finish_popup = True


    elif game_state == "TIMED_CHOICE":
        if key_char == b'y':
            if player_coins >= TIME_EXTEND_COST:
                player_coins -= TIME_EXTEND_COST
                timed_mode_seconds += TIME_EXTEND_AMOUNT
                game_state = "RACING"
            else: # Not enough coins, end the race
                game_state = "FINISHED"
                show_finish_popup = True
        elif key_char == b'n':
            game_state = "FINISHED"
            show_finish_popup = True


def keyboardUpListener(key, x, y):
    """Handles regular key releases."""
    global key_states
    key_int = ord(key)
    key_states[key_int] = False


def mouseListener(button, state, x, y):
    """Handles mouse inputs."""
    glutPostRedisplay()


def handle_menu_selection():
    """Handles logic for menu item selection."""
    global game_state, menu_selection, weather_selection, mode_selection, countdown_start_time


    selected_option = menu_options[menu_selection]


    if selected_option.startswith("Start Race"):
        game_state = "COUNTDOWN"
        countdown_start_time = time.time()
    elif selected_option.startswith("Weather"):
        weather_selection = (weather_selection + 1) % len(weather_options)
        menu_options[1] = f"Weather: {weather_options[weather_selection]}"
    elif selected_option.startswith("Mode"):
        mode_selection = (mode_selection + 1) % len(mode_options)
        menu_options[2] = f"Mode: {mode_options[mode_selection]}"
    elif selected_option == "Exit":
        glutLeaveMainLoop()


# --- Game Loop & Rendering ---
def setupCamera():
    """
    Configures the camera's projection and view settings.
    Toggles between third-person and first-person views.
    """
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, window_width / window_height, 0.1, 20000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


    if is_first_person:
        # --- NEW: First-Person Camera ---
        eye_height = 18
        look_ahead_dist = 300


        cam_x = player_car_pos[0]
        cam_y = player_car_pos[1]
        cam_z = player_car_pos[2] + eye_height


        target_y = player_car_pos[1] + look_ahead_dist
        initial_x_offset = player_car_pos[0] - ROAD_CURVE_AMPLITUDE * math.sin(player_car_pos[1] / ROAD_CURVE_FREQUENCY)
        road_x_at_target = ROAD_CURVE_AMPLITUDE * math.sin(target_y / ROAD_CURVE_FREQUENCY)
        cam_target_x = road_x_at_target + initial_x_offset
        cam_target_y = target_y
        cam_target_z = cam_z


        gluLookAt(cam_x, cam_y, cam_z, cam_target_x, cam_target_y, cam_target_z, 0, 0, 1)


    else:
        # --- Original Third-Person Camera ---
        cam_target_x = player_car_pos[0]
        cam_target_y = player_car_pos[1] + 50
        cam_target_z = player_car_pos[2] + 20


        rotation_rad = math.radians(camera_rotation_angle + player_car_angle - 90)
        vertical_rad = math.radians(camera_vertical_angle)


        cam_x = player_car_pos[0] + camera_distance_from_player * math.cos(vertical_rad) * math.cos(rotation_rad)
        cam_y = player_car_pos[1] + camera_distance_from_player * math.cos(vertical_rad) * math.sin(rotation_rad)
        cam_z = player_car_pos[2] + camera_distance_from_player * math.sin(vertical_rad)


        gluLookAt(cam_x, cam_y, cam_z, cam_target_x, cam_target_y, cam_target_z, 0, 0, 1)


def update_player_movement():
    global player_car_pos, player_car_speed, player_car_strafing_speed, key_states, current_boost_speed_multiplier
    global distance_traveled, previous_player_y, player_finished, finished_cars, show_finish_popup
    global player_finish_position, game_time, is_crashed, crash_timer, game_state, player_coins


    # The 'is_crashed' flag is now handled by game state transitions.


    effective_speed = player_car_speed * current_boost_speed_multiplier
    effective_strafing_speed = player_car_strafing_speed * current_boost_speed_multiplier / 1.5


    if not player_finished:
        if key_states.get(GLUT_KEY_UP, False):
            player_car_pos[1] += effective_speed
        if key_states.get(GLUT_KEY_DOWN, False):
            player_car_pos[1] -= effective_speed * 0.5
        if key_states.get(GLUT_KEY_LEFT, False):
            player_car_pos[0] -= effective_strafing_speed
        if key_states.get(GLUT_KEY_RIGHT, False):
            player_car_pos[0] += effective_strafing_speed


    if player_car_pos[1] > previous_player_y:
        distance_traveled += (player_car_pos[1] - previous_player_y)


    previous_player_y = player_car_pos[1]


    if not player_finished and mode_options[mode_selection] == "Competitive" and player_car_pos[1] >= FINISH_LINE_DISTANCE:
        player_car_pos[1] = FINISH_LINE_DISTANCE
        player_finished = True
        finished_cars.append({"id": "player", "time": game_time})
        
        finished_cars.sort(key=lambda x: x["time"])
        for i, car in enumerate(finished_cars):
            if car["id"] == "player":
                player_finish_position = i + 1
                break
        
        if player_finish_position == 1:
            player_coins += 100
        elif player_finish_position == 2:
            player_coins += 50
        elif player_finish_position == 3:
            player_coins += 25


        show_finish_popup = True
        game_state = "FINISHED"


def spawn_new_opponent_car():
    """Spawns a new opponent car ahead of the player."""
    global player_car_pos, ROAD_WIDTH, player_car_speed, opponent_cars
    y_pos = player_car_pos[1] + random.uniform(OPPONENT_SPAWN_AHEAD_DISTANCE * 0.5, OPPONENT_SPAWN_AHEAD_DISTANCE)
    
    # --- FIX: Spawn cars relative to the road's curve ---
    road_x_at_spawn = ROAD_CURVE_AMPLITUDE * math.sin(y_pos / ROAD_CURVE_FREQUENCY)
    x_pos = road_x_at_spawn + random.uniform(-ROAD_WIDTH/2 + 20, ROAD_WIDTH/2 - 20)
    
    speed = random.uniform(player_car_speed * 0.8, player_car_speed * 1.2)
    color = (random.uniform(0.4, 1.0), random.uniform(0.4, 1.0), random.uniform(0.4, 1.0))
    opponent_cars.append([x_pos, y_pos, 10, 90, speed, color, y_pos, False])


def update_opponent_cars():
    """Updates the positions of opponent cars, making them follow the road's curve."""
    global opponent_cars, player_car_pos, cars_passed, finished_cars, game_time


    if mode_options[mode_selection] != "Competitive":
        cars_to_remove = []
        for i, car in enumerate(opponent_cars):
            if car[1] < player_car_pos[1] - OPPONENT_DESPAWN_DISTANCE:
                cars_to_remove.append(i)
        
        for i in sorted(cars_to_remove, reverse=True):
            opponent_cars.pop(i)


        while len(opponent_cars) < NUM_OPPONENT_CARS:
            spawn_new_opponent_car()


    for i in range(len(opponent_cars)):
        car = opponent_cars[i]
        
        if car[7]:
            car[4] = 0
            continue


        current_car_y = car[1]
        
        road_x_offset = ROAD_CURVE_AMPLITUDE * math.sin((current_car_y) / ROAD_CURVE_FREQUENCY)
        initial_x_offset = car[0] - ROAD_CURVE_AMPLITUDE * math.sin((car[6]) / ROAD_CURVE_FREQUENCY)
        car[0] = road_x_offset + initial_x_offset


        next_y = current_car_y + car[4]
        next_road_x_offset = ROAD_CURVE_AMPLITUDE * math.sin((next_y) / ROAD_CURVE_FREQUENCY)
        delta_x = (next_road_x_offset + initial_x_offset) - car[0]
        delta_y = next_y - current_car_y
        
        car[3] = math.degrees(math.atan2(delta_x, delta_y)) + 90
        car[1] += car[4]


        if not player_finished and car[1] < player_car_pos[1] and car[6] >= player_car_pos[1]:
            cars_passed += 1
            
        car[6] = current_car_y


        if mode_options[mode_selection] == "Competitive" and car[1] >= FINISH_LINE_DISTANCE and not car[7]:
            car[1] = FINISH_LINE_DISTANCE
            car[7] = True
            finished_cars.append({"id": f"opponent_{i}", "time": game_time})
            car[4] = 0
                        
def update_trees():
    """Updates tree positions to recycle them."""
    global fixed_trees, player_car_pos, TREE_SCROLL_DISTANCE
    
    for i in range(len(fixed_trees)):
        tree = fixed_trees[i]
        tree_x, tree_y_offset, tree_scale = tree


        if tree_y_offset < player_car_pos[1] - TREE_SCROLL_DISTANCE / 2:
            tree_y_offset = player_car_pos[1] + TREE_SCROLL_DISTANCE / 2 + random.uniform(0, TREE_SCROLL_DISTANCE / 2)
            road_x_offset = ROAD_CURVE_AMPLITUDE * math.sin((tree_y_offset) / ROAD_CURVE_FREQUENCY)
            side = random.choice([-1, 1])
            tree_x = road_x_offset + side * random.uniform(TREE_MIN_X, TREE_MAX_X)
            tree_scale = random.uniform(0.8, 1.2)


        fixed_trees[i] = [tree_x, tree_y_offset, tree_scale]




def update_mountains():
    """Updates mountain positions to recycle them."""
    global mountains, player_car_pos, MOUNTAIN_SCROLL_DISTANCE


    for i in range(len(mountains)):
        mountain = mountains[i]
        mountain_x, mountain_y_offset, mountain_width, mountain_height, mountain_length = mountain


        if mountain_y_offset < player_car_pos[1] - MOUNTAIN_SCROLL_DISTANCE / 2:
            mountain_y_offset = player_car_pos[1] + MOUNTAIN_SCROLL_DISTANCE / 2 + random.uniform(0, MOUNTAIN_SCROLL_DISTANCE / 2)
            side = random.choice([-1, 1])
            mountain_x = side * random.uniform(MOUNTAIN_MIN_X, MOUNTAIN_MAX_X)
            mountain_width = random.uniform(100, 200)
            mountain_height = random.uniform(50, 300)
            mountain_length = random.uniform(100, 200)
            mountains[i] = [mountain_x, mountain_y_offset, mountain_width, mountain_height, mountain_length]


def add_new_nitro_pickup():
    """Adds a new nitro pickup ahead of the player."""
    global player_car_pos, ROAD_WIDTH, NITRO_RADIUS, NITRO_SPAWN_AHEAD_DISTANCE
    
    spawn_y = player_car_pos[1] + random.uniform(NITRO_RADIUS * 2, NITRO_SPAWN_AHEAD_DISTANCE)
    road_x_offset = ROAD_CURVE_AMPLITUDE * math.sin((spawn_y) / ROAD_CURVE_FREQUENCY)
    nitro_x_relative = random.uniform(-ROAD_WIDTH/2 + NITRO_RADIUS, ROAD_WIDTH/2 - NITRO_RADIUS)
    nitro_x = road_x_offset + nitro_x_relative


    if mode_options[mode_selection] == "Competitive":
        nitro_y = min(spawn_y, FINISH_LINE_DISTANCE - 100)
    else:
        nitro_y = spawn_y


    nitro_z = 1 + NITRO_RADIUS
    nitro_pickups.append([nitro_x, nitro_y, nitro_z, False, nitro_x_relative])


def update_nitro_pickups():
    global nitro_pickups, nitro_amount, player_car_pos, NITRO_RADIUS, CAR_COLLISION_RADIUS
    global MAX_NITRO_PICKUPS_ON_SCREEN, NITRO_SPAWN_AHEAD_DISTANCE, NITRO_PICKUP_AMOUNT, MAX_NITRO_AMOUNT, player_finished


    pickups_to_remove = []
    for i, pickup_data in enumerate(nitro_pickups):
        nitro_x, nitro_y, nitro_z, is_collected, nitro_x_relative = pickup_data


        road_x_offset = ROAD_CURVE_AMPLITUDE * math.sin((nitro_y) / ROAD_CURVE_FREQUENCY)
        nitro_x = road_x_offset + nitro_x_relative
        nitro_pickups[i][0] = nitro_x


        if not is_collected and not is_crashed:
            car_front_x = player_car_pos[0]
            car_front_y = player_car_pos[1] + CAR_COLLISION_RADIUS
            dist = math.sqrt((car_front_x - nitro_x)**2 + (car_front_y - nitro_y)**2)
            if dist < CAR_COLLISION_RADIUS + NITRO_RADIUS:
                nitro_amount = min(MAX_NITRO_AMOUNT, nitro_amount + NITRO_PICKUP_AMOUNT)
                pickups_to_remove.append(i)
        
        despawn_condition = nitro_y < player_car_pos[1] - NITRO_SPAWN_AHEAD_DISTANCE / 2
        if mode_options[mode_selection] == "Competitive":
            despawn_condition = despawn_condition or nitro_y >= FINISH_LINE_DISTANCE
        
        if despawn_condition:
            pickups_to_remove.append(i)


    for i in sorted(pickups_to_remove, reverse=True):
        if i < len(nitro_pickups):
            nitro_pickups.pop(i)
        
    refill_condition = not player_finished if mode_options[mode_selection] == "Competitive" else True
    while refill_condition and len(nitro_pickups) < MAX_NITRO_PICKUPS_ON_SCREEN:
        add_new_nitro_pickup()


def handle_boost():
    """Manages the boost timer and state."""
    global is_boosting, boost_timer, boost_level, current_boost_speed_multiplier


    if is_boosting:
        boost_timer -= 1.0 / 60.0
        if boost_timer <= 0:
            is_boosting = False
            boost_level = 0
            current_boost_speed_multiplier = 1.0
            boost_timer = 0


def update_countdown():
    global game_state, countdown_start_time, countdown_text, start_time
    elapsed = time.time() - countdown_start_time
    if elapsed < 1:
        countdown_text = "3"
    elif elapsed < 2:
        countdown_text = "2"
    elif elapsed < 3:
        countdown_text = "1"
    elif elapsed < 4:
        countdown_text = "GO!"
    else:
        game_state = "RACING"
        start_time = time.time()


def spawn_sparks(x, y, z, count=20):
    """Creates a burst of sparks at a location."""
    global sparks
    for _ in range(count):
        vx = random.uniform(-2, 2)
        vy = random.uniform(-1, 3)
        vz = random.uniform(1, 4)
        life = random.uniform(0.3, 0.8)
        sparks.append([x, y, z, vx, vy, vz, life])


def update_sparks():
    """Moves and fades out sparks."""
    global sparks
    sparks_to_keep = []
    for spark in sparks:
        spark[6] -= 1.0 / 60.0
        if spark[6] > 0:
            spark[0] += spark[3]
            spark[1] += spark[4]
            spark[2] += spark[5]
            spark[5] -= 0.1
            sparks_to_keep.append(spark)
    sparks = sparks_to_keep


def trigger_crash():
    """Activates the crash state or the choice to reborn."""
    global is_crashed, current_boost_speed_multiplier, is_boosting, game_state, choice_timer_start
    if game_state == "RACING":
        is_crashed = True
        is_boosting = False
        current_boost_speed_multiplier = 0 # Stop the car immediately
        spawn_sparks(player_car_pos[0], player_car_pos[1], player_car_pos[2])
        
        game_state = "CRASHED_CHOICE"
        choice_timer_start = time.time()


def check_collisions():
    """Checks for all types of player collisions."""
    global player_car_pos, opponent_cars, is_crashed, current_boost_speed_multiplier, is_invincible


    if is_crashed or player_finished or game_state != "RACING":
        return


    # Only check for car/fireball collisions if not invincible
    if not is_invincible:
        # Collision with opponent cars
        for car in opponent_cars:
            if car[7]: continue
            dist = math.sqrt((player_car_pos[0] - car[0])**2 + (player_car_pos[1] - car[1])**2)
            if dist < CAR_COLLISION_RADIUS * 2:
                trigger_crash()
                return # Exit immediately after a crash is triggered
    
    # Road edge collision check should always happen, regardless of invincibility
    road_x_at_player = ROAD_CURVE_AMPLITUDE * math.sin(player_car_pos[1] / ROAD_CURVE_FREQUENCY)
    left_boundary = road_x_at_player - ROAD_WIDTH / 2
    right_boundary = road_x_at_player + ROAD_WIDTH / 2
    is_off_road = player_car_pos[0] < left_boundary or player_car_pos[0] > right_boundary
    
    if is_off_road:
        # Don't affect boost speed, just the base multiplier if not boosting
        if not is_boosting:
            current_boost_speed_multiplier = 0.3
        if random.random() < 0.3:
             spawn_sparks(player_car_pos[0], player_car_pos[1], player_car_pos[2], count=2)
    elif not is_boosting:
        # If back on the road and not boosting, restore normal speed.
        current_boost_speed_multiplier = 1.0

def init_weather_particles():
    """Initializes particles for rain or snow."""
    global weather_particles
    weather_particles = []
    for _ in range(NUM_WEATHER_PARTICLES):
        x = random.uniform(-1000, 1000)
        y = random.uniform(-1000, 1000)
        z = random.uniform(10, 800)
        weather_particles.append([x, y, z])


def update_weather_particles():
    """Updates rain or snow particle positions."""
    global weather_particles
    for i in range(len(weather_particles)):
        if weather_options[weather_selection] == "Monsoon":
            weather_particles[i][2] -= 25
            weather_particles[i][1] -= 10
        elif weather_options[weather_selection] == "Winter":
            weather_particles[i][2] -= 2
            weather_particles[i][0] += math.sin(weather_particles[i][2] * 0.1) * 0.5


        if weather_particles[i][2] < 0:
            weather_particles[i][0] = random.uniform(-1000, 1000)
            weather_particles[i][1] = random.uniform(-1000, 1000)
            weather_particles[i][2] = random.uniform(700, 800)


def get_player_rank():
    """Calculates the player's current rank."""
    global player_car_pos, opponent_cars, player_rank, finished_cars, player_finished, player_finish_position


    if mode_options[mode_selection] != "Competitive":
        player_rank = 1
        return


    if player_finished:
        player_rank = player_finish_position
        return


    all_active_cars = [{"id": "player", "y": player_car_pos[1]}]
    for i, car_data in enumerate(opponent_cars):
        if not car_data[7]:
            all_active_cars.append({"id": f"opponent_{i}", "y": car_data[1]})


    all_active_cars.sort(key=lambda car: car["y"], reverse=True)


    for i, car in enumerate(all_active_cars):
        if car["id"] == "player":
            player_rank = i + 1
            break


def update_game_time():
    global game_time, start_time, timed_mode_seconds, game_state, show_finish_popup, choice_timer_start
    if game_state == "RACING":
        if mode_options[mode_selection] == "Timed":
            timed_mode_seconds -= 1.0 / 60.0
            if timed_mode_seconds <= 0:
                timed_mode_seconds = 0
                game_state = "TIMED_CHOICE"
                choice_timer_start = time.time()
        else:
            game_time = int(time.time() - start_time)


def update_choice_timers():
    """Handles the countdown for respawn/time-extend choices."""
    global game_state, choice_timer_start, show_finish_popup
    elapsed = time.time() - choice_timer_start
    if elapsed >= CHOICE_DURATION:
        if game_state == "CRASHED_CHOICE" or game_state == "TIMED_CHOICE":
            game_state = "FINISHED"
            show_finish_popup = True


def update_invincibility():
    """Manages the player's invincibility timer after respawning."""
    global is_invincible, invincibility_timer
    if is_invincible:
        invincibility_timer -= 1.0 / 60.0 # Assuming 60 FPS
        if invincibility_timer <= 0:
            is_invincible = False


def idle():
    """Idle function that runs continuously."""
    global game_state, global_rotation_angle


    if game_state == "COUNTDOWN":
        update_countdown()
    elif game_state == "RACING":
        update_invincibility() # Handle invincibility timer
        update_player_movement()
        update_nitro_pickups()
        handle_boost()
        update_opponent_cars()
        update_trees()
        update_mountains()
        update_game_time()
        get_player_rank()
        check_collisions()
        update_sparks()
        update_weather_particles()
    elif game_state == "CRASHED_CHOICE" or game_state == "TIMED_CHOICE":
        update_choice_timers()
        update_sparks()


    global_rotation_angle = (global_rotation_angle + 2) % 360
    glutPostRedisplay()


def showScreen():
    """Display function to render the game scene."""
    draw_environment()  # This sets the sky color based on weather and time
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    
    if game_state == "MENU":
        draw_menu()
    else:
        glViewport(0, 0, window_width, window_height)
        setupCamera()
        draw_game_scene()
        draw_hud()


    glutSwapBuffers()


def draw_menu():
    """Draws the main menu UI with starry background."""
    # Set up orthographic projection for 2D rendering
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, window_width, 0, window_height)
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Clear with black background for menu
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glClear(GL_COLOR_BUFFER_BIT)
    
    # Draw the starry background
    draw_stars_for_menu()
    
    # Draw menu text
    headline = "ARM RACING GAME"
    text_scale = 0.8
    text_width = get_stroke_text_width(headline) * text_scale
    start_x = (window_width - text_width) / 2
    
    draw_text(start_x, window_height - 100, headline, font="large", color=(1, 1, 0))
    
    for i, option in enumerate(menu_options):
        color = (1, 1, 0) if i == menu_selection else (1, 1, 1)
        draw_text(window_width / 2 - 100, window_height / 2 - i * 50, option, font=GLUT_BITMAP_HELVETICA_18, color=color)


    draw_text(10, 10, f"Coins: {player_coins}", font=GLUT_BITMAP_HELVETICA_18, color=(1,0,0))
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def draw_game_scene():
    """Renders all 3D elements of the game world."""
    ground_color = (0.4, 0.5, 0.1)
    if not is_day:
        ground_color = (0.1, 0.15, 0.05)
    elif weather_options[weather_selection] == "Winter":
        ground_color = (0.9, 0.9, 1.0)
    elif weather_options[weather_selection] == "Monsoon":
        ground_color = (0.3, 0.35, 0.1)


    road_min_y = player_car_pos[1] - 3000
    road_max_y = player_car_pos[1] + 5000 
    
    num_segments = int((road_max_y - road_min_y) / ROAD_SEGMENT_LENGTH)
    for i in range(num_segments):
        segment_center_y = road_min_y + i * ROAD_SEGMENT_LENGTH
        
        offset1 = ROAD_CURVE_AMPLITUDE * math.sin((segment_center_y) / ROAD_CURVE_FREQUENCY)
        offset2 = ROAD_CURVE_AMPLITUDE * math.sin((segment_center_y + ROAD_SEGMENT_LENGTH) / ROAD_CURVE_FREQUENCY)


        draw_curved_ground(segment_center_y, ROAD_SEGMENT_LENGTH, ROAD_WIDTH, ground_color)
        
        road_color = (0.2, 0.2, 0.2) if is_day else (0.1, 0.1, 0.1)
        glPushMatrix()
        glTranslatef(0, segment_center_y, 0)
        glBegin(GL_QUADS)
        draw_colored_quad(
            (-ROAD_WIDTH/2 + offset1, -ROAD_SEGMENT_LENGTH/2, 1),
            (ROAD_WIDTH/2 + offset1, -ROAD_SEGMENT_LENGTH/2, 1),
            (ROAD_WIDTH/2 + offset2, ROAD_SEGMENT_LENGTH/2, 1),
            (-ROAD_WIDTH/2 + offset2, ROAD_SEGMENT_LENGTH/2, 1),
            road_color
        )
        glEnd()
        glPopMatrix()


        line_z = 1.2
        edge_line_thickness = 5
        line_color = (1.0, 1.0, 1.0) if is_day else (0.6, 0.6, 0.6)


        glPushMatrix()
        glTranslatef(0, segment_center_y, line_z)
        glBegin(GL_QUADS)
        draw_colored_quad((-ROAD_WIDTH/2 + offset1, -ROAD_SEGMENT_LENGTH/2, 0),(-ROAD_WIDTH/2 + offset1 + edge_line_thickness, -ROAD_SEGMENT_LENGTH/2, 0),(-ROAD_WIDTH/2 + offset2 + edge_line_thickness, ROAD_SEGMENT_LENGTH/2, 0),(-ROAD_WIDTH/2 + offset2, ROAD_SEGMENT_LENGTH/2, 0),line_color)
        glEnd()
        glPopMatrix()


        glPushMatrix()
        glTranslatef(0, segment_center_y, line_z)
        glBegin(GL_QUADS)
        draw_colored_quad((ROAD_WIDTH/2 - edge_line_thickness + offset1, -ROAD_SEGMENT_LENGTH/2, 0),(ROAD_WIDTH/2 + offset1, -ROAD_SEGMENT_LENGTH/2, 0),(ROAD_WIDTH/2 + offset2, ROAD_SEGMENT_LENGTH/2, 0),(ROAD_WIDTH/2 - edge_line_thickness + offset2, ROAD_SEGMENT_LENGTH/2, 0),line_color)
        glEnd()
        glPopMatrix()


        # Draw three solid center lines
        line_z = 1.2
        line_color = (1.0, 1.0, 1.0) if is_day else (0.6, 0.6, 0.6)


        # Calculate positions for the three lines
        center_line_offset = 0
        left_line_offset = -ROAD_WIDTH / 3
        right_line_offset = ROAD_WIDTH / 3


        # Draw the three solid lines for the entire segment
        glPushMatrix()
        glTranslatef(0, segment_center_y, line_z)
        glBegin(GL_QUADS)
        # Center line
        draw_colored_quad(
            (center_line_offset - ROAD_LINE_WIDTH/2 + offset1, -ROAD_SEGMENT_LENGTH/2, 0),
            (center_line_offset + ROAD_LINE_WIDTH/2 + offset1, -ROAD_SEGMENT_LENGTH/2, 0),
            (center_line_offset + ROAD_LINE_WIDTH/2 + offset2, ROAD_SEGMENT_LENGTH/2, 0),
            (center_line_offset - ROAD_LINE_WIDTH/2 + offset2, ROAD_SEGMENT_LENGTH/2, 0),
            line_color
        )
        # Left line
        draw_colored_quad(
            (left_line_offset+18 - ROAD_LINE_WIDTH/2 + offset1, -ROAD_SEGMENT_LENGTH/2, 0),
            (left_line_offset+18 + ROAD_LINE_WIDTH/2 + offset1, -ROAD_SEGMENT_LENGTH/2, 0),
            (left_line_offset+18 + ROAD_LINE_WIDTH/2 + offset2, ROAD_SEGMENT_LENGTH/2, 0),
            (left_line_offset+18 - ROAD_LINE_WIDTH/2 + offset2, ROAD_SEGMENT_LENGTH/2, 0),
            line_color
        )
        # Right line
        draw_colored_quad(
            (right_line_offset-18 - ROAD_LINE_WIDTH/2 + offset1, -ROAD_SEGMENT_LENGTH/2, 0),
            (right_line_offset-18 + ROAD_LINE_WIDTH/2 + offset1, -ROAD_SEGMENT_LENGTH/2, 0),
            (right_line_offset-18 + ROAD_LINE_WIDTH/2 + offset2, ROAD_SEGMENT_LENGTH/2, 0),
            (right_line_offset-18 - ROAD_LINE_WIDTH/2 + offset2, ROAD_SEGMENT_LENGTH/2, 0),
            line_color
        )
        glEnd()
        glPopMatrix()


    draw_finish_line()


    for mountain in mountains:
        draw_mountain(mountain[0], mountain[1], 0, mountain[2], mountain[3], mountain[4])
    for tree in fixed_trees:
        draw_pixel_tree(tree[0], tree[1], 0, tree[2])


    for nitro_data in nitro_pickups:
        if not nitro_data[3]:
            draw_nitro_pickup(nitro_data[0], nitro_data[1], nitro_data[2], NITRO_RADIUS)


    if not is_first_person:
        draw_player_car()
        if is_boosting:
            if boost_level == 1: draw_boost_effect((0.2, 0.2, 1.0))
            elif boost_level == 2: draw_boost_effect((1.0, 0.2, 0.2))
    
    draw_sparks()


    for car in opponent_cars:
        draw_opponent_car(car)
    
    draw_weather_particles()


def draw_hud():
    """Draws all 2D UI elements over the game scene."""
    draw_text(10, window_height - 30, f"DIST: {int(distance_traveled)}", font=GLUT_BITMAP_HELVETICA_18)
    draw_text(window_width - 250, window_height - 30, f"NITRO: {int(nitro_amount)}/{MAX_NITRO_AMOUNT}", font=GLUT_BITMAP_HELVETICA_18, color=(1,1,1))
    draw_text(10, 10, f"Coins: {player_coins}", font=GLUT_BITMAP_HELVETICA_18, color=(1,0,0))
    
    if mode_options[mode_selection] == "Competitive":
        draw_text(window_width - 400, window_height - 30, f"POS: {player_rank}/{NUM_OPPONENT_CARS + 1}", font=GLUT_BITMAP_HELVETICA_18)
    elif mode_options[mode_selection] == "Timed":
        draw_text(window_width / 2 - 50, window_height - 30, f"TIME: {int(timed_mode_seconds)}", font=GLUT_BITMAP_HELVETICA_18, color=(1,1,1))
        draw_text(window_width / 2 - 150, 10, "Press 'C' to add 15s for 10 coins", font=GLUT_BITMAP_HELVETICA_18,color=(1,0,0))


    if game_state == "COUNTDOWN":
        draw_text(window_width / 2 - 100, window_height / 2, countdown_text, font="large", color=(1, 0, 0))


    # Draw choice pop-ups
    if game_state == "CRASHED_CHOICE":
        time_left = max(0, CHOICE_DURATION - (time.time() - choice_timer_start))
        draw_text(window_width / 2 - 490, window_height / 2 - 250, f"YOU CRASHED! Respawn for {REBORN_COST} coins?", font=GLUT_BITMAP_HELVETICA_18, color=(1,0,0))
        draw_text(window_width / 2 - 490, window_height / 2-280, f"Press Y (Yes) or N (No). Time: {int(time_left)+1}s", font=GLUT_BITMAP_HELVETICA_18, color=(1,0,0))
        if player_coins < REBORN_COST:
            draw_text(window_width / 2 - 490, window_height / 2 - 310, "Not enough coins!", font=GLUT_BITMAP_HELVETICA_18, color=(1,0,0))


    if game_state == "TIMED_CHOICE":
        time_left = max(0, CHOICE_DURATION - (time.time() - choice_timer_start))
        draw_text(window_width / 2 - 490, window_height / 2 - 250, f"TIME'S UP! Extend for {TIME_EXTEND_COST} coins?", font=GLUT_BITMAP_HELVETICA_18, color=(1,0,0))
        draw_text(window_width / 2 - 490, window_height / 2-280, f"Press Y (Yes) or N (No). Time: {int(time_left)+1}s", font=GLUT_BITMAP_HELVETICA_18, color=(1,0,0))
        if player_coins < TIME_EXTEND_COST:
            draw_text(window_width / 2 - 490, window_height / 2 - 310, "Not enough coins!", font=GLUT_BITMAP_HELVETICA_18, color=(1,0,0))


    if show_finish_popup:
        draw_text(window_width / 2 - 250, window_height / 2 + 20, "RACE OVER!", font="large", color=(1,0,0))
        if mode_options[mode_selection] == "Competitive":
            if player_finish_position == 0:
                draw_text(window_width / 2 - 490, window_height / 2-300, "You did not finish the race.", font=GLUT_BITMAP_HELVETICA_18, color=(1,0,0))
            else:
                suffix = {1: "st", 2: "nd", 3: "rd"}.get(player_finish_position % 10, "th") if not 10 < player_finish_position % 100 < 20 else "th"
                draw_text(window_width / 2 - 490, window_height / 2-300, f"YOU FINISHED {player_finish_position}{suffix}!", font=GLUT_BITMAP_HELVETICA_18, color=(1,0,0))
                draw_text(window_width / 2 - 490, window_height / 2 - 270, f"Time: {game_time}s", font=GLUT_BITMAP_HELVETICA_18, color=(1,0,0))
        elif mode_options[mode_selection] == "Timed":
            draw_text(window_width / 2 - 490, window_height / 2-270, "TIME'S UP!", font=GLUT_BITMAP_HELVETICA_18, color=(1,0,0))
            draw_text(window_width / 2 - 490, window_height / 2 - 300, f"Distance: {int(distance_traveled)}", font=GLUT_BITMAP_HELVETICA_18, color=(1,0,0))
        
        draw_text(window_width / 2 - 490, window_height / 2 - 330, "Press Enter to return to Menu", font=GLUT_BITMAP_HELVETICA_18, color=(1,0,0))


def reset_game():
    """Resets all game variables for a new race."""
    global player_car_pos, player_car_angle, opponent_cars, cars_passed, game_time
    global distance_traveled, previous_player_y, player_finished, show_finish_popup, finished_cars, player_finish_position
    global is_crashed, nitro_amount, nitro_pickups, game_state, timed_mode_seconds, is_day, is_first_person
    global is_invincible, invincibility_timer


    player_car_pos = [0, -200, 10]
    player_car_angle = 90
    player_finished = False
    is_crashed = False
    show_finish_popup = False
    player_finish_position = 0 
    
    distance_traveled = 0.0
    previous_player_y = -200.0
    game_time = 0
    cars_passed = 0
    
    nitro_amount = 0
    timed_mode_seconds = 60
    is_day = True
    is_first_person = False 
    is_invincible = False # Reset invincibility
    invincibility_timer = 0.0


    opponent_cars = []
    finished_cars = []
    nitro_pickups = []
    init_game_objects()
    game_state = "MENU"


# --- Main Initialization ---
def init_game_objects():
    """Initializes all dynamic game objects like cars, trees, etc."""
    global opponent_cars, previous_player_y, mountains, fixed_trees, nitro_pickups, stars_for_menu
    
    opponent_cars.clear()
    fixed_trees.clear()
    mountains.clear()
    nitro_pickups.clear()
    stars_for_menu.clear()  # Clear any existing stars


    for i in range(NUM_OPPONENT_CARS):
        y_pos = -200 + (i + 1) * 100
        
        # --- FIX: Spawn cars relative to the road's curve ---
        road_x_at_spawn = ROAD_CURVE_AMPLITUDE * math.sin(y_pos / ROAD_CURVE_FREQUENCY)
        x_pos = road_x_at_spawn + random.uniform(-ROAD_WIDTH / 2 + 20, ROAD_WIDTH / 2 - 20)
        
        speed = random.uniform(player_car_speed * 0.8, player_car_speed * 1.2)
        color = (random.uniform(0.4, 1.0), random.uniform(0.4, 1.0), random.uniform(0.4, 1.0))
        opponent_cars.append([x_pos, y_pos, 10, 90, speed, color, y_pos, False])


    previous_player_y = player_car_pos[1]


    for i in range(NUM_FIXED_TREES):
        side = random.choice([-1, 1])
        x_pos = side * random.uniform(TREE_MIN_X, TREE_MAX_X)
        y_pos_offset = player_car_pos[1] + random.uniform(-TREE_DISPLAY_RANGE, TREE_DISPLAY_RANGE)
        scale = random.uniform(0.8, 1.2)
        fixed_trees.append([x_pos, y_pos_offset, scale])


    for i in range(NUM_MOUNTAINS):
        side = random.choice([-1, 1])
        x_pos = side * random.uniform(MOUNTAIN_MIN_X, MOUNTAIN_MAX_X)
        y_pos_offset = player_car_pos[1] + random.uniform(-MOUNTAIN_DISPLAY_RANGE, MOUNTAIN_DISPLAY_RANGE)
        width = random.uniform(100, 200)
        height = random.uniform(50, 300)
        length = random.uniform(100, 200)
        mountains.append([x_pos, y_pos_offset, width, height, length])


    for i in range(MAX_NITRO_PICKUPS_ON_SCREEN):
        add_new_nitro_pickup()
    
    # Initialize stars for menu background
    for i in range(NUM_MENU_STARS):
        x = random.uniform(0, window_width)
        y = random.uniform(0, window_height)
        stars_for_menu.append([x, y])
    
    init_weather_particles()


def main():
    """Main function to initialize and run the game."""
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH | GLUT_MULTISAMPLE)
    glutInitWindowSize(window_width, window_height)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"ARM RACING GAME") 
    
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_MULTISAMPLE)
    
    reset_game() 


    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutKeyboardUpFunc(keyboardUpListener)
    glutSpecialFunc(specialKeyListener)
    glutSpecialUpFunc(specialKeyUpListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)


    glutMainLoop()


if __name__ == "__main__":
    main()
