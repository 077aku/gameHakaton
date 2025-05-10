import pygame
import random
import math
from src.database import update_score
from src import player_progress

WIDTH, HEIGHT = 800, 600
WHITE, BLACK = (255, 255, 255), (0, 0, 0)

ASSETS = {
    "player": "assets/player.png",
    "enemy": "assets/enemy.png",
    "boss": "assets/boss.png",
    "shoot": "assets/shoot.wav",
    "explosion": "assets/explosion.wav",
    "bg_music": "assets/background_music.mp3",
    "game_over": "assets/game_over.wav",
    "powerup": "assets/powerup.png",
    "powerup2": "assets/powerup2.png",
    "powerup3": "assets/powerup3.png",
    "background": "assets/background.png",
    'explosion_anim': "assets/explosion_anim.png",
    'shield_effect':'assets/shield_effect.png',
    'multi_effect':'assets/multi_effect.png',
    'life_effect':'assets/life_effect.png',
    'sparkle':'assets/sparkle.png',
    'bonus_sound':'assets/bonus_sound.wav',
    'bullet_image':'assets/bullet_image.png',
    'menu_bonus':'assets/menu_bonus.png',
}

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.transform.scale(pygame.image.load(ASSETS["player"]), (80, 60))
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT - 50))
        self.speed = 5
        self.lives = 3
        self.shield = False
        self.multi_shot = False
        self.shield_end_time = 0
        self.multi_shot_end_time = 0
        self.lives_flash_timer = 0
        self.shield_effect_angle = 0
        self.multi_effect_flash = True

    def update(self, keys):
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed

        current_time = pygame.time.get_ticks()
        if self.shield and current_time > self.shield_end_time:
            self.shield = False
        if self.multi_shot and current_time > self.multi_shot_end_time:
            self.multi_shot = False
        if self.lives_flash_timer > 0:
            self.lives_flash_timer -= 1
            if self.lives_flash_timer % 10 < 5:
                self.image.set_alpha(100)
            else:
                self.image.set_alpha(255)
        else:
            self.image.set_alpha(255)
    def draw_effects(self, surface):
        if self.shield:
            self.shield_effect_angle += 5
            radius = max(self.rect.width, self.rect.height) // 2 + 10
            alpha_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(alpha_surface, (0, 150, 255, 100), (radius, radius), radius)
            rotated = pygame.transform.rotate(alpha_surface, self.shield_effect_angle)
            new_rect = rotated.get_rect(center=self.rect.center)
            surface.blit(rotated, new_rect.topleft)

        if self.multi_shot:
            self.multi_effect_flash = not self.multi_effect_flash
            if self.multi_effect_flash:
                radius = max(self.rect.width, self.rect.height) // 2 + 6
                pygame.draw.circle(surface, (255, 50, 50), self.rect.center, radius, 2)



class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.transform.scale(pygame.image.load(ASSETS["enemy"]), (80, 60))
        self.rect = self.image.get_rect(center=(random.randint(40, WIDTH - 40), random.randint(-100, -40)))
        self.speed = random.randint(2, 4)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()

