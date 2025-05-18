import pygame
import sys
import random
from sqlalchemy import String
from pygame.math import Vector2
from connect import SessionLocal
from databse import high_score

# Initialize pygame
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()

# Game constants
cell_size = 40
cell_number = 20
screen = pygame.display.set_mode((cell_number * cell_size, cell_number * cell_size))
pygame.display.set_caption('Snake Game')
clock = pygame.time.Clock()

# Initialize database session
session = SessionLocal()

# Load assets
try:
    apple = pygame.image.load('Graphics/apple.png').convert_alpha()
except pygame.error:
    apple = pygame.Surface((cell_size, cell_size))
    apple.fill((255, 0, 0))  # Red square as apple

try:
    game_font = pygame.font.Font('Font/PoetsenOne-Regular.ttf', 25)
except:
    game_font = pygame.font.SysFont(None, 25)

# Game event
SCREEN_UPDATE = pygame.USEREVENT
pygame.time.set_timer(SCREEN_UPDATE, 150)

class SNAKE:
    def __init__(self):
        self.reset()
        self.crunch_sound = pygame.mixer.Sound('Sound/crunch.wav')
        
        # Load graphics
        self.head_up = pygame.image.load('Graphics/head_up.png').convert_alpha()
        self.head_down = pygame.image.load('Graphics/head_down.png').convert_alpha()
        self.head_right = pygame.image.load('Graphics/head_right.png').convert_alpha()
        self.head_left = pygame.image.load('Graphics/head_left.png').convert_alpha()
        
        self.tail_up = pygame.image.load('Graphics/tail_up.png').convert_alpha()
        self.tail_down = pygame.image.load('Graphics/tail_down.png').convert_alpha()
        self.tail_right = pygame.image.load('Graphics/tail_right.png').convert_alpha()
        self.tail_left = pygame.image.load('Graphics/tail_left.png').convert_alpha()

        self.body_vertical = pygame.image.load('Graphics/body_vertical.png').convert_alpha()
        self.body_horizontal = pygame.image.load('Graphics/body_horizontal.png').convert_alpha()

        self.body_tr = pygame.image.load('Graphics/body_tr.png').convert_alpha()
        self.body_tl = pygame.image.load('Graphics/body_tl.png').convert_alpha()
        self.body_br = pygame.image.load('Graphics/body_br.png').convert_alpha()
        self.body_bl = pygame.image.load('Graphics/body_bl.png').convert_alpha()

    def reset(self):
        self.body = [Vector2(5,10), Vector2(4,10), Vector2(3,10)]
        self.direction = Vector2(1, 0)
        self.new_block = False

    def draw_snake(self):
        self.update_head_graphics()
        self.update_tail_graphics()

        for index, block in enumerate(self.body):
            x_pos = int(block.x * cell_size)
            y_pos = int(block.y * cell_size)
            block_rect = pygame.Rect(x_pos, y_pos, cell_size, cell_size)

            if index == 0:
                screen.blit(self.head, block_rect)
            elif index == len(self.body) - 1:
                screen.blit(self.tail, block_rect)
            else:
                previous_block = self.body[index + 1] - self.body[index]
                next_block = self.body[index - 1] - self.body[index]
                
                if previous_block.x == next_block.x:
                    screen.blit(self.body_vertical, block_rect)
                elif previous_block.y == next_block.y:
                    screen.blit(self.body_horizontal, block_rect)
                else:
                    if (previous_block.x == -1 and next_block.y == -1) or (previous_block.y == -1 and next_block.x == -1):
                        screen.blit(self.body_tl, block_rect)
                    elif (previous_block.x == -1 and next_block.y == 1) or (previous_block.y == 1 and next_block.x == -1):
                        screen.blit(self.body_bl, block_rect)
                    elif (previous_block.x == 1 and next_block.y == -1) or (previous_block.y == -1 and next_block.x == 1):
                        screen.blit(self.body_tr, block_rect)
                    elif (previous_block.x == 1 and next_block.y == 1) or (previous_block.y == 1 and next_block.x == 1):
                        screen.blit(self.body_br, block_rect)

    def update_head_graphics(self):
        head_relation = self.body[1] - self.body[0]
        if head_relation == Vector2(1,0): self.head = self.head_left
        elif head_relation == Vector2(-1,0): self.head = self.head_right
        elif head_relation == Vector2(0,1): self.head = self.head_up
        elif head_relation == Vector2(0,-1): self.head = self.head_down

    def update_tail_graphics(self):
        tail_relation = self.body[-2] - self.body[-1]
        if tail_relation == Vector2(1,0): self.tail = self.tail_left
        elif tail_relation == Vector2(-1,0): self.tail = self.tail_right
        elif tail_relation == Vector2(0,1): self.tail = self.tail_up
        elif tail_relation == Vector2(0,-1): self.tail = self.tail_down

    def move_snake(self):
        if self.new_block:
            body_copy = self.body[:]
            body_copy.insert(0, body_copy[0] + self.direction)
            self.body = body_copy
            self.new_block = False
        else:
            body_copy = self.body[:-1]
            body_copy.insert(0, body_copy[0] + self.direction)
            self.body = body_copy

    def add_block(self):
        self.new_block = True

    def play_crunch_sound(self):
        self.crunch_sound.play()

