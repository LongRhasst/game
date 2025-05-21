import pygame, sys
from button import Button
from snake import *
from connect import SessionLocal
from databse import high_score
from snake import MAIN
from sound_manager import SoundManager  # Import SoundManager

session = SessionLocal()

pygame.mixer.init()
sound_manager = SoundManager()  # Create a SoundManager instance
click_sound = pygame.mixer.Sound("Sound/click.mp3")

SCREEN = pygame.display.set_mode((1280, 850))
pygame.display.set_caption("Menu")

BG = pygame.image.load("assets/Background.jpg")

def get_font(size): # Returns Press-Start-2P in the desired size
    return pygame.font.Font("assets/font.ttf", size)

def play():
    pygame.mixer.pre_init(44100,-16,2,512)
    pygame.init()
    cell_size = 40
    cell_number = 20
    screen = pygame.display.set_mode((cell_number * cell_size,cell_number * cell_size))
    clock = pygame.time.Clock()

    SCREEN_UPDATE = pygame.USEREVENT
    pygame.time.set_timer(SCREEN_UPDATE,150)

    # Pass sound manager to MAIN
    main_game = MAIN(sound_manager=sound_manager)
    
    # Use sound manager for background music
    if not sound_manager.muted:
        sound_manager.play_bgm()
    else:
        pygame.mixer.music.stop()  # Ensure music is stopped if muted
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == SCREEN_UPDATE:
                main_game.update()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    if main_game.snake.direction.y != 1:
                        main_game.snake.direction = Vector2(0,-1)
                if event.key == pygame.K_RIGHT:
                    if main_game.snake.direction.x != -1:
                        main_game.snake.direction = Vector2(1,0)
                if event.key == pygame.K_DOWN:
                    if main_game.snake.direction.y != -1:
                        main_game.snake.direction = Vector2(0,1)
                if event.key == pygame.K_LEFT:
                    if main_game.snake.direction.x != 1:
                        main_game.snake.direction = Vector2(-1,0)

        screen.fill((175,215,70))
        main_game.draw_elements()
        pygame.display.update()
        clock.tick(60)
    