class Boss(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.transform.scale(pygame.image.load(ASSETS["boss"]), (160, 120))
        self.rect = self.image.get_rect(center=(WIDTH // 2, -100))
        self.speed = 1
        self.hp = 20
        self.direction = 1
        self.shoot_timer = 0

    def update(self):
        if self.rect.top < 50:
            self.rect.y += self.speed
        else:
            self.rect.x += self.direction * self.speed
            if self.rect.left <= 0 or self.rect.right >= WIDTH:
                self.direction *= -1

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed=-8):
        super().__init__()
        # Заменяем простую заливку на изображение
        self.image = pygame.image.load(ASSETS["bullet_image"]).convert_alpha()  # Замените на путь к изображению пули
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0 or self.rect.top > HEIGHT:
            self.kill()


class PowerUp(pygame.sprite.Sprite):
    EFFECTS = [
        ("shield", ASSETS["powerup"]),
        ("multi", ASSETS["powerup2"]),
        ("life", ASSETS["powerup3"])
    ]

    def __init__(self, effect_name, image_path):
        super().__init__()
        self.effect = effect_name
        self.image = pygame.transform.scale(pygame.image.load(image_path), (40, 40))
        self.rect = self.image.get_rect(center=(random.randint(50, WIDTH - 50), -40))
        self.speed = 3

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()

class FloatingText(pygame.sprite.Sprite):
    def __init__(self, text, x, y, color=(255, 255, 0), lifespan=60):
        super().__init__()
        self.font = pygame.font.Font("assets/emulogic.ttf", 12)
        self.image = self.font.render(text, True, color)
        self.rect = self.image.get_rect(center=(x, y))
        self.lifespan = lifespan

    def update(self):
        self.rect.y -= 1
        self.lifespan -= 1
        if self.lifespan <= 0:
            self.kill()

class GameplayScreen:
    def __init__(self, screen, player_id):
        self.screen = screen
        self.player_id = player_id
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font("assets/emulogic.ttf", 12)
        self.effects = pygame.sprite.Group()

        # Загружаем две копии фона
        self.background1 = pygame.transform.scale(pygame.image.load(ASSETS["background"]), (WIDTH, HEIGHT))
        self.background2 = self.background1.copy()

        # Начальные позиции фонов
        self.bg1_y = 0
        self.bg2_y = -HEIGHT

        self.player = Player()
        self.progress = player_progress.load_progress()

        # Применяем апгрейды к игроку
        self.player.lives += self.progress["upgrades"]["extra_life"]
        if random.randint(1, 100) <= self.progress["upgrades"]["shield_chance"]:
            self.player.shield = True
            self.player.shield_end_time = pygame.time.get_ticks() + 5000
        if random.randint(1, 100) <= self.progress["upgrades"]["multi_shot_chance"]:
            self.player.multi_shot = True
            self.player.multi_shot_end_time = pygame.time.get_ticks() + 5000

        self.all_sprites = pygame.sprite.Group(self.player)
        self.enemies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.bosses = pygame.sprite.Group()
        self.floating_texts = pygame.sprite.Group()

        self.shoot_sound = pygame.mixer.Sound(ASSETS["shoot"])
        self.explosion_sound = pygame.mixer.Sound(ASSETS["explosion"])
        self.game_over_sound = pygame.mixer.Sound(ASSETS["game_over"])
        pygame.mixer.music.load(ASSETS["bg_music"])
        pygame.mixer.music.play(-1)

        self.space_pressed = False
        self.spawn_timer = 0
        self.powerup_timer = 0
        self.level = 1
        self.score = 0
        self.pause = False
        self.boss_spawned = False
        self.level_transition_timer = 0

    def run(self):
        running = True
        while running:
            self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return self.score
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        self.pause = not self.pause

            if self.pause:
                self.draw_pause()
                continue

            keys = pygame.key.get_pressed()

            for sprite in self.all_sprites:
                if isinstance(sprite, Player):
                    sprite.update(keys)
                else:
                    sprite.update()
            self.floating_texts.update()
            self.effects.update()

            if keys[pygame.K_SPACE] and not self.space_pressed:
                self.fire()
                self.space_pressed = True
            if not keys[pygame.K_SPACE]:
                self.space_pressed = False

            self.spawn_timer += 1
            if self.spawn_timer > max(30 - self.level * 2, 10):
                enemy = Enemy()
                self.all_sprites.add(enemy)
                self.enemies.add(enemy)
                self.spawn_timer = 0

            if self.score // 10 + 1 > self.level:
                self.level += 1
                self.boss_spawned = False
                self.level_transition_timer = 120

            if self.level % 5 == 0 and not self.boss_spawned:
                boss = Boss()
                self.all_sprites.add(boss)
                self.bosses.add(boss)
                self.boss_spawned = True

            self.powerup_timer += 1
            if self.powerup_timer > 600:
                effect_name, image_path = random.choice(PowerUp.EFFECTS)
                p = PowerUp(effect_name, image_path)
                self.all_sprites.add(p)
                self.powerups.add(p)

                spark = AnimatedSprite(ASSETS["sparkle"], 32, 32, 4, p.rect.center, scale=1.5, lifespan=20)
                self.all_sprites.add(spark)

                self.powerup_timer = 0

            # Обработка фонов
            self.bg1_y += 1
            self.bg2_y += 1

            if self.bg1_y >= HEIGHT:
                self.bg1_y = -HEIGHT
            if self.bg2_y >= HEIGHT:
                self.bg2_y = -HEIGHT

            # Отображение фонов
            self.screen.blit(self.background1, (0, self.bg1_y))
            self.screen.blit(self.background2, (0, self.bg2_y))

            for bullet in self.bullets:
                hit_enemy = pygame.sprite.spritecollideany(bullet, self.enemies)
                if hit_enemy:
                    bullet.kill()
                    hit_enemy.kill()
                    self.score += 1
                    self.explosion_sound.play()
                    expl = AnimatedSprite(ASSETS["explosion_anim"], 64, 64, 4 , hit_enemy.rect.center)
                    self.all_sprites.add(expl)
                    self.floating_texts.add(FloatingText("+1", hit_enemy.rect.centerx, hit_enemy.rect.centery))

                for boss in self.bosses:
                    if bullet.rect.colliderect(boss.rect):
                        bullet.kill()
                        boss.hp -= 1
                        if boss.hp <= 0:
                            boss.kill()
                            self.score += 20
                            self.boss_spawned = False
                            ft = FloatingText("+20", boss.rect.centerx, boss.rect.centery)
                            self.floating_texts.add(ft)

            for enemy in self.enemies:
                if self.player.rect.colliderect(enemy.rect):
                    enemy.kill()
                    if not self.player.shield:
                        self.player.lives -= 1
                        if self.player.lives <= 0:
                            return self.score

            for p in pygame.sprite.spritecollide(self.player, self.powerups, True):
                current_time = pygame.time.get_ticks()
                effect = None
                if p.effect == "shield":
                    self.player.shield = True
                    self.player.shield_end_time = current_time + 5000
                    effect = BonusEffect("shield", self.player.rect)
                    ft = FloatingText("Shield Activated!", self.player.rect.centerx, self.player.rect.top - 10)
                elif p.effect == "multi":
                    self.player.multi_shot = True
                    self.player.multi_shot_end_time = current_time + 5000
                    effect = BonusEffect("multi", self.player.rect)
                    ft = FloatingText("Multi Shot!", self.player.rect.centerx, self.player.rect.top - 10)
                elif p.effect == "life":
                    self.player.lives += 1
                    effect = BonusEffect("life", self.player.rect)
                    ft = FloatingText("+1 Life", self.player.rect.centerx, self.player.rect.top - 10)

                if effect:
                    self.effects.add(effect)
                self.floating_texts.add(ft)

            for boss in self.bosses:
                boss.shoot_timer += 1
                if boss.shoot_timer > 120:
                    bullet = Bullet(boss.rect.centerx, boss.rect.bottom, speed=5)
                    self.all_sprites.add(bullet)
                    self.enemy_bullets.add(bullet)
                    boss.shoot_timer = 0

            for bullet in self.enemy_bullets:
                if self.player.rect.colliderect(bullet.rect):
                    bullet.kill()
                    if not self.player.shield:
                        self.player.lives -= 1
                        ft = FloatingText("-1", bullet.rect.centerx, bullet.rect.centery, color=(255, 0, 0))
                        self.floating_texts.add(ft)
                        if self.player.lives <= 0:
                            player_progress.add_xp(self.score)
                            return self.score

            self.all_sprites.draw(self.screen)
            self.effects.draw(self.screen)
            self.floating_texts.draw(self.screen)
            self.draw_ui()

            if self.level_transition_timer > 0:
                self.draw_level_transition()

                if self.level_transition_timer == 3:
                    # Показываем окно прокачки перед началом нового уровня
                    upgrade = UpgradeScreen(self.screen, self.progress)
                    upgrade.run()

                self.level_transition_timer -= 1

            pygame.display.flip()

    def fire(self):
        self.shoot_sound.play()
        if self.player.multi_shot:
            for offset in [-20, 0, 20]:
                bullet = Bullet(self.player.rect.centerx + offset, self.player.rect.top)
                self.bullets.add(bullet)
                self.all_sprites.add(bullet)
        else:
            bullet = Bullet(self.player.rect.centerx, self.player.rect.top)
            self.bullets.add(bullet)
            self.all_sprites.add(bullet)

    def draw_ui(self):
        lives_text = self.font.render(f"Lives: {self.player.lives}", True, WHITE)
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        level_text = self.font.render(f"Level: {self.level}", True, WHITE)
        self.screen.blit(lives_text, (10, 10))
        self.screen.blit(score_text, (10, 40))
        self.screen.blit(level_text, (10, 70))

    def draw_pause(self):
        pause_text = self.font.render("Paused - Press 'P' to resume", True, WHITE)
        self.screen.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 2))
        pygame.display.flip()

    def draw_level_transition(self):
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        text = self.font.render(f"Level {self.level}", True, WHITE)
        self.screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 20))


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, spritesheet_path, frame_width, frame_height, frames, pos, scale=1, lifespan=None):
        super().__init__()
        self.spritesheet = pygame.image.load(spritesheet_path).convert_alpha()
        self.frames = []
        for i in range(frames):
            frame = self.spritesheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
            if scale != 1:
                frame = pygame.transform.scale(frame, (int(frame_width * scale), int(frame_height * scale)))
            self.frames.append(frame)
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=pos)
        self.index = 0
        self.frame_delay = 5
        self.counter = 0
        self.lifespan = lifespan

    def update(self):
        self.counter += 1
        if self.counter >= self.frame_delay:
            self.counter = 0
            self.index += 1
            if self.index >= len(self.frames):
                self.kill()
            else:
                self.image = self.frames[self.index]
        if self.lifespan:
            self.lifespan -= 1
            if self.lifespan <= 0:
                self.kill()

