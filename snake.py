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

class OBSTACLE:
    def __init__(self, snake_body, fruit_pos):
        self.obstacles = []
        self.obstacle_count = 0
        self.debug_mode = True  # Set to True for debugging output
        
        # Load the stone image for obstacles
        try:
            self.stone_image = pygame.image.load('Graphics/stone.png').convert_alpha()
            if self.debug_mode:
                print("Stone image loaded successfully")
        except Exception as e:
            self.stone_image = None
            print(f"Error loading stone image: {e}")
            print("Creating fallback obstacle graphics")
            
            # Create a distinctive fallback surface
            self.fallback_surface = pygame.Surface((cell_size, cell_size), pygame.SRCALPHA)
            self.fallback_surface.fill((100, 50, 50))  # Reddish-brown color
            
            # Add clear markings to the fallback surface
            pygame.draw.rect(self.fallback_surface, (50, 20, 20), 
                            pygame.Rect(0, 0, cell_size, cell_size), 4)
            pygame.draw.line(self.fallback_surface, (200, 50, 50), 
                            (0, 0), (cell_size, cell_size), 3)
            pygame.draw.line(self.fallback_surface, (200, 50, 50), 
                            (cell_size, 0), (0, cell_size), 3)
            
        # Generate obstacles with structured patterns instead of random
        self.generate_structured_obstacles(snake_body, fruit_pos)
    
    def generate_structured_obstacles(self, snake_body, fruit_pos):
        """Generate obstacles in structured patterns including straight lines"""
        self.obstacles.clear()
        
        # Create at least 3 straight lines with 4 obstacles each
        self._create_structured_lines(snake_body, fruit_pos)
        
        # Add some additional random obstacles if needed
        remaining_obstacles = 20 - len(self.obstacles)
        if remaining_obstacles > 0:
            self._add_random_obstacles(snake_body, fruit_pos, remaining_obstacles)
            
        self.obstacle_count = len(self.obstacles)
        if self.debug_mode:
            print(f"Total obstacles: {len(self.obstacles)}")
            
    def _create_structured_lines(self, snake_body, fruit_pos):
        """Create at least 3 straight lines with 4 obstacles each"""
        # Define potential line configurations (try more configurations than needed)
        line_configs = [
            # Horizontal lines (x, y, length, direction)
            {'start_x': 2, 'start_y': 5, 'length': 4, 'horizontal': True},
            {'start_x': 14, 'start_y': 8, 'length': 4, 'horizontal': True},
            {'start_x': 6, 'start_y': 12, 'length': 4, 'horizontal': True},
            {'start_x': 10, 'start_y': 16, 'length': 4, 'horizontal': True},
            
            # Vertical lines (x, y, length, direction)
            {'start_x': 5, 'start_y': 2, 'length': 4, 'horizontal': False},
            {'start_x': 15, 'start_y': 3, 'length': 4, 'horizontal': False},
            {'start_x': 10, 'start_y': 10, 'length': 4, 'horizontal': False},
            {'start_x': 8, 'start_y': 14, 'length': 4, 'horizontal': False}
        ]
        
        # Shuffle the configurations to get different patterns each time
        random.shuffle(line_configs)
        
        lines_created = 0
        for config in line_configs:
            # Try to create this line
            if self._try_create_line(config, snake_body, fruit_pos):
                lines_created += 1
                # Stop once we've created at least 3 lines
                if lines_created >= 3:
                    break
    
    def _try_create_line(self, config, snake_body, fruit_pos):
        """Try to create a line according to the given configuration"""
        # Extract configuration
        start_x = config['start_x']
        start_y = config['start_y']
        length = config['length']
        horizontal = config['horizontal']
        
        # Check if line can be placed
        positions = []
        for i in range(length):
            if horizontal:
                pos = Vector2(start_x + i, start_y)
            else:
                pos = Vector2(start_x, start_y + i)
                
            # Check boundaries
            if not (0 <= pos.x < cell_number and 0 <= pos.y < cell_number):
                return False
                
            # Check if position is already occupied
            if pos in snake_body or pos == fruit_pos or pos in self.obstacles:
                return False
                
            positions.append(pos)
        
        # If we got here, the line can be placed
        self.obstacles.extend(positions)
        
        if self.debug_mode:
            line_type = "horizontal" if horizontal else "vertical"
            print(f"Created {line_type} line at ({start_x}, {start_y}) with length {length}")
        
        return True
        
    def _add_random_obstacles(self, snake_body, fruit_pos, count):
        """Add random obstacles to fill up to the desired count"""
        for i in range(count):
            attempts = 0
            while attempts < 100:  # Limit attempts to prevent infinite loop
                pos = Vector2(random.randint(0, cell_number - 1), random.randint(0, cell_number - 1))
                
                # Check if position is valid (not on snake, fruit, or existing obstacle)
                if pos not in snake_body and pos != fruit_pos and pos not in self.obstacles:
                    self.obstacles.append(pos)
                    if self.debug_mode:
                        print(f"Random obstacle added at {pos}")
                    break
                
                attempts += 1
    
    def generate_obstacles(self, snake_body, fruit_pos, count=0):
        """Legacy method kept for compatibility"""
        self.generate_structured_obstacles(snake_body, fruit_pos)
    
    def draw_obstacles(self):
        """Draw all obstacles on the screen"""
        if not self.obstacles and self.debug_mode:
            print("No obstacles to draw")
            
        for obstacle in self.obstacles:
            obstacle_rect = pygame.Rect(int(obstacle.x * cell_size), int(obstacle.y * cell_size), cell_size, cell_size)
            
            if self.stone_image:
                # Use the stone image
                screen.blit(self.stone_image, obstacle_rect)
            else:
                # Draw a very visible fallback
                if hasattr(self, 'fallback_surface'):
                    screen.blit(self.fallback_surface, obstacle_rect)
                else:
                    # Even more basic fallback
                    pygame.draw.rect(screen, (255, 0, 0), obstacle_rect)  # Bright red
                    pygame.draw.rect(screen, (0, 0, 0), obstacle_rect, 3)  # Black border
                    # Add X marking
                    pygame.draw.line(screen, (0, 0, 0), 
                                   (obstacle_rect.left, obstacle_rect.top), 
                                   (obstacle_rect.right, obstacle_rect.bottom), 4)
                    pygame.draw.line(screen, (0, 0, 0), 
                                   (obstacle_rect.left, obstacle_rect.bottom), 
                                   (obstacle_rect.right, obstacle_rect.top), 4)
    
    def check_collision(self, pos):
        """Check if the given position collides with any obstacle"""
        return pos in self.obstacles
    
    def increase_difficulty(self, score, snake_body, fruit_pos):
        """Add obstacles as score increases"""
        # Method kept for backwards compatibility
        pass

