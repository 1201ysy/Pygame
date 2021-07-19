import pygame
import os


# Constants
BALL_X_SPEED = 0.2
BALL_Y_SPEED = -0.2


## Pygame basic initializations

pygame.init() 

# Screen size settings
screen_width = 640
screen_height = 480
screen  = pygame.display.set_mode((screen_width,screen_height))

# Screen title
pygame.display.set_caption("Pang")

# FPS setting
clock = pygame.time.Clock()


## Variables 
current_path = os.path.dirname(__file__)
image_path = os.path.join(current_path, "images")

# Background/Stage variables
background = pygame.image.load(os.path.join(image_path, "background.png"))

stage = pygame.image.load(os.path.join(image_path, "stage.png"))
stage_size = stage.get_rect().size
stage_height = stage_size[1]


# Character variables
character = pygame.image.load(os.path.join(image_path, "character.png"))
character_size = character.get_rect().size
character_width = character_size[0]
character_height = character_size[1]
character_x_pos = screen_width/2 - character_width/2
character_y_pos = screen_height - character_height - stage_height
character_to_x_left = 0
character_to_x_right = 0
character_speed = 0.5

# Weapon variables
weapon = pygame.image.load(os.path.join(image_path, "weapon.png"))
weapon_size = weapon.get_rect().size
weapon_width = weapon_size[0]
weapon_speed = 1
weapons = []
weapon_to_remove = -1

# Ball variables
ball_images = [
    pygame.image.load(os.path.join(image_path, "balloon1.png")),
    pygame.image.load(os.path.join(image_path, "balloon2.png")),
    pygame.image.load(os.path.join(image_path, "balloon3.png")),
    pygame.image.load(os.path.join(image_path, "balloon4.png"))
]
ball_speed_y = [-0.92, -0.83, -0.74, -0.65]
balls = []
balls.append({"pos_x": 300, "pos_y": 50, "img_idx": 0, "to_x": BALL_X_SPEED, "to_y": BALL_Y_SPEED , "init_spd_y": ball_speed_y[0]})
ball_to_remove = -1


# Font
game_font = pygame.font.SysFont("arialblack", 40)
total_time = 100
start_ticks = pygame.time.get_ticks()

# End game message
game_result = "Game Over"


## Start game loop

