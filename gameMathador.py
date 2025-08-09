import pygame
import random
import os
import tkinter as tk
import sys
import threading

# ---------------- Constants ----------------
SCREEN_WIDTH, SCREEN_HEIGHT = 1024, 768
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ORANGE = (252, 178, 80)
BLUE = (70, 197, 252)
PLAYER_SPEED = 5
BASE_ENEMY_SPEED = 1

try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    current_dir = os.getcwd()

ASSET_FILE_PATH = os.path.join(current_dir, "assets", "shooter")


# ---------------- Explosion ----------------
class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.frames = []
        for radius in range(10, 60, 10):
            frame_surf = pygame.Surface((60, 60), pygame.SRCALPHA)
            pygame.draw.circle(frame_surf, (255, 100, 0), (30, 30), radius)
            self.frames.append(frame_surf)
        self.index = 0
        self.image = self.frames[self.index]
        self.rect = self.image.get_rect(center=(x, y))
        self.animation_speed = 5

    def update(self):
        self.index += 0.2 * self.animation_speed
        if self.index >= len(self.frames):
            self.kill()
        else:
            self.image = self.frames[int(self.index)]


# ---------------- Bullet ----------------
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, weapon_type, amount):
        super().__init__()
        self.image = pygame.Surface((5, 10))
        # Choose color based on weapon type
        if weapon_type == 'decrease':
            self.image.fill((0, 135, 71))  # Greenish
        else:
            self.image.fill((255, 165, 0))  # Orange
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed
        self.weapon_type = weapon_type
        self.amount = amount  # how many points to add/subtract

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT:
            self.kill()


# ---------------- Player ----------------
class Player(pygame.sprite.Sprite):
    def __init__(self, game):
        super().__init__()
        self.game = game
        # Load animation frames
        self.frames = []
        for i in range(1, 3):
            frame_path = os.path.join(ASSET_FILE_PATH, f"player_{i}.png")
            frame = pygame.image.load(frame_path)
            self.frames.append(frame)

        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        self.health = 3

        self.animation_speed = 5  # lower => faster loop
        self.animation_counter = 0

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += PLAYER_SPEED
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= PLAYER_SPEED
        if keys[pygame.K_DOWN] and self.rect.bottom < SCREEN_HEIGHT:
            self.rect.y += PLAYER_SPEED

        # Animate
        self.animation_counter += 1
        if self.animation_counter >= self.animation_speed:
            self.animation_counter = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.image = self.frames[self.frame_index]

    def shoot(self, weapon_type, amount=1):
        if self.game.shoot_sound:
            self.game.shoot_sound.play()
        bullet = Bullet(self.rect.centerx, self.rect.top, -5, weapon_type, amount)
        self.game.all_sprites.add(bullet)
        self.game.bullets.add(bullet)