class SNAKE:
    def __init__(self, sound_manager=None):
        self.reset()
        self.sound_manager = sound_manager
        self.crunch_sound = pygame.mixer.Sound('Sound/crunch.wav')
        
        # Set initial volume based on sound manager
        if self.sound_manager:
            volume = 0 if self.sound_manager.muted else self.sound_manager.sfx_volume
            self.crunch_sound.set_volume(volume)
        
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
        # Use sound manager if available, otherwise play directly
        if self.sound_manager:
            # If we have sound manager, respect its settings
            if not self.sound_manager.muted:
                self.crunch_sound.set_volume(self.sound_manager.sfx_volume)
                self.crunch_sound.play()
        else:
            # Default behavior without sound manager
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
    def __init__(self, sound_manager=None):
        self.sound_manager = sound_manager
        self.snake = SNAKE(sound_manager)
        self.fruit = FRUIT()
        self.obstacles = OBSTACLE(self.snake.body, self.fruit.pos)
        self.game_active = True
        self.restart_button = pygame.Rect(0, 0, 200, 50)
        self.menu_button = pygame.Rect(0, 0, 200, 50)
        self.score = 0

    def update(self):
        if self.game_active:
            self.snake.move_snake()
            self.check_collision()
            self.check_fail()
            
            # Update score without changing obstacles
            current_score = len(self.snake.body) - 3
            if current_score > self.score:
                self.score = current_score

    def draw_elements(self):
        self.draw_grass()
        self.obstacles.draw_obstacles()  # Draw obstacles
        self.fruit.draw_fruit()
        self.snake.draw_snake()
        self.draw_score()

    def check_collision(self):
        if self.fruit.pos == self.snake.body[0]:
            self.fruit.randomize()
            self.snake.add_block()
            self.snake.play_crunch_sound()
            
            # Make sure fruit doesn't appear on snake or obstacles
            while self.fruit.pos in self.snake.body or self.fruit.pos in self.obstacles.obstacles:
                self.fruit.randomize()

    def check_fail(self):
        head = self.snake.body[0]
        # Check boundary collision
        if not (0 <= head.x < cell_number) or not (0 <= head.y < cell_number):
            self.game_over()
        
        # Check snake self collision
        for block in self.snake.body[1:]:
            if block == head:
                self.game_over()
        
        # Check obstacle collision
        if self.obstacles.check_collision(head):
            self.game_over()

    def game_over(self):
        # Use sound manager if available
        if self.sound_manager:
            self.sound_manager.stop_bgm()
            if not self.sound_manager.muted:
                game_over_sound = pygame.mixer.Sound('Sound/game_over.mp3')
                game_over_sound.set_volume(self.sound_manager.sfx_volume)
                game_over_sound.play()
        else:
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
        small_font = pygame.font.Font(None, 30)
        input_box = pygame.Rect(250, 300, 300, 60)
        color = pygame.Color('dodgerblue2')
        text = ''
        saving = True
        error_message = None
        score_saved = False
        save_button = pygame.Rect(350, 400, 100, 50)
        
        while saving:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        # Try to save score
                        if text:
                            self._attempt_save_score(text, score)
                            score_saved = True
                            saving = False
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    elif event.key == pygame.K_ESCAPE:
                        saving = False
                    else:
                        # Limit name length
                        if len(text) < 15:
                            text += event.unicode
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if save_button.collidepoint(mouse_pos):
                        if text:
                            self._attempt_save_score(text, score)
                            score_saved = True
                            saving = False
            
            save_screen.fill((175, 215, 70))
            
            # Title
            title_surface = font.render("SAVE YOUR SCORE", True, (56, 74, 12))
            save_screen.blit(title_surface, (250, 150))
            
            # Score display
            score_text = f"Score: {score}"
            score_surface = font.render(score_text, True, (56, 74, 12))
            save_screen.blit(score_surface, (250, 200))
            
            # Input prompt
            prompt = font.render("Enter your name:", True, (56, 74, 12))
            save_screen.blit(prompt, (250, 250))
            
            # Input box
            txt_surface = font.render(text, True, color)
            pygame.draw.rect(save_screen, color, input_box, 2)
            save_screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
            
            # Save button
            pygame.draw.rect(save_screen, (50, 205, 50), save_button, border_radius=10)
            save_text = small_font.render("SAVE", True, (255, 255, 255))
            save_screen.blit(save_text, (save_button.x + 25, save_button.y + 15))
            
            # Instruction text
            instruction_text = small_font.render("Press ENTER to save or ESC to skip", True, (56, 74, 12))
            save_screen.blit(instruction_text, (250, 500))
            
            pygame.display.flip()
            clock.tick(30)
        
        # Restore game screen
        screen = pygame.display.set_mode((cell_number * cell_size, cell_number * cell_size))
        self.show_game_over_screen()
    
    def _attempt_save_score(self, name, score):
        # Helper method to attempt saving the score
        try:
            new_score = high_score(name=name, high_score=score)
            session.add(new_score)
            session.commit()
            return True
        except Exception as e:
            error_msg = str(e)
            print(f"Error saving score: {error_msg}")
            
            # Try fallback to local file if database fails
            try:
                with open("local_scores.txt", "a") as f:
                    f.write(f"{name},{score}\n")
                print("Score saved to local file instead")
                return True
            except Exception as local_err:
                print(f"Failed to save locally: {local_err}")
                return False

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
        self.obstacles = OBSTACLE(self.snake.body, self.fruit.pos)  # Reset obstacles
        self.score = 0  # Reset score
        self.game_active = True

    def go_to_main_menu(self):
        from main import main_menu
        main_menu()  # Replace with actual main menu logic if needed