def options():
    volume_changed = False
    bgm_volume = sound_manager.bgm_volume
    sfx_volume = sound_manager.sfx_volume
    is_muted = sound_manager.muted
    
    # Play background music for testing sound levels
    if pygame.mixer.music.get_busy() == 0:
        sound_manager.play_bgm('bgm')
    
    # Create a test sound button for SFX testing
    test_sound = pygame.Rect(680, 350, 40, 40)
    
    # Add test buttons for specific sounds
    crunch_test_button = pygame.Rect(1000, 250, 40, 40)
    game_over_test_button = pygame.Rect(1000, 350, 40, 40)
    
    while True:
        OPTIONS_MOUSE_POS = pygame.mouse.get_pos()

        SCREEN.fill("white")
        
        OPTIONS_TEXT = get_font(45).render("SOUND OPTIONS", True, "Black")
        OPTIONS_RECT = OPTIONS_TEXT.get_rect(center=(640, 100))
        SCREEN.blit(OPTIONS_TEXT, OPTIONS_RECT)

        # BGM Volume slider
        BGM_TEXT = get_font(30).render(f"Music Volume: {int(bgm_volume * 100)}%", True, "Black")
        BGM_RECT = BGM_TEXT.get_rect(midleft=(300, 200))
        SCREEN.blit(BGM_TEXT, BGM_RECT)
        
        bgm_slider_bg = pygame.Rect(300, 250, 680, 20)
        pygame.draw.rect(SCREEN, "Gray", bgm_slider_bg)
        bgm_slider = pygame.Rect(300, 250, 680 * bgm_volume, 20)
        pygame.draw.rect(SCREEN, "#b68f40", bgm_slider)
        
        # SFX Volume slider
        SFX_TEXT = get_font(30).render(f"Effects Volume: {int(sfx_volume * 100)}%", True, "Black")
        SFX_RECT = SFX_TEXT.get_rect(midleft=(300, 300))
        SCREEN.blit(SFX_TEXT, SFX_RECT)
        
        sfx_slider_bg = pygame.Rect(300, 350, 680, 20)
        pygame.draw.rect(SCREEN, "Gray", sfx_slider_bg)
        sfx_slider = pygame.Rect(300, 350, 680 * sfx_volume, 20)
        pygame.draw.rect(SCREEN, "#b68f40", sfx_slider)
        
        # Draw test buttons for specific sounds
        pygame.draw.rect(SCREEN, "Green", test_sound)
        test_icon = get_font(20).render("►", True, "White")
        test_icon_rect = test_icon.get_rect(center=test_sound.center)
        SCREEN.blit(test_icon, test_icon_rect)
        
        # Crunch test button
        pygame.draw.rect(SCREEN, "Red", crunch_test_button)
        crunch_text = get_font(15).render("Eat", True, "White")
        crunch_rect = crunch_text.get_rect(center=crunch_test_button.center)
        SCREEN.blit(crunch_text, crunch_rect)
        
        # Game over test button
        pygame.draw.rect(SCREEN, "Blue", game_over_test_button)
        go_text = get_font(15).render("GO", True, "White")
        go_rect = go_text.get_rect(center=game_over_test_button.center)
        SCREEN.blit(go_text, go_rect)
        
        # Additional label for test buttons
        test_label = get_font(20).render("Test Sounds:", True, "Black")
        SCREEN.blit(test_label, (880, 200))
        
        # Mute button
        MUTE_BUTTON = Button(
            image=None, pos=(640, 450),
            text_input=("UNMUTE" if is_muted else "MUTE"), 
            font=get_font(40), base_color="Black", hovering_color="Green"
        )
        
        # Apply button
        APPLY_BUTTON = Button(
            image=None, pos=(500, 550),
            text_input="APPLY", font=get_font(40), base_color="Black", hovering_color="Green"
        )
        
        # Back button
        OPTIONS_BACK = Button(
            image=None, pos=(780, 550),
            text_input="BACK", font=get_font(40), base_color="Black", hovering_color="Green"
        )

        # Update buttons
        for button in [MUTE_BUTTON, APPLY_BUTTON, OPTIONS_BACK]:
            button.changeColor(OPTIONS_MOUSE_POS)
            button.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Handle BGM volume slider
                if bgm_slider_bg.collidepoint(OPTIONS_MOUSE_POS):
                    bgm_volume = (OPTIONS_MOUSE_POS[0] - 300) / 680
                    bgm_volume = max(0, min(1, bgm_volume))
                    volume_changed = True
                    # Apply BGM volume immediately
                    sound_manager.set_bgm_volume(bgm_volume)
                
                # Handle SFX volume slider
                if sfx_slider_bg.collidepoint(OPTIONS_MOUSE_POS):
                    sfx_volume = (OPTIONS_MOUSE_POS[0] - 300) / 680
                    sfx_volume = max(0, min(1, sfx_volume))
                    volume_changed = True
                    # Apply SFX volume immediately
                    sound_manager.set_sfx_volume(sfx_volume)
                    # Play a test sound to hear the new volume
                    sound_manager.play_sound('button_click')
                
                # Test sound button
                if test_sound.collidepoint(OPTIONS_MOUSE_POS):
                    sound_manager.play_sound('button_click')
                
                # Test specific sounds
                if crunch_test_button.collidepoint(OPTIONS_MOUSE_POS):
                    sound_manager.play_sound('eat')
                
                if game_over_test_button.collidepoint(OPTIONS_MOUSE_POS):
                    sound_manager.play_sound('game_over')
                
                # Mute button with immediate effect
                if MUTE_BUTTON.checkForInput(OPTIONS_MOUSE_POS):
                    is_muted = not is_muted
                    sound_manager.toggle_mute()
                    
                    # Update crunch sound volume in all existing snake instances
                    # This requires calling a global update function
                    sound_manager.update_game_sound_volumes()
                
                if APPLY_BUTTON.checkForInput(OPTIONS_MOUSE_POS):
                    # Save settings persistently
                    sound_manager.set_bgm_volume(bgm_volume)
                    sound_manager.set_sfx_volume(sfx_volume)
                    sound_manager.update_game_sound_volumes()
                    
                    if not is_muted:
                        sound_manager.play_sound('button_click')
                
                if OPTIONS_BACK.checkForInput(OPTIONS_MOUSE_POS):
                    if not is_muted:
                        sound_manager.play_sound('button_click')
                    main_menu()
            
            # Allow dragging sliders
            if event.type == pygame.MOUSEMOTION and pygame.mouse.get_pressed()[0]:
                if bgm_slider_bg.collidepoint(OPTIONS_MOUSE_POS):
                    bgm_volume = (OPTIONS_MOUSE_POS[0] - 300) / 680
                    bgm_volume = max(0, min(1, bgm_volume))
                    # Apply volume change in real-time for immediate feedback
                    sound_manager.set_bgm_volume(bgm_volume)
                    volume_changed = True
                
                if sfx_slider_bg.collidepoint(OPTIONS_MOUSE_POS):
                    sfx_volume = (OPTIONS_MOUSE_POS[0] - 300) / 680
                    sfx_volume = max(0, min(1, sfx_volume))
                    # Apply volume change in real-time for immediate feedback
                    sound_manager.set_sfx_volume(sfx_volume)
                    volume_changed = True
                    # Don't play test sound on every mouse movement to avoid spam

        pygame.display.update()

