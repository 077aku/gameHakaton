import pygame
from src.database import get_connection

_font = None  # внутренний кэш для шрифта

def draw_text(screen, text, x, y, color=(0, 0, 0)):
    global _font
    if _font is None:
        _font = pygame.font.SysFont("arial", 24)
    label = _font.render(text, True, color)
    screen.blit(label, (x, y))

def registration_screen(screen):
    name = ""
    phone = ""
    input_active = "name"
    clock = pygame.time.Clock()

    while True:
        screen.fill((255, 255, 255))
        draw_text(screen, "Enter Your Name:", 250, 150)
        draw_text(screen, name, 260, 210)
        draw_text(screen, "Enter Phone Number:", 250, 270)
        draw_text(screen, phone, 260, 330)
        draw_text(screen, "Press ENTER to start", 250, 400, (128, 0, 0))

        pygame.display.flip()
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN:
                if input_active == "name":
                    if event.key == pygame.K_RETURN:
                        input_active = "phone"
                    elif event.key == pygame.K_BACKSPACE:
                        name = name[:-1]
                    else:
                        name += event.unicode
                elif input_active == "phone":
                    if event.key == pygame.K_RETURN:
                        if name.strip() and phone.strip():
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
