# src/screens/gameover.py
import pygame
from src.database import update_score, get_leaderboard

def gameover_screen(screen, player_id, score):
    update_score(player_id, score)
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 28)
    small_font = pygame.font.SysFont("arial", 22)

    button_rect = pygame.Rect(300, 450, 200, 50)
    quit_rect = pygame.Rect(300, 520, 200, 50)

    while True:
        screen.fill((0, 0, 0))
        screen.blit(font.render("Game Over", True, (255, 0, 0)), (320, 60))
        screen.blit(font.render(f"Ваш счёт: {score}", True, (255, 255, 255)), (300, 120))

        screen.blit(small_font.render("Лидеры:", True, (255, 255, 255)), (330, 170))
        for i, (name, scr) in enumerate(get_leaderboard()):
            screen.blit(small_font.render(f"{i+1}. {name[:10]} — {scr}", True, (200, 200, 200)), (280, 200 + i * 30))

        pygame.draw.rect(screen, (0, 128, 0), button_rect)
        pygame.draw.rect(screen, (128, 0, 0), quit_rect)
        screen.blit(small_font.render("Играть заново", True, (255, 255, 255)), (button_rect.x + 35, button_rect.y + 15))
        screen.blit(small_font.render("Выйти", True, (255, 255, 255)), (quit_rect.x + 75, quit_rect.y + 15))

        pygame.display.flip()
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    return True
                elif quit_rect.collidepoint(event.pos):
                    return False
