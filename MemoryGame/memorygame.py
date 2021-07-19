import pygame
import os
import math
from random import *

# Setup game for level "level"
def setup(level):
    global display_time
    display_time = 5 - (level // 3)
    display_time = max(display_time, 1)

    number_count = (level // 3 ) + 5
    number_count = min(number_count, 20)

    shuffle_grid(number_count)

# Randomly shuffle the grid with numbers from 1 to "number_count"
def shuffle_grid(number_count):
    rows = 5
    columns = 9

    cell_size = 130
    button_size = 110
    screen_left_margin = 55
    screen_top_margin = 20


    grid = [[0 for col in range(columns)] for row in range(rows)]
    number = 1
    while number <= number_count:
        row_idx = randrange(0, rows)
        col_idx = randrange(0, columns)

        if grid[row_idx][col_idx] == 0:
            grid[row_idx][col_idx] = number
            number+=1

            center_x = screen_left_margin + (col_idx * cell_size) + (cell_size/2)
            center_y = screen_top_margin + (row_idx * cell_size) + (cell_size/2)

            button = pygame.Rect(0,0, button_size, button_size)
            button.center = (center_x, center_y)

            number_buttons.append(button)

# Start screen
def display_start_screen():
    pygame.draw.circle(screen, WHITE, start_button.center, 60, 5)

    start_msg = start_font.render(f"START", True, WHITE)
    msg_rect = start_msg.get_rect(center=start_button.center)
    screen.blit(start_msg, msg_rect)

    level_msg = game_font.render(f"Next level is {level}", True, WHITE)
    msg_rect = level_msg.get_rect(center=(screen_width/2, screen_height/2))
    screen.blit(level_msg, msg_rect)

# Game Screen
def display_game_screen():
    global hidden
    elapsed_time = (pygame.time.get_ticks() - start_ticks) / 1000
    if elapsed_time > display_time:
        hidden = True

    for idx, rect in enumerate (number_buttons, start=1):
        if hidden:
            pygame.draw.rect(screen, WHITE, rect)

        else:
            pygame.draw.rect(screen, GRAY, rect)
            cell_text = game_font.render(str(idx), True, WHITE)
            text_rect = cell_text.get_rect(center = rect.center)
            screen.blit(cell_text, text_rect)
        
# Check if buttons are clicked from "pos" mouse click inputs
def check_buttons(pos):
    global start, start_ticks, level, hidden
    # check in game screen
    if start:
        check_number_buttons(pos)
        if len(number_buttons) == 0:
            start = False
            hidden = False
            level += 1
            setup(level)

    # check in start screen
    elif start_button.collidepoint(pos):
        # check if its clicked in the circle and not the rect
        x1 ,y1 = pos
        x2, y2 = start_button.center
        distance = math.hypot(x1 - x2, y1 - y2)
        if distance <= 60:
            start_ticks = pygame.time.get_ticks()
            start = True

# verify if correct button is clicked in order
def check_number_buttons(pos):
    if hidden == True:
        for button in number_buttons:
            if button.collidepoint(pos):
                if button == number_buttons[0]:
                    del number_buttons[0]
                else:
                    game_over()
                break

# displays game over message
def game_over():
    global running
    msg = game_font.render(f"Your memory level is {level}!", True, WHITE)
    msg_rect = msg.get_rect(center=(screen_width/2, screen_height/2))
    screen.fill(BLACK)
    screen.blit(msg, msg_rect)
    running = False

##################################################################################
## Pygame basic initializations

pygame.init() 
pygame.font.init()

# Screen size settings
screen_width = 1280
screen_height = 720
screen  = pygame.display.set_mode((screen_width,screen_height))

# Screen title
pygame.display.set_caption("Memory Game")
current_path = os.path.dirname(__file__)

# Fonts
game_font = pygame.font.Font(os.path.join(current_path, "freesansbold.ttf"), 80)
start_font = pygame.font.Font(os.path.join(current_path, "freesansbold.ttf"), 30)

# FPS setting
clock = pygame.time.Clock()

## Variables

# Colors
WHITE = (255,255,255)
BLACK = (0,0,0)
GRAY = (50,50,50)

# Start button
start_button = pygame.Rect(0,0, 120, 120)
start_button.center = (120, screen_height - 120)

# Game state variables
start = False
hidden = False
display_time = None
start_ticks = None
level = 1
number_buttons = []

## Start game loop

setup(level)

running = True
while running:
    click_pos = None

    for event in pygame.event.get():
        if event.type == pygame.QUIT: 
            running = False
        elif event.type == pygame.MOUSEBUTTONUP:
            click_pos = pygame.mouse.get_pos()

    # drawing
    screen.fill(BLACK)
    if start:
        display_game_screen()
    else:
        display_start_screen()

    if click_pos:
        check_buttons(click_pos)

    # update screen 
    pygame.display.update()   


## Quit pygame
pygame.time.delay(5000)
pygame.quit()