running = True 
while running:
    dt = clock.tick(60) 
 
    for event in pygame.event.get():  
        if event.type == pygame.QUIT: 
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                character_to_x_left -= character_speed * dt
            elif event.key == pygame.K_RIGHT:
                character_to_x_right += character_speed * dt
            elif event.key == pygame.K_SPACE:
                weapon_x_pos = character_x_pos + (character_width/2) - (weapon_width/2)
                weapon_y_pos = character_y_pos
                weapons.append([weapon_x_pos, weapon_y_pos])


        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                character_to_x_left = 0
            elif event.key == pygame.K_RIGHT:
                character_to_x_right = 0
            elif event.key == pygame.K_SPACE:
                pass

    # character movement
    character_x_pos += character_to_x_left + character_to_x_right

    # bound character to game screen size
    if character_x_pos < 0:
        character_x_pos = 0
    elif character_x_pos > screen_width - character_width :
        character_x_pos = screen_width - character_width


    # update weapon list movevment speed and filter out weapons that are off screen
    weapons = [ [w[0], w[1] - weapon_speed * dt ] for w in weapons]
    weapons = [ [w[0], w[1]] for w in weapons if w[1] > 0 ]

    # ball movement
    for _, ball_val in enumerate(balls):
        ball_pos_x = ball_val["pos_x"]
        ball_pos_y = ball_val["pos_y"]
        ball_img_idx = ball_val["img_idx"]

        ball_size = ball_images[ball_img_idx].get_rect().size
        ball_width = ball_size[0]
        ball_height = ball_size[1]

        if ball_pos_x < 0 or ball_pos_x > screen_width - ball_width:
            ball_val["to_x"] *= -1

        if ball_pos_y >= screen_height - stage_height - ball_height:
            ball_val["to_y"] = ball_val["init_spd_y"]
        else:
            ball_val["to_y"] += 0.02

        ball_val["pos_x"] += ball_val["to_x"] * dt
        ball_val["pos_y"] += ball_val["to_y"] * dt


    # collision
    character_rect = character.get_rect()
    character_rect.left = character_x_pos
    character_rect.top = character_y_pos
    
    for ball_idx, ball_val in enumerate(balls):
        ball_pos_x = ball_val["pos_x"]
        ball_pos_y = ball_val["pos_y"]
        ball_img_idx = ball_val["img_idx"]

        ball_rect = ball_images[ball_img_idx].get_rect()
        ball_rect.left = ball_pos_x
        ball_rect.top = ball_pos_y

        # Character - Ball collisions
        if character_rect.colliderect(ball_rect):
            print("character ball collision occured")
            game_result = "Game Over"
            running = False
            break

        # Weapon - Ball collisions
        for weapon_idx, weapon_val in enumerate(weapons):
            weapon_pos_x = weapon_val[0]
            weapon_pos_y = weapon_val[1]

            weapon_rect = weapon.get_rect()
            weapon_rect.left = weapon_pos_x
            weapon_rect.top = weapon_pos_y

            if weapon_rect.colliderect(ball_rect):
                print("weapon ball collision occured")
                weapon_to_remove = weapon_idx
                ball_to_remove = ball_idx
  
                if ball_img_idx < 3:
                    small_ball_size = ball_images[ball_img_idx + 1].get_rect().size
                    small_ball_width = small_ball_size[0]
                    small_ball_height = small_ball_size[1]

                    balls.append({"pos_x": ball_pos_x + (ball_width/2) - (small_ball_width/2), "pos_y": ball_pos_y+ (ball_height/2) - (small_ball_height/2), "img_idx": ball_img_idx +1 , "to_x": BALL_X_SPEED, "to_y": BALL_Y_SPEED , "init_spd_y": ball_speed_y[ball_img_idx +1 ]})
                    balls.append({"pos_x": ball_pos_x + (ball_width/2) - (small_ball_width/2), "pos_y": ball_pos_y+ (ball_height/2) - (small_ball_height/2), "img_idx": ball_img_idx +1 , "to_x": -BALL_X_SPEED, "to_y": BALL_Y_SPEED , "init_spd_y": ball_speed_y[ball_img_idx +1 ]})

                break
        else:
            # only 1 ball collision per weapon
            # to prevent weapon also removing newly split ball object 
            continue
        break


    if ball_to_remove > -1:
        del balls[ball_to_remove]
        ball_to_remove = -1

    if weapon_to_remove > -1:
        del weapons[weapon_to_remove]
        weapon_to_remove = -1

    if len(balls) == 0 :
        game_result = "Mission Complete"
        running = False

    # drawings

    screen.blit(background, (0,0))
    screen.blit(stage, (0,screen_height- stage_height))
    screen.blit(character, (character_x_pos, character_y_pos))

    for weapon_x_pos, weapon_y_pos in weapons:
        screen.blit(weapon, (weapon_x_pos,weapon_y_pos))

    for _, ball_val in enumerate(balls):
        ball_pos_x = ball_val["pos_x"]
        ball_pos_y = ball_val["pos_y"]
        ball_img_idx = ball_val["img_idx"]

        screen.blit(ball_images[ball_img_idx], (ball_pos_x, ball_pos_y))

    elapsed_time = (pygame.time.get_ticks() - start_ticks) / 1000
    timer = game_font.render("Time: {}".format(int(total_time - elapsed_time)) , True, (255,255,255))
    screen.blit(timer, (10, 10))

    if total_time - elapsed_time <= 0:
        print("timeout")
        game_result = "Time Over"
        running = False

    # update screen 
    pygame.display.update()   


## Quit pygame
msg = game_font.render(game_result , True, (255,255,255))
msg_rect = msg.get_rect(center = (int(screen_width/2), int(screen_height/2)))
screen.blit(msg, msg_rect)
pygame.display.update()   
pygame.time.delay(2000)
pygame.quit()