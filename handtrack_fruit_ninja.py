
import cv2
import mediapipe as mp
import pygame
import random
import math
import time
import sys
import os

pygame.init()

# ---------------- WINDOW ----------------
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fruit Ninja - Hand Slice Arcade")
clock = pygame.time.Clock()

font = pygame.font.SysFont("Arial", 27, bold=True)
small_font = pygame.font.SysFont("Arial", 19, bold=True)
big_font = pygame.font.SysFont("Arial", 58, bold=True)

WHITE = (255, 255, 255)
GOLD = (255, 220, 60)
GREEN = (70, 255, 145)
RED = (255, 65, 85)
DARK = (12, 14, 38)

# ---------------- FRUIT IMAGES ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRUIT_DIR = os.path.join(BASE_DIR, "assets", "fruits")

fruit_names = ["apple", "mango", "grapes", "banana", "watermelon"]
fruit_images = {}

for name in fruit_names:
    path = os.path.join(FRUIT_DIR, name + ".png")
    if os.path.exists(path):
        image = pygame.image.load(path).convert_alpha()
        fruit_images[name] = pygame.transform.smoothscale(
            image, (76, 76)
        )
    else:
        print("Missing fruit image:", path)

# ---------------- HAND TRACKING ----------------
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
)

# ---------------- CAMERA ----------------

camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not camera.isOpened():
    print("Webcam not detected!")
    hands.close()
    pygame.quit()
    sys.exit()

# ---------------- GAME VARIABLES ----------------
fruits = []
particles = []
popups = []
trail = []

score = 0
game_duration = 30
start_time = time.time()
spawn_timer = 0
finger_position = None
previous_finger = None
game_over = False

# ---------------- BACKGROUND ----------------
stars = [
    (random.randrange(WIDTH), random.randrange(HEIGHT),
     random.randrange(1, 4))
    for _ in range(90)
]

def draw_background():
    # Deep blue-purple gradient
    for y in range(0, HEIGHT, 4):
        ratio = y / HEIGHT
        color = (
            int(13 + 18 * ratio),
            int(12 + 8 * ratio),
            int(42 + 45 * ratio)
        )
        pygame.draw.rect(screen, color, (0, y, WIDTH, 4))

    # Neon grid
    for x in range(0, WIDTH, 65):
        pygame.draw.line(
            screen, (30, 35, 75), (x, 0), (x, HEIGHT), 1
        )

    for y in range(0, HEIGHT, 65):
        pygame.draw.line(
            screen, (30, 35, 75), (0, y), (WIDTH, y), 1
        )

    # Decorative glowing dots
    for x, y, radius in stars:
        pygame.draw.circle(
            screen, (65, 70, 125), (x, y), radius
        )

def draw_panel(rect, color=(20, 24, 58), border=GOLD):
    panel = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
    pygame.draw.rect(
        panel, (*color, 225),
        (0, 0, rect[2], rect[3]), border_radius=18
    )
    pygame.draw.rect(
        panel, (*border, 210),
        (0, 0, rect[2], rect[3]), 2, border_radius=18
    )
    screen.blit(panel, rect[:2])

def show_text(text, x, y, color=WHITE, selected_font=font):
    surface = selected_font.render(text, True, color)
    screen.blit(surface, (x, y))

# ---------------- FRUIT CREATION ----------------
def create_fruit():
    is_bomb = random.random() < 0.16

    name = random.choice(fruit_names)
    radius = 34

    fruits.append({
        "x": random.randint(75, WIDTH - 75),
        "y": HEIGHT + 50,
        "radius": radius,
        "speed_y": random.uniform(-15, -11),
        "speed_x": random.uniform(-3, 3),
        "rotation": random.randint(-20, 20),
        "spin": random.uniform(-2.5, 2.5),
        "bomb": is_bomb,
        "name": name
    })