# ---------------- Enemy ----------------
class Enemy(pygame.sprite.Sprite):
    def __init__(self, game, speed, x, y):
        super().__init__()
        self.game = game
        self.width = 120
        self.height = 40
        self.image = pygame.Surface((self.width, self.height))

        self.color_left = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
        self.color_middle = (255, 0, 0)
        self.color_right = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))

        self.shield_x = random.randint(1, 10)
        self.shield_y = random.randint(1, 10)
        self.cockpit_value = random.randint(2, 20)
        while self.cockpit_value == self.shield_x + self.shield_y:
            self.cockpit_value = random.randint(2, 20)

        # Draw sections
        pygame.draw.rect(self.image, self.color_left, (0, 0, self.width // 3, self.height))
        pygame.draw.rect(self.image, self.color_middle, (self.width // 3, 0, self.width // 3, self.height))
        pygame.draw.rect(self.image, self.color_right, (2 * self.width // 3, 0, self.width // 3, self.height))
        # Outlines
        pygame.draw.rect(self.image, BLACK, (0, 0, self.width // 3, self.height), 2)
        pygame.draw.rect(self.image, BLACK, (self.width // 3, 0, self.width // 3, self.height), 2)
        pygame.draw.rect(self.image, BLACK, (2 * self.width // 3, 0, self.width // 3, self.height), 2)

        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = speed
        self.font = pygame.font.Font(None, 24)

    def update(self):
        dt = self.game.clock.get_time()  # ms since last frame
        self.rect.y += self.speed * dt * 0.05
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

    def hit(self, weapon_type, hit_x, amount):
        left_boundary = self.rect.left + self.width // 3
        right_boundary = self.rect.left + 2 * self.width // 3

        if hit_x < left_boundary:
            if weapon_type == 'decrease':
                self.shield_x -= amount
            else:
                self.shield_x += amount
        elif hit_x < right_boundary:
            if weapon_type == 'decrease':
                self.cockpit_value -= amount
            else:
                self.cockpit_value += amount
        else:
            if weapon_type == 'decrease':
                self.shield_y -= amount
            else:
                self.shield_y += amount

        # Check if destroyed
        if self.shield_x + self.shield_y == self.cockpit_value:
            explosion = Explosion(self.rect.centerx, self.rect.centery)
            self.game.all_sprites.add(explosion)
            self.game.explosions.add(explosion)
            if self.game.explosion_sound:
                self.game.explosion_sound.play()
            self.game.score += 10
            self.kill()

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        x_text = self.font.render(f"{self.shield_x}", True, BLACK)
        c_text = self.font.render(f"{self.cockpit_value}", True, BLACK)
        y_text = self.font.render(f"{self.shield_y}", True, BLACK)
        surface.blit(x_text, (self.rect.x + 15, self.rect.y + 10))
        surface.blit(c_text, (self.rect.centerx - 10, self.rect.y + 10))
        surface.blit(y_text, (self.rect.right - 35, self.rect.y + 10))


# ---------------- Main Game Class ----------------
class SpaceShooter:
    def __init__(self):
        # Make sure Pygame modules are ready
        if not pygame.get_init():
            pygame.init()
        if not pygame.font.get_init():
            pygame.font.init()

        # Create the display
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Matador")
        self.clock = pygame.time.Clock()

        # Sounds
        try:
            pygame.mixer.init()
            shoot_sound_path = os.path.join(ASSET_FILE_PATH, "shoot.wav")
            self.shoot_sound = pygame.mixer.Sound(shoot_sound_path)
            explosion_sound_path = os.path.join(ASSET_FILE_PATH, "explosion.wav")
            self.explosion_sound = pygame.mixer.Sound(explosion_sound_path)
        except Exception:
            self.shoot_sound = None
            self.explosion_sound = None

        self.font = pygame.font.Font(None, 36)

        # Game state
        self.score = 0
        self.wave = 1
        self.wave_spawned = False
        self.GAME_RUNNING = 1
        self.GAME_OVER = 2
        self.game_state = self.GAME_RUNNING

        # Sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.explosions = pygame.sprite.Group()

        self.player = Player(self)
        self.all_sprites.add(self.player)

        self.show_intro_screen()

    def show_intro_screen(self):
        """Intro screen with an image (press any key to continue)."""
        intro_image_path = os.path.join(ASSET_FILE_PATH, "MathIntro.png")
        try:
            intro_image = pygame.image.load(intro_image_path)
        except Exception:
            intro_image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            intro_image.fill(BLUE)

        intro_image = pygame.transform.scale(intro_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # End the entire game
                    return  # so run_game can detect we want to exit
                elif event.type == pygame.KEYDOWN:
                    waiting = False
            self.screen.blit(intro_image, (0, 0))
            pygame.display.flip()
            self.clock.tick(15)

    def draw_background(self):
        background_path = os.path.join(ASSET_FILE_PATH, "starry_background.png")
        try:
            bg = pygame.image.load(background_path)
            bg = pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.screen.blit(bg, (0, 0))
        except Exception:
            # fallback fill
            self.screen.fill(BLACK)

    def draw_ui(self):
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        health_text = self.font.render(f"Lives: {self.player.health}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(health_text, (10, 50))

    def get_enemies_for_wave(self, n):
        if n == 1:
            return 2
        elif n == 2:
            return 4
        else:
            return n

    def spawn_wave(self, n):
        count = self.get_enemies_for_wave(n)
        for i in range(count):
            speed = BASE_ENEMY_SPEED + 0.1
            x = random.randint(0, SCREEN_WIDTH - 120)
            spacing = 10
            y = -(i + 1) * (40 + spacing)
            enemy = Enemy(self, speed, x, y)
            self.enemies.add(enemy)
            self.all_sprites.add(enemy)

    def run_game_loop(self):
        """Main loop for the game."""
        running = True
        while running:
            dt = self.clock.tick(60)

            # Check if any wave should spawn
            if not self.enemies and not self.wave_spawned and self.game_state == self.GAME_RUNNING:
                self.spawn_wave(self.wave)
                self.wave_spawned = True

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False  # user closed the pygame window
                elif event.type == pygame.KEYDOWN:
                    if self.game_state == self.GAME_RUNNING:
                        if event.key == pygame.K_s:
                            self.player.shoot('increase', 1)
                        elif event.key == pygame.K_d:
                            self.player.shoot('decrease', 1)
                        elif event.key == pygame.K_a:
                            self.player.shoot('increase', 5)
                        elif event.key == pygame.K_f:
                            self.player.shoot('decrease', 5)
                    else:  # GAME_OVER
                        if event.key == pygame.K_r:
                            self.reset_game()
                        elif event.key == pygame.K_k:
                            running = False

            if self.game_state == self.GAME_RUNNING and running:
                self.all_sprites.update()

                # bullet-enemy collisions
                for bullet in self.bullets:
                    hits = pygame.sprite.spritecollide(bullet, self.enemies, False)
                    for e in hits:
                        e.hit(bullet.weapon_type, bullet.rect.centerx, bullet.amount)
                        bullet.kill()

                # player-enemy collisions
                p_hits = pygame.sprite.spritecollide(self.player, self.enemies, True)
                for e in p_hits:
                    explosion = Explosion(e.rect.centerx, e.rect.centery)
                    self.all_sprites.add(explosion)
                    self.explosions.add(explosion)
                    if self.explosion_sound:
                        self.explosion_sound.play()
                    self.player.health -= 1
                    if self.player.health <= 0:
                        self.game_state = self.GAME_OVER

                # If wave cleared
                if not self.enemies and self.game_state == self.GAME_RUNNING:
                    self.wave += 1
                    self.wave_spawned = False

            # Draw
            self.screen.fill(BLACK)
            self.draw_background()
            self.all_sprites.draw(self.screen)
            for e in self.enemies:
                e.draw(self.screen)
            self.draw_ui()

            # If game over, overlay
            if self.game_state == self.GAME_OVER:
                self.screen.fill(ORANGE)
                over_text = self.font.render("GAME OVER", True, BLACK)
                restart_text = self.font.render("R to restart, K to exit", True, BLACK)
                self.screen.blit(over_text, (SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 - 50))
                self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - 180, SCREEN_HEIGHT // 2))

            pygame.display.flip()

        # End of loop => user closed or pressed K
        pygame.quit()

    def reset_game(self):
        """Restart the game after game over."""
        self.score = 0
        self.wave = 1
        self.wave_spawned = False
        self.player.health = 3
        self.player.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)

        self.all_sprites.empty()
        self.enemies.empty()
        self.bullets.empty()
        self.explosions.empty()

        self.all_sprites.add(self.player)
        self.game_state = self.GAME_RUNNING


# ---------------- main(...) ----------------
def main(parent=None):
    """
    If parent is None, run the game standalone (blocks this script).
    If a parent is given (the main switchboard), run the game in a separate thread 
    with a hidden Toplevel so that the main window is blocked until the game ends.
    """
    # Ensure Pygame is ready for repeated runs
    if not pygame.get_init():
        pygame.init()

    if parent is None:
        # Standalone
        game = SpaceShooter()
        game.run_game_loop()
    else:
        # Modal / blocking mode with a hidden dummy Toplevel
        dummy = tk.Toplevel(parent)
        dummy.withdraw()
        dummy.grab_set()

        def game_thread():
            # Run Pygame game
            game = SpaceShooter()
            game.run_game_loop()
            # Once game ends, destroy dummy
            dummy.destroy()

        threading.Thread(target=game_thread, daemon=True).start()
        parent.wait_window(dummy)