class BonusEffect(pygame.sprite.Sprite):
    def __init__(self, effect_type, target_rect, duration=60):
        super().__init__()
        self.effect_type = effect_type


        if effect_type == "shield":
            self.image = pygame.transform.scale(pygame.image.load(ASSETS["shield_effect"]), (90, 70))
            self.sound = pygame.mixer.Sound(ASSETS["bonus_sound"])
        elif effect_type == "multi":
            self.image = pygame.transform.scale(pygame.image.load(ASSETS["multi_effect"]), (90, 70))
            self.sound = pygame.mixer.Sound(ASSETS["bonus_sound"])
        elif effect_type == "life":
            self.image = pygame.transform.scale(pygame.image.load(ASSETS["life_effect"]), (50, 50))
            self.sound = pygame.mixer.Sound(ASSETS["bonus_sound"])
        else:
            self.image = pygame.Surface((1, 1))
            self.sound = None
        self.rect = self.image.get_rect(center=target_rect.center)
        self.timer = duration

        if self.sound:
            self.sound.play()

    def update(self):
        self.timer -= 1
        if self.timer <= 0:
            self.kill()




class UpgradeScreen:
    def __init__(self, screen, player_progress):
        self.screen = screen
        self.font = pygame.font.Font("assets/emulogic.ttf", 15)
        self.selected = 0
        self.options = [
            {"name": "Shield Chance +10%", "key": "shield_chance"},
            {"name": "Multi-Shot Chance +10%", "key": "multi_shot_chance"},
            {"name": "Extra Life", "key": "extra_life"},
        ]
        self.player_progress = player_progress

        # Фон масштабирован под экран
        self.background = pygame.transform.scale(
            pygame.image.load("assets/menu_bonus.png"), (WIDTH, HEIGHT)
        )

        # Центры текстов для попадания в чёрные поля на фоне
        self.text_positions = [
            (WIDTH // 2 -40, 250),   # Shield
            (WIDTH // 2 -35, 370),   # Multi-Shot
            (WIDTH // 2 -40, 490),   # Extra Life
        ]

    def run(self):
        running = True
        while running:
            self.screen.blit(self.background, (0, 0))

            for i, option in enumerate(self.options):
                color = (255, 255, 0) if i == self.selected else (255, 255, 255)
                text = self.font.render(option["name"], True, color)
                text_x, text_y = self.text_positions[i]
                self.screen.blit(text, (text_x - text.get_width() // 2, text_y))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.selected = (self.selected - 1) % len(self.options)
                    if event.key == pygame.K_DOWN:
                        self.selected = (self.selected + 1) % len(self.options)
                    if event.key == pygame.K_RETURN:
                        selected_upgrade = self.options[self.selected]["key"]
                        self.player_progress["upgrades"][selected_upgrade] += 1
                        player_progress.save_progress(self.player_progress)
                        return
