'''import pygame
import random

def get_lanes_for_level(level, lane_x_positions_all):
    if level == 2:
        return lane_x_positions_all[:3]  # Reduce to 3 lanes
    return lane_x_positions_all

class Opponent(pygame.sprite.Sprite):
    def __init__(self, lane_x_positions, lane_y_positions, speed_multiplier):
        super().__init__()
        self.image = pygame.transform.scale(pygame.image.load(random.choice(['truck.png', 'police.png', 'car.png'])), (80, 130))
        self.rect = self.image.get_rect()

        available_lanes = [(x, y) for x, y in zip(lane_x_positions, lane_y_positions) if y is None or y < -200]
        if available_lanes:
            self.rect.x, lane_y_positions[lane_x_positions.index(self.rect.x)] = random.choice(available_lanes)
        else:
            self.rect.x = random.choice(lane_x_positions)
            lane_y_positions[lane_x_positions.index(self.rect.x)] = -200

        self.rect.y = random.randint(-150, -60)
        self.speed = random.randint(2, 5) * speed_multiplier

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > 800:
            lane_y_positions[lane_x_positions.index(self.rect.x)] = None
            self.kill()
'''
import pygame

def draw_background(screen):
    LIGHT_LAND_ORANGE = (255, 179, 102)
    screen.fill(LIGHT_LAND_ORANGE)

    lane_color = (255, 255, 255)  # White lanes
    lane_width = 10
    lane_height = 40

    green_width = (screen.get_width() - 3 * 150) // 2  # Adjust green area width for level 2
    for i in range(1, 3):
        pygame.draw.rect(screen, (0, 0, 0), (green_width + i * 150, 0, lane_width, screen.get_height()))
        for j in range(0, screen.get_height(), lane_height * 2):
            pygame.draw.rect(screen, lane_color, (green_width + i * 150, j, lane_width, lane_height))
