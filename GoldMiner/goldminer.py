import pygame
import os
import math
import random

# Claw sprite class
class Claw(pygame.sprite.Sprite):
    def __init__(self, image, position):
        super().__init__()
        self.image = image
        self.original_image = image
        self.rect = image.get_rect(center = position)

        self.offset = pygame.math.Vector2(default_offset_x_claw, 0)
        self.position = position

        self.direction = LEFT
        self.angle_speed = 2.5/30
        self.angle = 10

        self.prev_direction = self.direction
        self.prev_angle = self.angle

    # update claw state
    def update(self, to_x, fps = 60):
        if self.direction == LEFT:
            self.angle += self.angle_speed * fps
        elif self.direction == RIGHT:
            self.angle -= self.angle_speed * fps
        
        if self.angle > 170:
            self.angle = 170
            self.set_direction(RIGHT)
        elif self.angle < 10:
            self.angle = 10
            self.set_direction(LEFT)

        self.offset.x += to_x * fps
        self.rotate()
    
    # perform rotation of claw
    def rotate(self):
        self.image = pygame.transform.rotozoom(self.original_image, -self.angle, 1)
        offset_rotated = self.offset.rotate(self.angle)
        self.rect = self.image.get_rect(center = self.position + offset_rotated)

    def set_direction(self, direction):
        self.direction = direction

    def set_init_state(self):
        self.offset.x = default_offset_x_claw
        self.angle = 10
        self.set_direction(LEFT)
    
    def set_prev_state(self):
        self.offset.x = default_offset_x_claw
        self.angle = self.prev_angle
        self.set_direction(self.prev_direction)

    def save_curr_state(self):
        self.prev_direction = self.direction
        self.prev_angle = self.angle
        claw.set_direction(STOP)

    def draw(self, screen):
        pygame.draw.line(screen, BLACK, self.position, self.rect.center , 5)
        screen.blit(self.image, self.rect)
        
# Gemstone sprite class
class Gemstone(pygame.sprite.Sprite):
    def __init__(self, image, position, weight_speed, price):
        super().__init__()
        self.image = image
        self.rect = image.get_rect(center = position)
        self.weight_speed = weight_speed
        self.price = price
        self.position = position
    
    def set_position(self, position, angle):
        r = self.rect.size[0] // 2
        rad_angle = math.radians(angle)
        to_x = r * math.cos(rad_angle)
        to_y = r * math.sin(rad_angle)
        self.rect.center = (position[0] + to_x, position[1] + to_y)

# Randomly create gemstone; random type & position
def create_random_gemstone():
    gem_type = ""
    while not gem_type:
        rand = random.randint(1, 100)
        if rand in range(1,30):
            gem_type = "stone"
        elif rand in range(31, 70):
            gem_type = "small_gold"
        elif rand in range(71, 94):
            gem_type = "big_gold"
        elif rand in range(91, 100):
            gem_type = "diamond"
    create_gemstone(gem_type)

