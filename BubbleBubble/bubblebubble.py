import pygame
import os
import math
import random


# Bubble sprite class
class Bubble(pygame.sprite.Sprite):
    def __init__(self,  color, image, animation = None, position=(0,0), row_idx=-1, col_idx=-1):
        super().__init__()
        self.image = image
        self.color = color
        self.position = position
        self.rect = image.get_rect(center = position)
        self.radius = 18
        self.row_idx = row_idx
        self.col_idx = col_idx   
        self.sparkle = random.randint(0, len(sparkle_animation) -1)
        self.animation = animation
        self.fall_speed = fall_speed + random.randint(self.row_idx, self.row_idx + 2)

    def set_rect(self, position):
        self.rect = self.image.get_rect(center=position)

    def set_angle(self, angle):
        self.angle = angle
        self.rad_angle = math.radians(angle)

    def set_map_index(self, row_idx, col_idx):
        self.row_idx = row_idx
        self.col_idx = col_idx       

    def draw(self, screen, to_x = None):
        if to_x:
            screen.blit(self.image, (self.rect.x + to_x , self.rect.y))
        else:
            screen.blit(self.image, self.rect)
    
    def draw_remove(self, screen):
        if animation_count % 2 == 0:
            screen.blit(sparkle_animation[self.sparkle], self.rect)
        screen.blit(self.animation[animation_count], self.rect)

    def move(self):
        to_x = self.radius * math.cos(self.rad_angle)
        to_y = self.radius * math.sin(self.rad_angle) * -1

        self.rect.x += to_x
        self.rect.y += to_y

        if self.rect.left < 0 or self.rect.right > screen_width:
            self.set_angle(180 - self.angle)
    
    def fall(self):
        self.rect.y += self.fall_speed

    def drop_downward(self, height):
        self.rect = self.image.get_rect(center= (self.rect.centerx, self.rect.centery + height))

# Pointer sprite class
class Pointer(pygame.sprite.Sprite):
    def __init__(self, image, position, angle):
        super().__init__()
        self.image = image
        self.position = position
        self.rect = image.get_rect(center = position)  
        self.angle = angle
        self.original_image = image
    
    def draw(self, screen):
        screen.blit(self.image, self.rect)
    
    def rotate(self, angle):
        self.angle += angle
        
        if self.angle > 170:
            self.angle = 170
        elif self.angle < 10:
            self.angle = 10
        
        self.image = pygame.transform.rotozoom( self.original_image, self.angle, 1)
        self.rect = self.image.get_rect(center=self.position)


# Setup game map based on level
# map data stored as a list of character
# 'R','B','P','Y','G' = Color bubbles
# '.' = empty spot
# '/' = invalid spot (odd rows has 1 less spot)
def setup():
    global map, level
    map = [[
        list(".RRRR..."),
        list("..RRR../"),
        list("....Y..."),  
        list("...YY../"),
        list("....Y..."),
        list("......./"),  
        list("........"),
        list("......./"),
        list("........"),
        list("......./"),
        list("........"),
        ],
        [
        list("RRYYBBGG"),
        list("RRYYBBG/"),
        list("BBGGRRYY"),
        list("BGGRRYY/"),
        list("........"),
        list("......./"),
        list("........"),
        list("......./"),
        list("........"),
        list("......./"),
        list("........")        
        ],
        [
        list("...YY..."),
        list("...G.../"),
        list("...R...."),
        list("...B.../"),
        list("...R...."),
        list("...G.../"),
        list("...P...."),
        list("...P.../"),
        list("........"),
        list("......./"),
        list("........")
        ],
        [
        list("G......G"),
        list("RGBYRGB/"),
        list("Y......Y"),
        list("BYRGBYR/"),
        list("...R...."),
        list("...G.../"),
        list("...R...."),
        list("......./"),
        list("........"),
        list("......./"),
        list("........")
        ]
    ]

    for row_idx, row in enumerate(map[level]):
        for col_idx, col in enumerate(row):
            if col in [".", "/"]:
                continue
            position = get_bubble_position(row_idx, col_idx)
            image, animation = get_bubble_image(col)
            if image:
                bubble_group.add(Bubble(col, image, animation,  position,  row_idx, col_idx))

