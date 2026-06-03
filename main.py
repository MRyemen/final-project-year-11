#Authert: Dvir Zilber

import pygame
from player import Player
from network import Network
from fireball import Fireball

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
font = pygame.font.SysFont("Arial", 40, bold=True)
time_left = 5

# --- STRING NETWORK HELPERS ---
def parse_data(data):
    try:
        parts = data.split(",")
        #Added a 5th item to grab the connection count from the server
        return int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3]), int(parts[4])
    except:
        return 0, 0, 6, 0, 1


def make_data(x, y, health, action):
    return f"{x},{y},{health},{action}"


# --- NETWORK SETUP ---
n = Network()
client_id = int(n.get_player_id())

if client_id == 0:
    p1 = Player(100, 420, (255, 0, 0), 1)
    p2 = Player(650, 420, (0, 0, 255), 2)
else:
    p1 = Player(650, 420, (0, 0, 255), 2)
    p2 = Player(100, 420, (255, 0, 0), 1)

my_fireballs = []
enemy_fireballs = []

#Game State Variables
game_state = "WAITING"
countdown_start = 0


def draw_hud():
    # Figure out P1's color and text based on their ID
    if p1.id == 1:
        p1_text = f"RED HP: {p1.health}"
        p1_color = (255, 0, 0)  # Red text
    else:
        p1_text = f"BLUE HP: {p1.health}"
        p1_color = (0, 0, 255)  # Blue text

    # Figure out P2's color and text based on their ID
    if p2.id == 1:
        p2_text = f"RED HP: {p2.health}"
        p2_color = (255, 0, 0)  # Red text
    else:
        p2_text = f"BLUE HP: {p2.health}"
        p2_color = (0, 0, 255)  # Blue text

    # Render the new strings with their matching colors
    p1_score = font.render(p1_text, False , p1_color)
    p2_score = font.render(p2_text, False , p2_color)

    # Draw them to the screen
    screen.blit(p1_score, (20, 20))
    screen.blit(p2_score, (WIDTH - p2_score.get_width() - 20, 20))


def draw_background():
    sky_blue = (135, 206, 235)
    screen.fill(sky_blue)
    white = (255, 255, 255)
    pygame.draw.circle(screen, white, (150, 100), 40)
    pygame.draw.circle(screen, white, (190, 90), 50)
    pygame.draw.circle(screen, white, (230, 100), 40)
    pygame.draw.circle(screen, white, (190, 120), 30)
    pygame.draw.circle(screen, white, (600, 150), 40)
    pygame.draw.circle(screen, white, (640, 140), 50)
    pygame.draw.circle(screen, white, (680, 150), 40)
    pygame.draw.circle(screen, white, (640, 170), 30)
    gray = (100, 100, 100)
    pygame.draw.rect(screen, gray, (0, 500, 800, 100))


def draw_cooldown_bar(p):
    current_time1 = pygame.time.get_ticks()
    time_since_shot = current_time1 - p.last_shot_time

    # Calculate how full the bar should be (0.0 to 1.0)
    ratio = min(time_since_shot / p.cooldown, 1.0)

    bar_width = p.rect.width
    bar_height = 5
    x = p.rect.x
    y = p.rect.y - 15  # Hover 15 pixels above the player's head

    # Draw gray background (empty bar)
    pygame.draw.rect(screen, (100, 100, 100), (x, y, bar_width, bar_height))

    # Draw colored fill (Orange = Charging, Green = Ready)
    fill_width = int(bar_width * ratio)
    color = (0, 255, 0) if ratio == 1.0 else (255, 165, 0)

    if fill_width > 0:
        pygame.draw.rect(screen, color, (x, y, fill_width, bar_height))



# Game Loop
running = True
clock = pygame.time.Clock()
try:
    while running:
        draw_background()
        current_action = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if game_state == "PLAYING":
                        # NEW: Check if 1.5 seconds have passed
                        current_time = pygame.time.get_ticks()
                        if current_time - p1.last_shot_time >= p1.cooldown:
                            current_action = p1.facing
                            my_fireballs.append(Fireball(p1.rect.centerx, p1.rect.centery, p1.facing))
                            p1.last_shot_time = current_time  # Reset our stopwatch

        # Only let the player move left/right if the game is PLAYING
        if game_state == "PLAYING":
            p1.handle_input()
        else:
            p1.vel_x = 0  # Force them to stand still during countdown

        p1.update()

        # --- NETWORK SYNC ---
        my_data_string = make_data(p1.rect.x, p1.rect.y, p1.health, current_action)
        enemy_data_string = n.send(my_data_string)


        # Unpack the new 5-item list
        enemy_x, enemy_y, enemy_health, enemy_action, total_players = parse_data(enemy_data_string)
        p2.rect.x = enemy_x
        p2.rect.y = enemy_y
        p2.health = enemy_health
        #Since action is now the direction (-1 or 1), we just pass it directly to the fireball!
        if enemy_action != 0:
            enemy_fireballs.append(Fireball(enemy_x + 20, enemy_y + 40, enemy_action))
            p2.last_shot_time = pygame.time.get_ticks()

        # --- THE STATE MACHINE (Timer & Game Over) ---
        if game_state == "WAITING":
            if total_players >= 2:
                game_state = "COUNTDOWN"
                countdown_start = pygame.time.get_ticks()  # Start the clock

        elif game_state == "COUNTDOWN":
            now = pygame.time.get_ticks()
            time_left = 3 - ((now - countdown_start) // 1000)
            if time_left <= 0:
                game_state = "PLAYING"

        elif game_state == "PLAYING":
            if p1.health <= 0 or p2.health <= 0:
                game_state = "GAMEOVER"

        # --- FIREBALL UPDATES ---
        for fb in my_fireballs[:]:
            fb.update()
            fb.draw(screen)

            if fb.x > 1000 or fb.x < -200:
                my_fireballs.remove(fb)
            elif p2.rect.colliderect(fb.rect):
                my_fireballs.remove(fb)

        for fb in enemy_fireballs[:]:
            fb.update()
            fb.draw(screen)

            # Clean up enemy fireballs that miss and go off-screen
            if fb.x > 1000 or fb.x < -200:
                enemy_fireballs.remove(fb)
            elif p1.rect.colliderect(fb.rect):
                p1.health -= 1
                enemy_fireballs.remove(fb)

        # --- DRAW EVERYTHING ---
        screen.blit(p1.image, p1.rect)
        screen.blit(p2.image, p2.rect)


        draw_cooldown_bar(p1)
        draw_cooldown_bar(p2)
        draw_hud()

        # Draw text overlays depending on the game state
        if game_state == "WAITING":
            text = font.render("Waiting for Player 2...", False, (0, 0, 0))
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2))

        elif game_state == "COUNTDOWN":
            text = font.render(f"Starting in {time_left}...", False, (0, 0, 0))
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2))


        elif game_state == "GAMEOVER":
            # 1. Figure out which player ID actually died
            if p1.health <= 0:
                dead_id = p1.id
            else:
                dead_id = p2.id
            # 2. ID 1 is Red, ID 2 is Blue. If Red died, Blue wins
            if dead_id == 1:
                screen.fill((0, 0, 255))  # Blue Won!
                win_text = font.render("BLUE WINS!", True, (255, 255, 255))
            else:
                screen.fill((255, 0, 0))  # Red Won
                win_text = font.render("RED WINS!", True, (255, 255, 255))
            screen.blit(win_text, (WIDTH // 2 - win_text.get_width() // 2, HEIGHT // 2))

        pygame.display.flip()
        clock.tick(60)
except KeyboardInterrupt:
    pass

pygame.quit()