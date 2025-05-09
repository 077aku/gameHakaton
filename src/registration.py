import pygame
from src.database import get_connection

def registration_screen(screen):
    pygame.font.init()
    background = pygame.image.load("assets/menu.png").convert()
    font = pygame.font.Font("assets/emulogic.ttf", 12)

    name = ""
    phone = ""
    input_active = "name"

    # Точные координаты с картинки
    name_rect = pygame.Rect(276, 286, 305, 28)
    phone_rect = pygame.Rect(276, 341, 305, 28)
    go_button_rect = pygame.Rect(210, 370, 400, 60)

    clock = pygame.time.Clock()

    while True:
        screen.blit(background, (0, 0))

        # Рисуем текст поверх полей
        text_name = font.render(name, True, (255, 255, 255))
        text_phone = font.render(phone, True, (255, 255, 255))
        screen.blit(text_name, (name_rect.x + 10, name_rect.y + 5))
        screen.blit(text_phone, (phone_rect.x + 10, phone_rect.y + 5))

        pygame.display.flip()
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if name_rect.collidepoint(event.pos):
                    input_active = "name"
                elif phone_rect.collidepoint(event.pos):
                    input_active = "phone"
                elif go_button_rect.collidepoint(event.pos):
                    if name.strip() and phone.strip():
                        conn = get_connection()
                        cursor = conn.cursor()
                        cursor.execute("INSERT INTO players (name, phone) VALUES (?, ?)", (name, phone))
                        conn.commit()
                        return cursor.lastrowid

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if input_active == "name":
                        input_active = "phone"
                    elif input_active == "phone":
                        if name.strip() and phone.strip():
                            conn = get_connection()
                            cursor = conn.cursor()
                            cursor.execute("INSERT INTO players (name, phone) VALUES (?, ?)", (name, phone))
                            conn.commit()
                            return cursor.lastrowid

                elif input_active == "name":
                    if event.key == pygame.K_BACKSPACE:
                        name = name[:-1]
                    elif len(name) < 20 and event.unicode.isprintable():
                        name += event.unicode.upper()

                elif input_active == "phone":
                    if event.key == pygame.K_BACKSPACE:
                        phone = phone[:-1]
                    elif event.unicode.isdigit() and len(phone) < 15:
                        phone += event.unicode