# Returns bubble (x,y) position of bubble given row,col index from the map list
def get_bubble_position(row,col):
    x = col * CELL_SIZE + BUBBLE_WIDTH//2
    y = row * CELL_SIZE + BUBBLE_HEIGHT//2 + wall_height
    if row % 2 == 1:
        x += BUBBLE_WIDTH//2
    return (x,y)

# Get bubble image for the "color" if it exists
def get_bubble_image(color):
    if color in bubble_images:
        if "animation" in bubble_images[color]:
            return bubble_images[color]["base"], bubble_images[color]["animation"]
        else:
            return  bubble_images[color]["base"], None

# Prepares current and next bubbles 
def prepare_bubbles(waiting = False):
    global curr_bubble, next_bubble
    if not waiting:
        if next_bubble:
            curr_bubble = next_bubble
        else:
            curr_bubble = create_bubble()

        curr_bubble.set_rect((screen_width//2, 624))
        next_bubble = create_bubble()
        next_bubble.set_rect((screen_width//4, 688))

# Randomly create a bubble 
def create_bubble():
    color = get_random_bubble_color()
    image, animation = get_bubble_image(color)
    return Bubble(color,image, animation)

# Randomly create a bubble color out of colors that already exists on the map
def get_random_bubble_color():
    global map, level
    colors = []
    for row in map[level]:
        for col in row:
            if col not in colors and col not in [".", "/"]:
                colors.append(col)
    return random.choice(colors)

# Check collision when bubbles are fired
def process_collision():
    global curr_bubble, fire, curr_fire_count
    hit_bubble = pygame.sprite.spritecollideany(curr_bubble, bubble_group, pygame.sprite.collide_mask)
    if hit_bubble or  curr_bubble.rect.top <= wall_height:
        row_idx, col_idx = get_map_index(*curr_bubble.rect.center)
        place_bubble(curr_bubble, row_idx, col_idx)
        remove_adjacent_bubbles(row_idx,col_idx,curr_bubble.color)
        curr_bubble = None
        fire = False
        curr_fire_count -= 1

# Get the map row,col index based on the x,y position on the screen
def get_map_index(x, y):
    row_idx = (y - wall_height) // CELL_SIZE
    col_idx = x // CELL_SIZE
    if row_idx % 2 == 1:
        col_idx = (x - CELL_SIZE//2) // CELL_SIZE 
        if col_idx > MAP_COL_COUNT -2: # even row has 1 less bubble
            col_idx = MAP_COL_COUNT -2
        elif col_idx < 0:
            col_idx = 0

    return row_idx, col_idx

# Place bubble "bubble" in "row_idx, col_idx" on the map and add to "bubble_group" group
def place_bubble(bubble, row_idx, col_idx):
    map[level][row_idx][col_idx] = bubble.color
    position = get_bubble_position(row_idx, col_idx)
    bubble.set_rect(position)
    bubble.set_map_index(row_idx, col_idx)
    bubble_group.add(bubble)

# Remove adjacent bubbles if there are more than 3 of the same color bubbles connected
# also remove hanging (floating) bubbles after removing the adjacent bubbles (not connected to top of screen/wall)
def remove_adjacent_bubbles(row_idx, col_idx, color):
    visited.clear()
    visit(row_idx, col_idx, color)
    if len(visited) >= 3:
        remove_visited_bubbles()
        remove_hanging_bubbles()

# Visit adjacent bubbles and update visited list
# If color is None, visit all adjacent bubbles regardless of its color
# else only check if same color 
def visit(row_idx, col_idx, color= None):
    if row_idx < 0 or row_idx >= MAP_ROW_COUNT or col_idx <0 or col_idx >= MAP_COL_COUNT:
        return 
    if color and map[level][row_idx][col_idx] != color:
        return
    if map[level][row_idx][col_idx] in [".", "/"]:
        return    
    if (row_idx, col_idx) in visited:
        return
    visited.append((row_idx,col_idx))
    
    # Adjacent row/col is different for even/odd rows (because odd rows have 1 less spot)
    # Adjacent bubbles index for even rows
    rows = [0, -1, -1, 0, 1, 1]
    cols = [-1, -1, 0, 1, 0, -1]

    if row_idx % 2 ==1:
        # Adjacent bubbles index for col rows
        rows = [0, -1, -1, 0, 1, 1]
        cols = [-1, 0 , 1, 1, 1, 0]

    for i in range(len(rows)):
        visit(row_idx + rows[i], col_idx + cols[i], color)

# Remove all bubbles in the visited list
def remove_visited_bubbles():
    bubbles_to_remove = [ b for b in bubble_group if (b.row_idx, b.col_idx) in visited]
    for bubble in bubbles_to_remove:
        map[level][bubble.row_idx][bubble.col_idx] = "."
        removing_bubble_group.add(bubble)
        bubble_group.remove(bubble)

# Remove all bubbles not in the visited list
def remove_not_visited_bubbles():
    bubbles_to_remove = [ b for b in bubble_group if (b.row_idx, b.col_idx) not in visited]
    for bubble in bubbles_to_remove:
        map[level][bubble.row_idx][bubble.col_idx] = "."
        falling_bubble_group.add(bubble)
        bubble_group.remove(bubble)
 
# Remove hanging bubbles
def remove_hanging_bubbles():
    visited.clear()
    for col_idx in range(MAP_COL_COUNT):
        if map[level][0][col_idx] != ".":
            visit(0, col_idx)
    remove_not_visited_bubbles()

# Draws animation for falling bubbles after it has been removed from bubble_group
def draw_falling_bubbles():
    for bubble in falling_bubble_group:
        bubble.fall()
        bubble.draw(screen)
        if bubble.rect.top > screen_height:
            falling_bubble_group.remove(bubble)

# Draws animation for removing bubbles (when 3+ bubbles of the same bubble connects) after it has been removed from bubble_group
def draw_removing_bubbles():
    global frame_count, animation_count
    frame_count +=1
    if frame_count !=0 and frame_count % 5 == 0:
        animation_count += 1
        if animation_count > NUM_ANIMATION_FRAMES - 1:
            animation_count = 0
            removing_bubble_group.empty()
            frame_count = 0

    for bubble in removing_bubble_group:
        bubble.draw_remove(screen)


# Draws bubble sprite group 
def draw_bubbles():
    to_x = None
    # Shake the bubbles to show wall is coming down soon
    if curr_fire_count == 2:
        to_x = random.randint(-1, 1) 
    elif curr_fire_count == 1:
        to_x = random.randint(-4, 4)
    
    for bubble in bubble_group:
        bubble.draw(screen, to_x)

# Drop the wall and update bubbles accordingly
def drop_wall():
    global wall_height, curr_fire_count
    wall_height += CELL_SIZE
    for bubble in bubble_group:
        bubble.drop_downward((CELL_SIZE))
    for bubble in removing_bubble_group :
        bubble.drop_downward((CELL_SIZE))
    for bubble in falling_bubble_group :
        bubble.drop_downward((CELL_SIZE))
    curr_fire_count = FIRE_COUNT

# returns the lowest bottom y bubble position of the bubble group
def get_lowest_bubble_bottom():
    bubble_bottoms = [b.rect.bottom for b in bubble_group]
    return max(bubble_bottoms)

# change all the bubble color to black
def change_bubble_color():
    for bubble in bubble_group:
        bubble.image = bubble_images["BL"]["base"]

def display_next_level():
    msg_line1 = game_font.render(f"STARTING", True, WHITE)
    msg_line2 = game_font.render(f"NEXT LEVEL: {level}", True, WHITE)
    msg_rect1 = msg_line1.get_rect(center=(screen_width/2, screen_height/2 - 60))
    msg_rect2 = msg_line2.get_rect(center=(screen_width/2, screen_height/2 + 10))
    screen.blit(msg_line1, msg_rect1)
    screen.blit(msg_line2, msg_rect2)

def display_game_over():
    msg = game_font.render(f"{game_result}", True, WHITE)
    msg_rect = msg.get_rect(center=(screen_width/2, screen_height/2))
    screen.blit(msg, msg_rect)

##################################################################################
## Pygame basic initializations

pygame.init() 

# Resource Paths
current_path = os.path.dirname(__file__)
image_path = os.path.join(current_path, "images")

# Screen size & title settings
screen_width = 448
screen_height = 720
screen  = pygame.display.set_mode((screen_width,screen_height))
pygame.display.set_caption("BubbleBubble")

# Font
game_font = pygame.font.SysFont("arialblack", 40)

# FPS setting
clock = pygame.time.Clock()


## Variables

# Constnts
CELL_SIZE = 56
BUBBLE_WIDTH = 56
BUBBLE_HEIGHT = 62
MAP_ROW_COUNT = 11
MAP_COL_COUNT = 8
NUM_ANIMATION_FRAMES = 4
FIRE_COUNT = 7
BLACK = (0,0,0)
WHITE = (255,255,255)


# Movements
to_angle_left = 0
to_angle_right = 0
angle_speed = 1.5/60
fall_speed = 15


# Images 
background = pygame.image.load(os.path.join(image_path, "background.png"))
wall = pygame.image.load(os.path.join(image_path, "wall.png"))
pointer_image = pygame.image.load(os.path.join(image_path, "pointer.png"))

bubble_images = {
    "R" : {
        "base":pygame.image.load(os.path.join(image_path, "red.png")).convert_alpha(),
        "animation": [
            pygame.image.load(os.path.join(image_path, "red_1.png")).convert_alpha(),
            pygame.image.load(os.path.join(image_path, "red_2.png")).convert_alpha(),
            pygame.image.load(os.path.join(image_path, "red_3.png")).convert_alpha(),
            pygame.image.load(os.path.join(image_path, "red_4.png")).convert_alpha(),
        ]
    }, 
    "Y" : {
        "base":pygame.image.load(os.path.join(image_path, "yellow.png")).convert_alpha(),
        "animation": [
            pygame.image.load(os.path.join(image_path, "yellow_1.png")).convert_alpha(),
            pygame.image.load(os.path.join(image_path, "yellow_2.png")).convert_alpha(),
            pygame.image.load(os.path.join(image_path, "yellow_3.png")).convert_alpha(),
            pygame.image.load(os.path.join(image_path, "yellow_4.png")).convert_alpha(),
        ]
    }, 

    "B" : {
        "base":pygame.image.load(os.path.join(image_path, "blue.png")).convert_alpha(),
        "animation": [
            pygame.image.load(os.path.join(image_path, "blue_1.png")).convert_alpha(),
            pygame.image.load(os.path.join(image_path, "blue_2.png")).convert_alpha(),
            pygame.image.load(os.path.join(image_path, "blue_3.png")).convert_alpha(),
            pygame.image.load(os.path.join(image_path, "blue_4.png")).convert_alpha(),
        ]
    }, 
    "G" : {
        "base":pygame.image.load(os.path.join(image_path, "green.png")).convert_alpha(),
        "animation": [
            pygame.image.load(os.path.join(image_path, "green_1.png")).convert_alpha(),
            pygame.image.load(os.path.join(image_path, "green_2.png")).convert_alpha(),
            pygame.image.load(os.path.join(image_path, "green_3.png")).convert_alpha(),
            pygame.image.load(os.path.join(image_path, "green_4.png")).convert_alpha(),
        ]
    }, 
    "P" : {
        "base":pygame.image.load(os.path.join(image_path, "purple.png")).convert_alpha(),
        "animation": [
            pygame.image.load(os.path.join(image_path, "purple_1.png")).convert_alpha(),
            pygame.image.load(os.path.join(image_path, "purple_2.png")).convert_alpha(),
            pygame.image.load(os.path.join(image_path, "purple_3.png")).convert_alpha(),
            pygame.image.load(os.path.join(image_path, "purple_4.png")).convert_alpha(),
        ]
    }, 

    "BL" : {
        "base":pygame.image.load(os.path.join(image_path, "black.png")).convert_alpha(),
    }, 
}

sparkle_animation = [

pygame.image.load(os.path.join(image_path, "sparkle1.png")).convert_alpha(),
pygame.image.load(os.path.join(image_path, "sparkle2.png")).convert_alpha(),
pygame.image.load(os.path.join(image_path, "sparkle3.png")).convert_alpha(),

]


# Game asset variables
map = []
visited = []
bubble_group = pygame.sprite.Group()
falling_bubble_group = pygame.sprite.Group()
removing_bubble_group = pygame.sprite.Group()
pointer = Pointer(pointer_image, (screen_width//2, 624), 90)

# Game state variables
level = 1
curr_bubble = None
next_bubble = None
fire = False
curr_fire_count = FIRE_COUNT
wall_height = 0
is_game_over = False
game_result = None
waiting = False
animation_count = 0
frame_count = 0

## Start game loop

setup()


running = True
while running:
    dt = clock.tick(60) 

    for event in pygame.event.get():
        if event.type == pygame.QUIT: 
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                to_angle_left += angle_speed * dt
            elif event.key == pygame.K_RIGHT:
                to_angle_right -= angle_speed * dt
            elif event.key == pygame.K_SPACE:
                if curr_bubble and not fire:
                    fire = True
                    curr_bubble.set_angle(pointer.angle)

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                to_angle_left = 0 
            elif event.key == pygame.K_RIGHT:
                to_angle_right = 0
        


    # Drawing
    if not curr_bubble:
        prepare_bubbles(waiting)

    if fire:
        process_collision()

    if curr_fire_count == 0:
        drop_wall()
    

    screen.blit(background, (0,0))
    screen.blit(wall, (0, wall_height - screen_height))
    draw_bubbles()

    if removing_bubble_group:
        draw_removing_bubbles()

    if falling_bubble_group:
        draw_falling_bubbles()

    pointer.rotate(to_angle_right + to_angle_left )
    pointer.draw(screen)

    # check if current level is cleared
    if not bubble_group:
        # if final level was complete, end game
        waiting = True
        if level == 3:
            game_result = "Mission Complete"
            is_game_over = True
        # if not on final level, move on to next level
        elif not (falling_bubble_group or removing_bubble_group):
            level += 1
            wall_height = 0
            curr_fire_count = FIRE_COUNT
            curr_bubble = None
            next_bubble = None
            waiting = False
            setup()
            display_next_level()
            pygame.display.update()
            total_time = 3
            start_ticks = pygame.time.get_ticks()
            elapsed_time = (pygame.time.get_ticks() - start_ticks) / 1000
            while (total_time - int(elapsed_time) > 0):
                elapsed_time = (pygame.time.get_ticks() - start_ticks) / 1000
            
    # check if current level failed (bubble reached the bottom)
    elif get_lowest_bubble_bottom() > len(map[level]) * CELL_SIZE:
        game_result = "Game Over"
        is_game_over = True
        change_bubble_color()
        draw_bubbles()

    if curr_bubble:
        if fire:
            curr_bubble.move()
        curr_bubble.draw(screen)

    if next_bubble:
        next_bubble.draw(screen)


    if is_game_over:
        display_game_over()
        running = False

    # update screen 
    pygame.display.update()   


## Quit pygame
pygame.time.delay(5000)
pygame.quit()