# Randomly select position that doesn't overlap with exisiting gemstones
# returns None if unable to find a valid location 
def get_new_rand_positon(gem_type):
    size = gems[gem_type]["image"].get_rect().size
    existing_postions = [] 

    # get all the position information for exisiing positions
    for gemstone in gemstone_group:
        position = gemstone.position
        gem_size = gemstone.rect.size

        starting_pos = (position[0] - int(gem_size[0]/2), position[1] - int(gem_size[1]/2))
        ending_pos = (position[0] + int(gem_size[0]/2), position[1] + int(gem_size[1]/2))

        existing_postions.append((starting_pos, ending_pos))

    # randomly select x and y pos and then check against exisiting gemstone postions
    attempted_positions = []
    for i in range(100):
        overlap = False
        x_pos = random.randint(0, screen_width - int(size[0]/2))
        x_dist = abs(screen_width/2 - x_pos)
        min_y_pos = max( 162 + int(size[1]/2)  ,int(x_dist * math.tan(10)))
        y_pos = random.randint(min_y_pos, screen_height - int(size[1]/2))
        
        new_starting_pos = (x_pos - int(size[0]/2), y_pos - int(size[1]/2))
        new_ending_pos = (x_pos + int(size[0]/2), y_pos + int(size[1]/2))

        for existing in existing_postions:
            # check it new gem overlaps both the axis of existing
            if existing[0][0] >= new_starting_pos[0]  and existing[0][0] <= new_ending_pos[0]:
                if (existing[0][1] >= new_starting_pos[1]  and existing[0][1] <= new_ending_pos[1]) or (existing[1][1] >= new_starting_pos[1]  and existing[1][1] <= new_ending_pos[1]):
                    overlap = True
                    break
            if existing[1][0] >= new_starting_pos[0]  and existing[1][0] <= new_ending_pos[0]:
                if (existing[0][1] >= new_starting_pos[1]  and existing[0][1] <= new_ending_pos[1]) or (existing[1][1] >= new_starting_pos[1]  and existing[1][1] <= new_ending_pos[1]):
                    overlap = True
                    break

            # check if new gem is inside the exisiting or only 1 axis is overlapping
            if existing[0][0] <= new_starting_pos[0] and existing[1][0] >= new_ending_pos[0]:
                if existing[0][1] <= new_starting_pos[1] and existing[1][1] >= new_ending_pos[1]:
                    overlap = True
                    break
                elif (existing[0][1] >= new_starting_pos[1]  and existing[0][1] <= new_ending_pos[1]) or (existing[1][1] >= new_starting_pos[1]  and existing[1][1] <= new_ending_pos[1]):
                    overlap = True
                    break
            if existing[0][1] <= new_starting_pos[1] and existing[1][1] >= new_ending_pos[1]:
                if (existing[0][0] >= new_starting_pos[0]  and existing[0][0] <= new_ending_pos[0]) or (existing[1][0] >= new_starting_pos[0]  and existing[1][0] <= new_ending_pos[0]):
                    overlap = True
                    break

        if not overlap:
            return (x_pos, y_pos)
        else:
            attempted_positions.append((x_pos, y_pos))
    
    print("Failed to find pos")

# Creates gemstone class object of "gem_type"
def create_gemstone(gem_type):
    global gemstone_group
    gem_position = get_new_rand_positon(gem_type)
    if gem_position:
        gem = Gemstone(gems[gem_type]["image"], gem_position, gems[gem_type]["weight_speed"], gems[gem_type]["price"])
        gemstone_group.add(gem)

# Setup gemstones for the start of the game
def setup_gemstone():
    for i in range(7):
        create_random_gemstone()

# Update current score with the gemstone price
def update_score(score):
    global current_score
    current_score += score

    if current_score >= goal_score:
        update_goal_score(goal_score)

# Update goal score and increase level of the game every 1500 points
def update_goal_score(goal):
    global goal_score, total_time, level, game_result
    goal_score += 1500
    total_time += 30
    if level < 10:
        level += 1
    else:
        game_result = "Mission Complete"
        display_game_over()

def display_score():
    txt_curr_score = game_font.render(f"Curr Score : {current_score:,}", True, BLACK)
    screen.blit(txt_curr_score, (50,20))

    txt_goal_score = game_font.render(f"Goal Score : {goal_score:,}", True, BLACK)
    screen.blit(txt_goal_score, (50,80))

def display_time(time):
    txt_timer = game_font.render(f"Time : {time}", True, BLACK)
    screen.blit(txt_timer, (1000, 80))

def display_level(level):
    txt_level = game_font.render(f"Level {level}", True, BLACK)
    txt_size = txt_level.get_rect().size
    screen.blit(txt_level, (1000, 20))

def display_game_over():
    game_font = pygame.font.SysFont("arialblack", 60)
    msg = game_font.render(f"{game_result}", True, BLACK)
    msg_rect = msg.get_rect(center=(screen_width/2, screen_height/2))
    screen.blit(msg, msg_rect)

##################################################################################
## Pygame basic initializations

pygame.init() 

# Screen size & title settings
screen_width = 1280
screen_height = 720
screen  = pygame.display.set_mode((screen_width,screen_height))
pygame.display.set_caption("Gold Miner")

