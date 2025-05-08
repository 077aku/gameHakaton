# src/screens/registration.py
import pygame
from src.database import get_connection

def draw_text(screen, text, x, y, color=(0, 0, 0), font_size=28):
    font = pygame.font.SysFont("arial", font_size)
    label = font.render(text, True, color)
    screen.blit(label, (x, y))

def registration_screen(screen):
    name, phone = "", ""
    input_mode = "name"
    clock = pygame.time.Clock()

    while True:
        screen.fill((255, 255, 255))
        draw_text(screen, "Введите имя:", 250, 150)
        draw_text(screen, name, 260, 190)
        draw_text(screen, "Введите телефон:", 250, 240)
        draw_text(screen, phone, 260, 280)
        draw_text(screen, "Нажмите ENTER чтобы начать", 180, 350, (0, 128, 0), 24)

        pygame.display.flip()
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); exit()
            if event.type == pygame.KEYDOWN:
                if input_mode == "name":
                    if event.key == pygame.K_RETURN:
                        input_mode = "phone"
                    elif event.key == pygame.K_BACKSPACE:
                        name = name[:-1]
                    else:
                        name += event.unicode
                elif input_mode == "phone":
                    if event.key == pygame.K_RETURN:
                        if name and phone:
                            conn = get_connection()
                            cursor = conn.cursor()
                            cursor.execute("INSERT INTO players (name, phone) VALUES (?, ?)", (name, phone))
                            conn.commit()
                            return cursor.lastrowid
                    elif event.key == pygame.K_BACKSPACE:
                        phone = phone[:-1]
                    else:
                        if event.unicode.isdigit():
                            phone += event.unicode