def draw_fruit(fruit):
    x = int(fruit["x"])
    y = int(fruit["y"])
    radius = fruit["radius"]

    if fruit["bomb"]:
        # Glowing bomb
        pygame.draw.circle(screen, (90, 20, 45), (x, y), radius + 8)
        pygame.draw.circle(screen, (255, 50, 65), (x, y), radius + 3, 3)
        pygame.draw.circle(screen, (28, 27, 43), (x, y), radius)
        pygame.draw.circle(screen, (240, 70, 70), (x, y), radius, 3)
        pygame.draw.circle(screen, GOLD, (x + 9, y - 10), 6)
        pygame.draw.line(
            screen, (255, 160, 50),
            (x + 8, y - radius + 3),
            (x + 18, y - radius - 10), 5
        )
        pygame.draw.circle(
            screen, WHITE, (x + 19, y - radius - 11), 3
        )
    else:
        image = fruit_images.get(fruit["name"])

        if image:
            rotated = pygame.transform.rotate(
                image, fruit["rotation"]
            )
            rect = rotated.get_rect(center=(x, y))
            screen.blit(rotated, rect)
        else:
            pygame.draw.circle(
                screen, (255, 100, 90), (x, y), radius
            )

# ---------------- SLICE EFFECTS ----------------
def create_slice_effect(x, y, bomb=False):
    if bomb:
        colors = [(255, 55, 65), (255, 160, 50), GOLD]
        count = 28
    else:
        colors = [
            (255, 80, 100), (255, 220, 80),
            (100, 255, 170), (90, 210, 255),
            (255, 255, 255)
        ]
        count = 20

    for _ in range(count):
        angle = random.uniform(0, math.tau)
        speed = random.uniform(2, 8)

        particles.append({
            "x": float(x),
            "y": float(y),
            "vx": math.cos(angle) * speed,
            "vy": math.sin(angle) * speed,
            "life": random.uniform(0.35, 0.75),
            "max_life": 0.75,
            "size": random.randint(3, 8),
            "color": random.choice(colors)
        })

def add_popup(x, y, text, color):
    popups.append({
        "x": float(x),
        "y": float(y),
        "text": text,
        "color": color,
        "life": 0.8
    })

def update_effects(dt):
    for p in particles[:]:
        p["x"] += p["vx"]
        p["y"] += p["vy"]
        p["vy"] += 12 * dt
        p["life"] -= dt

        if p["life"] <= 0:
            particles.remove(p)
            continue

        radius = max(1, int(p["size"] * p["life"] / p["max_life"]))
        pygame.draw.circle(
            screen, p["color"],
            (int(p["x"]), int(p["y"])), radius
        )

    for popup in popups[:]:
        popup["y"] -= 65 * dt
        popup["life"] -= dt

        if popup["life"] <= 0:
            popups.remove(popup)
            continue

        text_surface = font.render(
            popup["text"], True, popup["color"]
        )
        text_surface.set_alpha(
            max(0, min(255, int(255 * popup["life"] / 0.8)))
        )
        screen.blit(
            text_surface,
            (int(popup["x"]), int(popup["y"]))
        )

def draw_trail():
    if len(trail) < 2:
        return

    for i in range(1, len(trail)):
        ratio = i / len(trail)
        color = (
            100,
            int(160 + 95 * ratio),
            255
        )
        width = max(1, int(2 + 10 * ratio))

        pygame.draw.line(
            screen, color, trail[i - 1], trail[i], width
        )

    if trail:
        pygame.draw.circle(
            screen, WHITE, trail[-1], 5
        )

# ---------------- MAIN LOOP ----------------
running = True

