import pygame
import random
from src.database import update_score, get_leaderboard

WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
FPS = 60

LOGO_PATH = "assets/geeks_logo.png"
PLAYER_IMAGE_PATH = "assets/player.png"
ENEMY_IMAGE_PATH = "assets/enemy.png"
BACKGROUND_IMAGE_PATH = "assets/background.jpg"
BACKGROUND_MUSIC_PATH = "assets/background_music.mp3"

pygame.mixer.init()
try:
    shoot_sound = pygame.mixer.Sound("assets/shoot.wav")
    explosion_sound = pygame.mixer.Sound("assets/explosion.wav")
    game_over_sound = pygame.mixer.Sound("assets/game_over.wav")
except pygame.error as e:
    print(f"Error loading sound files: {e}")

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load(PLAYER_IMAGE_PATH)
        self.image = pygame.transform.scale(self.image, (80, 60))
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT - 50))
        self.speed = 5

    def update(self, keys):
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load(ENEMY_IMAGE_PATH)
        self.image = pygame.transform.scale(self.image, (120, 100))
        self.rect = self.image.get_rect(center=(random.randint(20, WIDTH - 20), random.randint(-100, -40)))
        self.speed = random.randint(2, 5)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 10))
        self.image.fill(BLACK)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = -7

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()

class Game:
    def __init__(self, player_id):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Geeks Invaders")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 20)
        self.player_id = player_id

        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()

        self.player = Player()
        self.all_sprites.add(self.player)

        self.score = 0
        self.spawn_timer = 0
        self.score_saved = False
        self.game_over_sound_played = False

        self.space_pressed = False  # <-- добавлено

        self.logo = pygame.image.load(LOGO_PATH)
        self.logo = pygame.transform.scale(self.logo, (90, 90))
        self.logo_rect = self.logo.get_rect(topleft=(10, 10))

        self.background = pygame.image.load(BACKGROUND_IMAGE_PATH)
        self.background = pygame.transform.scale(self.background, (WIDTH, HEIGHT))

        try:
            pygame.mixer.music.load(BACKGROUND_MUSIC_PATH)
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)
        except pygame.error as e:
            print(f"Ошибка загрузки фоновой музыки: {e}")

    def run(self):
        running = True
        game_over = False

        while running:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            if not game_over:
                keys = pygame.key.get_pressed()

                for sprite in self.all_sprites:
                    if isinstance(sprite, Player):
                        sprite.update(keys)
                    else:
                        sprite.update()

                self.spawn_timer += 1
                if self.spawn_timer > 30:
                    enemy = Enemy()
                    self.all_sprites.add(enemy)
                    self.enemies.add(enemy)
                    self.spawn_timer = 0

                # ОБНОВЛЁННЫЙ БЛОК СТРЕЛЬБЫ
                if keys[pygame.K_SPACE]:
                    if not self.space_pressed:
                        bullet = Bullet(self.player.rect.centerx, self.player.rect.top)
                        self.all_sprites.add(bullet)
                        self.bullets.add(bullet)
                        shoot_sound.play()
                        self.space_pressed = True
                else:
                    self.space_pressed = False

                for bullet in self.bullets:
                    hit_enemy = pygame.sprite.spritecollideany(bullet, self.enemies)
                    if hit_enemy:
                        hit_enemy.kill()
                        bullet.kill()
                        self.score += 1
                        explosion_sound.play()

                for enemy in self.enemies:
                    if self.player.rect.inflate(-40, -20).colliderect(enemy.rect.inflate(-40, -20)):
                        game_over = True
                        break

            else:
                if not self.score_saved:
                    update_score(self.player_id, self.score)
                    self.score_saved = True

                    if not self.game_over_sound_played:
                        pygame.mixer.music.stop()
                        game_over_sound.play()
                        self.game_over_sound_played = True

                    self.show_leaderboard_screen()
                    return

            self.screen.blit(self.background, (0, 0))
            self.screen.blit(self.logo, self.logo_rect)
            self.all_sprites.draw(self.screen)
            self.draw_ui()

            pygame.display.flip()

        pygame.quit()

    def draw_ui(self):
        score_text = self.font.render(f"Score: {self.score}", True, BLACK)
        score_rect = score_text.get_rect(topright=(WIDTH - 10, 10))
        self.screen.blit(score_text, score_rect)

    def show_leaderboard_screen(self):
        button_font = pygame.font.SysFont("arial", 28)
        button_text = button_font.render("Начать заново", True, WHITE)
        button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT - 100, 200, 50)

        showing = True
        while showing:
            self.screen.blit(self.background, (0, 0))

            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))

            title = button_font.render("Game Over", True, WHITE)
            title_rect = title.get_rect(center=(WIDTH // 2, 80))
            self.screen.blit(title, title_rect)

            leaderboard = get_leaderboard()
            self.screen.blit(self.font.render("Leaderboard:", True, WHITE), (WIDTH // 2 - 80, 140))
            for i, (name, score) in enumerate(leaderboard[:5]):
                entry = f"{i + 1}. {name[:10]}: {score}"
                text_surface = self.font.render(entry, True, WHITE)
                self.screen.blit(text_surface, (WIDTH // 2 - 80, 170 + i * 30))

            pygame.draw.rect(self.screen, (70, 130, 180), button_rect, border_radius=10)
            self.screen.blit(button_text, button_text.get_rect(center=button_rect.center))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    showing = False
                    pygame.quit()
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN and button_rect.collidepoint(event.pos):
                    self.reset_game()
                    return

    def reset_game(self):
        self.__init__(self.player_id)
        self.run()
