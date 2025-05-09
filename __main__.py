# __main__.py
import pygame
from src.core import GameManager

if __name__ == "__main__":
    pygame.init()
    pygame.mixer.init()
    manager = GameManager()
    manager.run()