try:
    while running:
        dt = min(clock.tick(60) / 1000.0, 0.04)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False

                if event.key == pygame.K_r and game_over:
                    fruits.clear()
                    particles.clear()
                    popups.clear()
                    trail.clear()
                    score = 0
                    start_time = time.time()
                    spawn_timer = 0
                    game_over = False
                    previous_finger = None

        # Webcam processing
        success, frame = camera.read()

        if not success:
            print("Cannot read webcam frame.")
            break

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (640, 480))
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)


        finger_position = None

        if results.multi_hand_landmarks:
            landmark = results.multi_hand_landmarks[0].landmark[8]
            finger_position = (
                int(landmark.x * WIDTH),
                int(landmark.y * HEIGHT)
            )

            camera_x = int(landmark.x * frame.shape[1])
            camera_y = int(landmark.y * frame.shape[0])

            cv2.circle(
                frame, (camera_x, camera_y), 10, (0, 255, 100), -1
            )

        preview = cv2.resize(frame, (320, 180))
        cv2.imshow("Hand Tracking Camera - Press Q to quit", preview)

        # Draw background
        draw_background()

        elapsed = time.time() - start_time
        remaining = max(0, int(game_duration - elapsed))

        if remaining <= 0:
            game_over = True

        # Update finger trail
        if finger_position and not game_over:
            if previous_finger:
                distance = math.dist(finger_position, previous_finger)

                # Fast finger movement produces a stronger slicing trail
                if distance > 4:
                    trail.append(finger_position)
            else:
                trail.append(finger_position)

            previous_finger = finger_position
        else:
            previous_finger = None

        trail = trail[-12:]

        # Spawn fruit
        if not game_over:
            spawn_timer += dt

            if spawn_timer >= 0.15:
                create_fruit()
                spawn_timer = 0

        # Move fruit and detect slicing
        for fruit in fruits[:]:
            if not game_over:
                fruit["x"] += fruit["speed_x"]
                fruit["y"] += fruit["speed_y"]
                fruit["speed_y"] += 0.12
                fruit["rotation"] += fruit["spin"]

            draw_fruit(fruit)

            if finger_position and not game_over:
                fx, fy = finger_position

                distance = math.hypot(
                    fx - fruit["x"], fy - fruit["y"]
                )

                if distance < fruit["radius"] + 17:
                    create_slice_effect(
                        fruit["x"], fruit["y"], fruit["bomb"]
                    )

                    if fruit["bomb"]:
                        score = max(0, score - 2)
                        add_popup(
                            fruit["x"], fruit["y"] - 20,
                            "-2", RED
                        )
                    else:
                        score += 1
                        add_popup(
                            fruit["x"], fruit["y"] - 20,
                            "+1", GOLD
                        )

                    fruits.remove(fruit)
                    continue

            if fruit["y"] > HEIGHT + 100:
                fruits.remove(fruit)

        # Slice trail and effects
        draw_trail()
        update_effects(dt)

        # Top HUD panels
        draw_panel((20, 16, 220, 65), border=GREEN)
        show_text(f"SCORE  {score}", 40, 32, GREEN)

        draw_panel((WIDTH - 225, 16, 205, 65), border=GOLD)
        timer_color = RED if remaining <= 8 else GOLD
        show_text(
            f"TIME  {remaining}s",
            WIDTH - 203, 32, timer_color
        )

        # Bottom instructions
        show_text(
            "MOVE YOUR INDEX FINGER TO SLICE!",
            245, HEIGHT - 42, WHITE, small_font
        )

        if finger_position:
            # Glowing fingertip indicator
            pygame.draw.circle(
                screen, (60, 255, 170),
                finger_position, 17, 2
            )
            pygame.draw.circle(
                screen, WHITE,
                finger_position, 4
            )

        # Game over overlay
        if game_over:
            overlay = pygame.Surface(
                (WIDTH, HEIGHT), pygame.SRCALPHA
            )
            overlay.fill((5, 5, 25, 205))
            screen.blit(overlay, (0, 0))

            draw_panel(
                (220, 205, 560, 300),
                color=(30, 24, 65),
                border=GOLD
            )

            show_text(
                "GAME OVER", 315, 245, GOLD, big_font
            )
            show_text(
                f"FINAL SCORE: {score}",
                335, 330, WHITE, font
            )
            show_text(
                "Press R to play again",
                340, 390, GREEN, font
            )
            show_text(
                "Press Q to quit",
                390, 435, WHITE, small_font
            )

        pygame.display.flip()

finally:
    camera.release()
    hands.close()
    cv2.destroyAllWindows()
    pygame.quit()
