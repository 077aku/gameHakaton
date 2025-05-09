# src/core.py
import pygame
from src.database import init_db, close_db
from src.registration import registration_screen
from src.screens.gameplay import GameplayScreen
from src.screens.gameover import gameover_screen

class GameManager:
    def __init__(self):
        init_db()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Geeks Invaders")

    def run(self):
        player_id = registration_screen(self.screen)
        while True:
            score = GameplayScreen(self.screen, player_id).run()
            if not gameover_screen(self.screen, player_id, score):
                break
        close_db()
        pygame.quit()
