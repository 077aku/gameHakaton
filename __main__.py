import pygame
from src.database import init_db
from src.registration import registration_screen
from src.game import Game

if __name__ == "__main__":
    pygame.init()
    init_db()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Geeks Invaders - Registration")
    player_id = registration_screen(screen)
    game = Game(player_id)
    game.run()
