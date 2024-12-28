
import pygame
import random
import sqlite3
import level2
import level3
import pygame.mixer 

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Database setup
def setup_database():
    conn = sqlite3.connect('highscore.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS highscores (
        id INTEGER PRIMARY KEY,
        player_name TEXT NOT NULL,
        score INTEGER NOT NULL,
        date TEXT DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    conn.commit()
    conn.close()

def add_highscore(player_name, score):
    conn = sqlite3.connect('highscore1.db')
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO highscores (player_name, score)
    VALUES (?, ?)
    ''', (player_name, score))
    conn.commit()
    conn.close()

def get_top_highscores(limit=250):
    conn = sqlite3.connect('highscore1.db')
    cursor = conn.cursor()
    cursor.execute('''
    SELECT player_name, score, date
    FROM highscores
    ORDER BY score DESC
    LIMIT ?
    ''', (limit,))
    top_scores = cursor.fetchall()
    conn.close()
    return top_scores


def check_username_exists(username):
    conn = sqlite3.connect('highscore1.db')
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM highscores WHERE player_name = ?', (username,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

setup_database()

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
INITIAL_LANE_WIDTH = 120
GREEN_WIDTH_LEVEL_1 = (SCREEN_WIDTH - 5 * INITIAL_LANE_WIDTH) // 2  # Updated for 5 lanes

# Colors
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
LIGHT_LAND_ORANGE = (255, 179, 102)
LIGHT_OCEAN_BLUE = (102, 178, 255)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# Load and scale images
player_car = pygame.image.load('assets/Black_viper.png')
player_car = pygame.transform.scale(player_car, (100, 120))

opponent_images = ['assets/truck.png', 'assets/police.png', 'assets/car.png', 'assets/ambulance.png', 'assets/taxi.png', 'assets/mini_truck.png']
opponent_sprites = [pygame.transform.scale(pygame.image.load(img), (100, 120)) for img in opponent_images]


# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Car Shooting Game')

# Clock
clock = pygame.time.Clock()

# Load background images
green_image = pygame.image.load('assets/lvl1(2).webp')
green_image = pygame.transform.scale(green_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

orange_image = pygame.image.load('assets/lvl2(2).webp')
orange_image = pygame.transform.scale(orange_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

blue_image = pygame.image.load('assets/lvl3(2).webp')
blue_image = pygame.transform.scale(blue_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Font for score and text input
font = pygame.font.SysFont(None, 36)

# Load sounds
background_music = pygame.mixer.music.load('assets/bg.mp3')
collision_sound = pygame.mixer.Sound('assets/crash.wav')
pygame.mixer.music.play(-1)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_car
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 10
        self.speed = 5

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        if keys[pygame.K_UP]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN]:
            self.rect.y += self.speed

        green_width = get_green_width(level)
        if self.rect.left < green_width:
            self.rect.left = green_width
        if self.rect.right > SCREEN_WIDTH - green_width:
            self.rect.right = SCREEN_WIDTH - green_width

    def shoot(self):
        laser = Laser(self.rect.centerx, self.rect.top)
        all_sprites.add(laser)
        lasers.add(laser)

class Laser(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 20))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = 10

    def update(self):
        self.rect.y -= self.speed
        if self.rect.bottom < 0:
            self.kill()

class Opponent(pygame.sprite.Sprite):
    BASE_SPEED = 5  # Set a base speed for all opponents

    def __init__(self, lane_x_positions, speed_multiplier):
        super().__init__()
        self.image = random.choice(opponent_sprites)
        self.rect = self.image.get_rect()
        
        green_width = get_green_width(level)
        black_track_width = get_black_track_width(level)
        lane_width = black_track_width // len(lane_x_positions)
        
        lane_index = random.randint(0, len(lane_x_positions) - 1)
        self.rect.x = green_width + lane_index * lane_width + (lane_width - self.rect.width) // 2
        
        self.rect.y = random.randint(-150, -60)
        self.speed = self.BASE_SPEED * speed_multiplier  # Use the base speed multiplied by the speed multiplier

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()
        
        # Check for collisions with other opponents
        collided = pygame.sprite.spritecollide(self, opponents, False)
        if len(collided) > 1:  # If collided with more than itself
            for other in collided:
                if other != self and other.rect.centery < self.rect.centery:
                    # If the other car is above this one, slow down
                    self.rect.y = other.rect.bottom + 5
def get_lanes_for_level(level, lane_x_positions_all):
    if level == 3:
        return lane_x_positions_all[:2]
    elif level == 2:
        return lane_x_positions_all[:3]
    return lane_x_positions_all

def check_level_transition():
    global level, current_level_module, lane_x_positions, speed_multiplier
    if score > 450 and level < 3:
        level = 3
        current_level_module = level_modules[level]
        lane_x_positions = get_lanes_for_level(level, lane_x_positions_all)
        speed_multiplier += 0.5
        return True
    elif score > 250 and level < 2:
        level = 2
        current_level_module = level_modules[level]
        lane_x_positions = get_lanes_for_level(level, lane_x_positions_all)
        speed_multiplier += 0.5
        return True
    return False

def display_highscores():
    top_scores = get_top_highscores()

    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                    done = True

        screen.fill(BLACK)

        title_surface = font.render("High Scores", True, pygame.Color('red'))
        screen.blit(title_surface, (SCREEN_WIDTH // 2 - title_surface.get_width() // 2, 50))

        # Create a table-like structure
        headers = ["Rank", "Player", "Score", "Date"]
        col_widths = [80, 200, 100, 200]
        y_offset = 100

        # Draw headers
        x_offset = 50
        for header, width in zip(headers, col_widths):
            header_surface = font.render(header, True, pygame.Color('yellow'))
            screen.blit(header_surface, (x_offset, y_offset))
            x_offset += width

        y_offset += 40

        # Draw scores
        for i, (player_name, score, date) in enumerate(top_scores):
            x_offset = 50
            row_data = [str(i + 1), player_name, str(score), date]
            for data, width in zip(row_data, col_widths):
                data_surface = font.render(data, True, pygame.Color('red'))
                screen.blit(data_surface, (x_offset, y_offset))
                x_offset += width
            y_offset += 30

        instructions = font.render("Press ENTER or ESC to return", True, pygame.Color('white'))
        screen.blit(instructions, (SCREEN_WIDTH // 2 - instructions.get_width() // 2, SCREEN_HEIGHT - 50))

        pygame.display.flip()
def check_username_score(username):
    conn = sqlite3.connect('highscore.db')
    cursor = conn.cursor()
    cursor.execute('SELECT MAX(score) FROM highscores WHERE player_name = ?', (username,))
    result = cursor.fetchone()
    conn.close()
    if result[0] is not None and result[0] > 250:
        return True
    return False

def update_highscore(username, new_score):
    conn = sqlite3.connect('highscore1.db')
    cursor = conn.cursor()
    cursor.execute('SELECT score FROM highscores WHERE player_name = ?', (username,))
    result = cursor.fetchone()
    
    if result is None:
        # If the username doesn't exist, insert a new record
        cursor.execute('INSERT INTO highscores (player_name, score) VALUES (?, ?)', (username, new_score))
    else:
        current_score = result[0]
        if new_score > current_score:
            # If the new score is higher, update the record
            cursor.execute('UPDATE highscores SET score = ? WHERE player_name = ?', (new_score, username))
    
    conn.commit()
    conn.close()

def cleanup_duplicate_usernames():
    conn = sqlite3.connect('highscore.db')
    cursor = conn.cursor()
    
    # Find duplicates and keep the one with the highest score
    cursor.execute('''
    DELETE FROM highscores
    WHERE id NOT IN (
        SELECT MAX(id)
        FROM highscores
        GROUP BY player_name
        HAVING MAX(score)
    )
    ''')
    
    conn.commit()
    conn.close()
def display_popup(screen, message):
    popup_width, popup_height = 650, 150  # Increased size
    popup_x = (SCREEN_WIDTH - popup_width) // 2
    popup_y = (SCREEN_HEIGHT - popup_height) // 2
    
    # Draw popup background
    popup_surface = pygame.Surface((popup_width, popup_height))
    popup_surface.fill(BLACK)
    pygame.draw.rect(popup_surface, WHITE, popup_surface.get_rect(), 2)
    
    # Render message
    font = pygame.font.SysFont(None, 36)  # Increased font size
    text_surface = font.render(message, True, WHITE)
    text_rect = text_surface.get_rect(center=(popup_width // 2, popup_height // 2))
    
    # Blit text onto popup surface
    popup_surface.blit(text_surface, text_rect)
    
    # Blit popup onto main screen
    screen.blit(popup_surface, (popup_x, popup_y))
    
    # Update display
    pygame.display.flip()
    
    # Wait for user input
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False
def get_player_name():
    input_box = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 20, 200, 40)
    color_inactive = pygame.Color('black')
    color_outline = pygame.Color('red')
    color_text = pygame.Color('red')
    active = False
    text = ''
    done = False

    background_image = pygame.image.load('cover11.webp')
    background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

    high_scores_text = font.render("See High Scores", True, pygame.Color('red'))
    high_scores_text_width, high_scores_text_height = high_scores_text.get_size()

    margin_right = 20
    margin_bottom = 20

    high_scores_button = pygame.Rect(
        SCREEN_WIDTH - high_scores_text_width - margin_right,
        SCREEN_HEIGHT - high_scores_text_height - margin_bottom,
        high_scores_text_width + 20,
        high_scores_text_height + 10
    )

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                
                if high_scores_button.collidepoint(event.pos):
                    display_highscores()

            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    elif event.key == pygame.K_RETURN:
                        if check_username_exists(text):
                            display_popup(screen,"Username already exists.Your score will be updated.")
                        done = True
                    else:
                        text += event.unicode

        screen.blit(background_image, (0, 0))

        txt_surface = font.render(text, True, color_text)
        width = max(200, txt_surface.get_width() + 10)
        input_box.w = width

        pygame.draw.rect(screen, color_outline, input_box.inflate(6, 6))
        pygame.draw.rect(screen, color_inactive, input_box)

        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))

        pygame.draw.rect(screen, pygame.Color('black'), high_scores_button)

        text_rect = high_scores_text.get_rect(center=high_scores_button.center)
        screen.blit(high_scores_text, text_rect.topleft)

        pygame.display.flip()

    return text

def get_black_track_width(level):
    if level == 3:
        return INITIAL_LANE_WIDTH * 2
    elif level == 2:
        return INITIAL_LANE_WIDTH * 3
    return INITIAL_LANE_WIDTH * 5  # Updated for 5 lanes in level 1


def get_green_width(level):
    return (SCREEN_WIDTH - get_black_track_width(level)) // 2

def draw_road_lines(level):
    green_width = get_green_width(level)
    black_track_width = get_black_track_width(level)
    
    if level == 1:
        screen.blit(green_image, (0, 0))
    elif level == 2:
        screen.blit(orange_image, (0, 0))
    else:
        screen.blit(blue_image, (0, 0))

    pygame.draw.rect(screen, BLACK, (green_width, 0, black_track_width, SCREEN_HEIGHT))

    pygame.draw.line(screen, YELLOW, (green_width, 0), (green_width, SCREEN_HEIGHT), 4)
    pygame.draw.line(screen, YELLOW, (SCREEN_WIDTH - green_width, 0), (SCREEN_WIDTH - green_width, SCREEN_HEIGHT), 4)

    lane_line_color = WHITE

    if level == 3:
        pygame.draw.line(screen, lane_line_color, 
                         (green_width + black_track_width // 2, 0), 
                         (green_width + black_track_width // 2, SCREEN_HEIGHT), 2)
    elif level == 2:
        for lane in range(1, 3):  # Draw 2 lines for 3 lanes
            pygame.draw.line(screen, lane_line_color, 
                             (green_width + lane * INITIAL_LANE_WIDTH, 0), 
                             (green_width + lane * INITIAL_LANE_WIDTH, SCREEN_HEIGHT), 2)
    else:  # Level 1
        for lane in range(1, 5):  # Draw 4 lines for 5 lanes
            pygame.draw.line(screen, lane_line_color, 
                             (green_width + lane * INITIAL_LANE_WIDTH, 0), 
                             (green_width + lane * INITIAL_LANE_WIDTH, SCREEN_HEIGHT), 2)
            
player = Player()
all_sprites = pygame.sprite.Group()
all_sprites.add(player)
opponents = pygame.sprite.Group()
lasers = pygame.sprite.Group()

score = 0
level = 1
level_modules = {1: None, 2: level2, 3: level3}
current_level_module = None
lane_x_positions_all = [get_green_width(1) + i * INITIAL_LANE_WIDTH for i in range(5)]  # Updated for 5 lanes
lane_x_positions = get_lanes_for_level(level, lane_x_positions_all)
speed_multiplier = 1

def reset_game():
    global score, level, player, all_sprites, opponents, lasers, lane_x_positions, speed_multiplier

    score = 0
    level = 1
    speed_multiplier = 1

    player = Player()
    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)
    opponents = pygame.sprite.Group()
    lasers = pygame.sprite.Group()

    lane_x_positions = get_lanes_for_level(level, lane_x_positions_all)

    game_loop()

# ... [previous code remains unchanged] ...

def play_again_prompt():
    screen.fill(BLACK)
    prompt_font = pygame.font.SysFont(None, 48)
    prompt_text = prompt_font.render("Oops, better luck next time! Press SPACE to restart or ESC to exit", True, WHITE)
    screen.blit(prompt_text, (SCREEN_WIDTH // 2 - prompt_text.get_width() // 2, SCREEN_HEIGHT // 2 - prompt_text.get_height() // 2))
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    reset_game()
                    return
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()

def spawn_opponent():
    new_opponent = Opponent(lane_x_positions, speed_multiplier)
    
    # Check for collision with existing opponents
    collision = pygame.sprite.spritecollideany(new_opponent, opponents)
    if not collision:
        all_sprites.add(new_opponent)
        opponents.add(new_opponent)
    else:
        # If there's a collision, try to adjust the y position
        attempts = 0
        while attempts < 10:  # Try up to 10 times
            new_opponent.rect.y -= 150  # Move it up by 150 pixels (increased to reduce chances of immediate collision)
            collision = pygame.sprite.spritecollideany(new_opponent, opponents)
            if not collision:
                all_sprites.add(new_opponent)
                opponents.add(new_opponent)
                break
            attempts += 1
        
        if attempts == 10:
            # If we couldn't find a spot after 10 attempts, don't spawn the opponent
            del new_opponent

def game_loop():
    global score
    running = True
    add_opponent_event = pygame.USEREVENT + 1
    pygame.time.set_timer(add_opponent_event, 1000)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == add_opponent_event:
                spawn_opponent()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.shoot()

        all_sprites.update()
        draw_road_lines(level)

        hits = pygame.sprite.groupcollide(opponents, lasers, True, True)
        for hit in hits:
            score += 10

        if pygame.sprite.spritecollideany(player, opponents):
            collision_sound.play()
            update_highscore(player_name, score)  # Use update_highscore instead of add_highscore
            play_again_prompt()
            running = False

        all_sprites.draw(screen)

        score_text = font.render(f'Score: {score}', True, WHITE)
        screen.blit(score_text, (10, 10))

        check_level_transition()

        pygame.display.flip()
        clock.tick(60)
 
# Start game
cleanup_duplicate_usernames() 
player_name = get_player_name()
game_loop()

pygame.quit()