class FRUIT:
    def __init__(self):
        self.randomize()
        
    def draw_fruit(self):
        fruit_rect = pygame.Rect(int(self.pos.x * cell_size), int(self.pos.y * cell_size), cell_size, cell_size)
        screen.blit(apple, fruit_rect)

    def randomize(self):
        self.x = random.randint(0, cell_number - 1)
        self.y = random.randint(0, cell_number - 1)
        self.pos = Vector2(self.x, self.y)

class MAIN:
    def __init__(self):
        self.snake = SNAKE()
        self.fruit = FRUIT()
        self.game_active = True
        self.restart_button = pygame.Rect(0, 0, 200, 50)
        self.menu_button = pygame.Rect(0, 0, 200, 50)

    def update(self):
        if self.game_active:
            self.snake.move_snake()
            self.check_collision()
            self.check_fail()

    def draw_elements(self):
        self.draw_grass()
        self.fruit.draw_fruit()
        self.snake.draw_snake()
        self.draw_score()

    def check_collision(self):
        if self.fruit.pos == self.snake.body[0]:
            self.fruit.randomize()
            self.snake.add_block()
            self.snake.play_crunch_sound()
            
            for block in self.snake.body[1:]:
                if block == self.fruit.pos:
                    self.fruit.randomize()

    def check_fail(self):
        head = self.snake.body[0]
        if not (0 <= head.x < cell_number) or not (0 <= head.y < cell_number):
            self.game_over()
        
        for block in self.snake.body[1:]:
            if block == head:
                self.game_over()

    def game_over(self):
        pygame.mixer.music.stop()
        pygame.mixer.Sound('Sound/game_over.mp3').play()
        self.game_active = False
        score = len(self.snake.body) - 3
        
        if score > 0:
            self.save_score(score)
        else:
            self.show_game_over_screen()

    def save_score(self, score):
        save_screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Save Score")

        font = pygame.font.Font(None, 60)
        input_box = pygame.Rect(250, 300, 300, 60)
        color = pygame.Color('dodgerblue2')
        text = ''
        saving = True

        while saving:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        try:
                            new_score = high_score(name=text, high_score=score)
                            session.add(new_score)
                            session.commit()
                            saving = False
                        except Exception as e:
                            print(f"Error saving score: {e}")
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode

            save_screen.fill((255, 255, 255))
            prompt = font.render("Enter your name:", True, (0, 0, 0))
            save_screen.blit(prompt, (250, 250))

            txt_surface = font.render(text, True, color)
            input_box.w = max(300, txt_surface.get_width() + 10)
            save_screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
            pygame.draw.rect(save_screen, color, input_box, 2)

            pygame.display.flip()
            clock.tick(30)

        screen = pygame.display.set_mode((cell_number * cell_size, cell_number * cell_size))
        self.show_game_over_screen()

    def show_game_over_screen(self):
        showing = True
        
        while showing:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if self.restart_button.collidepoint(mouse_pos):
                        self.restart_game()
                        showing = False
                    elif self.menu_button.collidepoint(mouse_pos):
                        self.go_to_main_menu()
                        showing = False

            # Draw game elements (snake, fruit, etc.)
            screen.fill((175, 215, 70))
            self.draw_elements()
            
            # Dark overlay
            overlay = pygame.Surface((cell_number * cell_size, cell_number * cell_size), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            
            # Game over text
            font = pygame.font.Font(None, 72)
            game_over_surface = font.render("GAME OVER", True, (255, 255, 255))
            game_over_rect = game_over_surface.get_rect(center=(cell_number * cell_size // 2, cell_number * cell_size // 3))
            screen.blit(game_over_surface, game_over_rect)
            
            # Score text
            score_text = f"Score: {len(self.snake.body) - 3}"
            score_surface = font.render(score_text, True, (255, 255, 255))
            score_rect = score_surface.get_rect(center=(cell_number * cell_size // 2, cell_number * cell_size // 2))
            screen.blit(score_surface, score_rect)
            
            # Buttons
            button_y = cell_number * cell_size // 2 + 100
            self.restart_button.center = (cell_number * cell_size // 2 - 120, button_y)
            self.menu_button.center = (cell_number * cell_size // 2 + 120, button_y)
            
            pygame.draw.rect(screen, (50, 205, 50), self.restart_button, border_radius=10)
            pygame.draw.rect(screen, (70, 130, 180), self.menu_button, border_radius=10)
            
            button_font = pygame.font.Font(None, 30)
            restart_text = button_font.render("Restart", True, (255, 255, 255))
            menu_text = button_font.render("Main Menu", True, (255, 255, 255))
            
            screen.blit(restart_text, (self.restart_button.centerx - restart_text.get_width() // 2, 
                                      self.restart_button.centery - restart_text.get_height() // 2))
            screen.blit(menu_text, (self.menu_button.centerx - menu_text.get_width() // 2, 
                                   self.menu_button.centery - menu_text.get_height() // 2))

            pygame.display.update()
            clock.tick(60)

    def draw_grass(self):
        grass_color = (167, 209, 61)
        for row in range(cell_number):
            for col in range(row % 2, cell_number, 2):
                grass_rect = pygame.Rect(col * cell_size, row * cell_size, cell_size, cell_size)
                pygame.draw.rect(screen, grass_color, grass_rect)

    def draw_score(self):
        score_text = str(len(self.snake.body) - 3)
        score_surface = game_font.render(score_text, True, (56, 74, 12))
        score_x = int(cell_size * cell_number - 60)
        score_y = int(cell_size * cell_number - 40)
        score_rect = score_surface.get_rect(center=(score_x, score_y))
        apple_rect = apple.get_rect(midright=(score_rect.left, score_rect.centery))
        bg_rect = pygame.Rect(apple_rect.left, apple_rect.top, 
                            apple_rect.width + score_rect.width + 6, apple_rect.height)

        pygame.draw.rect(screen, (167, 209, 61), bg_rect)
        screen.blit(score_surface, score_rect)
        screen.blit(apple, apple_rect)
        pygame.draw.rect(screen, (56, 74, 12), bg_rect, 2)

    def restart_game(self):
        self.snake.reset()
        self.fruit.randomize()
        self.game_active = True

    def go_to_main_menu(self):
        from main import main_menu
        main_menu()  # Replace with actual main menu logic if needed
