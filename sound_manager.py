import pygame
import os

class SoundManager:
    def __init__(self):
        pygame.mixer.init()
        self.sounds = {}
        self.current_bgm = None
        self.bgm_volume = 0.5
        self.sfx_volume = 0.7
        self.muted = False
        
        # Default sound paths (adjust these to match your files)
        self.sound_files = {
            'eat': 'Sound/crunch.wav',
            'game_over': 'Sound/game_over.wav',
            'button_click': 'Sound/button_click.wav',
            'bgm': 'Sound/bgm.mp3'
        }
        
        # Load all sounds
        self.load_sounds()
    
    def load_sounds(self):
        """Load all sound files"""
        for name, path in self.sound_files.items():
            try:
                if name == 'bgm':
                    # Background music is handled differently
                    continue
                else:
                    self.sounds[name] = pygame.mixer.Sound(path)
                    self.sounds[name].set_volume(self.sfx_volume)
            except Exception as e:
                print(f"Failed to load sound {name}: {e}")
                # Create empty sound as fallback
                self.sounds[name] = pygame.mixer.Sound(buffer=bytearray(100))
    
    def play_sound(self, name, loops=0):
        """Play a sound effect"""
        if not self.muted and name in self.sounds:
            self.sounds[name].play(loops=loops)
    
    def play_bgm(self, name='bgm'):
        """Play background music"""
        if not self.muted and name in self.sound_files:
            try:
                pygame.mixer.music.load(self.sound_files[name])
                pygame.mixer.music.set_volume(self.bgm_volume)
                pygame.mixer.music.play(-1)  # Loop indefinitely
                self.current_bgm = name
            except Exception as e:
                print(f"Failed to play background music: {e}")
    
    def stop_bgm(self):
        """Stop background music"""
        pygame.mixer.music.stop()
        self.current_bgm = None
    
    def set_bgm_volume(self, volume):
        """Set background music volume (0.0 to 1.0)"""
        self.bgm_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.bgm_volume)
    
    def set_sfx_volume(self, volume):
        """Set sound effects volume (0.0 to 1.0)"""
        self.sfx_volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(self.sfx_volume)
    
    def toggle_mute(self):
        """Toggle mute state"""
        self.muted = not self.muted
        if self.muted:
            pygame.mixer.music.set_volume(0)
            for sound in self.sounds.values():
                sound.set_volume(0)
        else:
            pygame.mixer.music.set_volume(self.bgm_volume)
            for sound in self.sounds.values():
                sound.set_volume(self.sfx_volume)
    
    def stop_all(self):
        """Stop all sounds and music"""
        pygame.mixer.music.stop()
        for sound in self.sounds.values():
            sound.stop()