def show_high_score():
    try:
        # Try to get high scores from database
        scores = session.query(high_score).order_by(high_score.high_score.desc()).limit(10).all()
    except Exception as e:
        # Handle the cryptography package error
        scores = []
        error_msg = str(e)
        print(f"Database error: {error_msg}")

    while True:
        SCORE_MOUSE_POS = pygame.mouse.get_pos()
        SCREEN.blit(BG, (0, 0)) 

        SCORE_TEXT = get_font(45).render("HIGH SCORE", True, "#b68f40")
        SCORE_RECT = SCORE_TEXT.get_rect(center=(640, 100))
        SCREEN.blit(SCORE_TEXT, SCORE_RECT)

        # Show error message if there was a database error
        if not scores and 'cryptography' in str(error_msg).lower():
            error_text1 = get_font(25).render("ERROR: Cannot load high scores", True, "#ff4040")
            error_text2 = get_font(25).render("Install 'cryptography' package:", True, "#ff4040")
            error_text3 = get_font(25).render("pip install cryptography", True, "#ff4040")
            
            SCREEN.blit(error_text1, (400, 200))
            SCREEN.blit(error_text2, (400, 250))
            SCREEN.blit(error_text3, (400, 300))
        else:
            # Display high scores if available
            for i, record in enumerate(scores):
                monospaced_font = pygame.font.SysFont("Courier", 45)
                # Display: Rank | Score | Name
                name_text = monospaced_font.render(str(i + 1), True, "#d7fcd4")
                score_text = monospaced_font.render(str(record.high_score), True,"#d7fcd4")
                date_text = monospaced_font.render(str(record.name), True, "#d7fcd4")

                SCREEN.blit(name_text, (300, 150 + i * 50))    # Rank
                SCREEN.blit(score_text, (600, 150 + i * 50))   # Score
                SCREEN.blit(date_text, (900, 150 + i * 50))    # Name

        SCORE_BACK = Button(
            image=None, pos=(640, 700),
            text_input="BACK", font=get_font(55),
            base_color="Black", hovering_color="#b68f40"
        )
        SCORE_BACK.changeColor(SCORE_MOUSE_POS)
        SCORE_BACK.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if SCORE_BACK.checkForInput(SCORE_MOUSE_POS):
                    click_sound.play()
                    main_menu()

        pygame.display.update()  # ✅ Cập nhật màn hình


def main_menu():
    while True:
        SCREEN.blit(BG, (0, 0))

        MENU_MOUSE_POS = pygame.mouse.get_pos()

        MENU_TEXT = get_font(100).render("MAIN MENU", True, "#b68f40")
        MENU_RECT = MENU_TEXT.get_rect(center=(640, 100))

        PLAY_BUTTON = Button(image=pygame.image.load("assets/Play_Rect.png"), pos=(640, 250), 
                            text_input="PLAY", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
        OPTIONS_BUTTON = Button(image=pygame.image.load("assets/Options_Rect.png"), pos=(640, 400), 
                            text_input="OPTIONS", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
        QUIT_BUTTON = Button(image=pygame.image.load("assets/Quit_Rect.png"), pos=(640, 700), 
                            text_input="QUIT", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
        SCORE_BUTTON = Button(image=pygame.image.load("assets/HighScore_Rect.png"), pos=(640, 550),
                            text_input="HIGH SCORE", font=get_font(75), base_color="#d7fcd4", hovering_color="White")

        SCREEN.blit(MENU_TEXT, MENU_RECT)

        for button in [PLAY_BUTTON, OPTIONS_BUTTON, QUIT_BUTTON, SCORE_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(SCREEN)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    click_sound.play()
                    play()
                if OPTIONS_BUTTON.checkForInput(MENU_MOUSE_POS):
                    click_sound.play()
                    options()
                if SCORE_BUTTON.checkForInput(MENU_MOUSE_POS):
                    click_sound.play()
                    show_high_score()
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    click_sound.play()
                    pygame.time.delay(200)
                    pygame.quit()
                    sys.exit()
        pygame.display.update()
        
main_menu()