# Fonts
game_font = pygame.font.SysFont("arialblack", 30)

# FPS setting
clock = pygame.time.Clock()

## Variables

# Claw direction
LEFT = -1
RIGHT = 1
STOP = 0 

# Colors
RED = (255,0,0)
BLACK = (0,0,0)

# Movement variables
default_offset_x_claw = 40
to_x_claw = 0
move_speed = 12/30
return_speed = 20/30

# Game state variables
level = 1
caught_gemstone = None
current_score = 0
goal_score = 1500

# Time variables
total_time = 90
start_ticks = pygame.time.get_ticks()
create_new_elapsed_time = {}

# Game result variables
game_result = None

# Path info
current_path = os.path.dirname(__file__)
image_path = os.path.join(current_path, "images")

# Background variables
background = pygame.image.load(os.path.join(image_path, "background.png"))

# Gemstone class variables
gemstone_group = pygame.sprite.Group()

small_gold = {
   "image" :  pygame.image.load(os.path.join(image_path, "small_gold.png")).convert_alpha(),
   "weight_speed" : 5/30,
   "price" : 100
}
big_gold = {
   "image" :  pygame.image.load(os.path.join(image_path, "big_gold.png")).convert_alpha(),
   "weight_speed" : 3/30,
   "price" : 500
}
stone = {
   "image" :  pygame.image.load(os.path.join(image_path, "stone.png")).convert_alpha(),
   "weight_speed" : 4/30,
   "price" : 10
}
diamond = {
   "image" :  pygame.image.load(os.path.join(image_path, "diamond.png")).convert_alpha(),
   "weight_speed" : 7/30,
   "price" : 700
}
gems = {"small_gold":small_gold, "big_gold":big_gold, "stone": stone, "diamond":diamond}

setup_gemstone()

# Claw class variables
claw_image = pygame.image.load(os.path.join(image_path, "claw.png")).convert_alpha()
claw = Claw(claw_image, (screen_width // 2, 110))


## Start game loop

running = True 
while running:
    dt = clock.tick(60) 

    for event in pygame.event.get():
        if event.type == pygame.QUIT: 
            running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if claw.direction != STOP: 
                claw.save_curr_state()
                to_x_claw = move_speed


    # Claw movement (swings)
    if claw.rect.left < -5 or claw.rect.right > screen_width + 5 or claw.rect.bottom > screen_height + 5:
        to_x_claw = -return_speed


    # After shooting out claw, stop retracting when it returns back to original position
    if math.hypot(claw.offset.x, claw.offset.y) < default_offset_x_claw:
        to_x_claw = 0
        claw.set_prev_state()

        # update score if gemstone was caught
        if caught_gemstone:
            update_score(caught_gemstone.price)
            gemstone_group.remove(caught_gemstone)
            caught_gemstone = None


    # claw collisions
    if not caught_gemstone and claw.direction == STOP and to_x_claw > 0:
        for gemstone in gemstone_group:
            if pygame.sprite.collide_mask(claw, gemstone):
                caught_gemstone = gemstone
                to_x_claw = -gemstone.weight_speed 
                break

    if caught_gemstone:
        caught_gemstone.set_position(claw.rect.center, claw.angle)

    # drawing
    screen.blit(background, (0,0))
    gemstone_group.draw(screen)
    claw.update(to_x_claw, dt)
    claw.draw(screen)
    display_score()

    elapsed_time = (pygame.time.get_ticks() - start_ticks) / 1000
    display_time( total_time - int(elapsed_time))

    display_level(level)

    # Update timer information
    if  total_time - int(elapsed_time) <= 0:
        running = False
        game_result = "Game Over"
        display_game_over()
    
    # create a new gemstone on the map every 5s
    elif int(elapsed_time) % 5 == 0:
        if int(elapsed_time) not in create_new_elapsed_time:
            create_new_elapsed_time[int(elapsed_time)] = True
            create_random_gemstone()

    # update screen 
    pygame.display.update()   


## Quit pygame
pygame.time.delay(5000)
pygame.quit()