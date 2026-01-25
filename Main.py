import arcade
import random
import math
import os

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Tancheke"
SAVE_FILE = "record.txt"

TILE_SIZE = 40
BULLET_SPEED = 7
SHOOT_COOLDOWN = 1.3
MAX_LEVELS = 3
ANGLE_OFFSET = -90

def load_high_score():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as file:
                content = file.read().strip()
                return int(content) if content else 0
        except (ValueError, IOError):
            return 0
    return 0

def save_high_score(new_score):
    current_high = load_high_score()
    if new_score > current_high:
        with open(SAVE_FILE, "w", encoding="utf-8") as file:
            file.write(str(new_score))

def reset_high_score():
    if os.path.exists(SAVE_FILE):
        os.remove(SAVE_FILE)

class FloatingText(arcade.Sprite):
    def __init__(self, x, y, text):
        super().__init__()
        self.texture = arcade.Texture.create_empty(f"empty_{random.random()}", (1, 1))
        self.center_x = x
        self.center_y = y
        self.text = text
        self.alpha = 255
        self.change_y = 1
        self.font_size = 14

    def update(self, delta_time: float = 1 / 60):
        self.center_y += self.change_y
        self.alpha -= 3
        if self.font_size < 20:
            self.font_size += 0.2
        if self.alpha <= 0:
            self.remove_from_sprite_lists()

    def draw(self, **kwargs):
        final_color = (
            int(arcade.color.GREEN_YELLOW[0]),
            int(arcade.color.GREEN_YELLOW[1]),
            int(arcade.color.GREEN_YELLOW[2]),
            int(max(0, self.alpha))
        )
        arcade.draw_text(
            self.text,
            self.center_x,
            self.center_y,
            final_color,
            int(self.font_size),
            anchor_x="center",
            bold=True
        )

class Particle(arcade.SpriteCircle):
    def __init__(self, x, y, color):
        super().__init__(random.randint(2, 4), color)
        self.center_x = x
        self.center_y = y
        speed = random.uniform(2, 6)
        angle = random.uniform(0, 2 * math.pi)
        self.change_x = math.cos(angle) * speed
        self.change_y = math.sin(angle) * speed
        self.alpha = 255
        self.fade_rate = random.randint(4, 8)

    def update(self, delta_time: float = 1 / 60):
        self.center_x += self.change_x
        self.center_y += self.change_y
        self.alpha -= self.fade_rate
        if self.alpha <= 0:
            self.remove_from_sprite_lists()

class Barrel(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__("PNG/Box.png", scale=1.0)
        self.center_x = x
        self.center_y = y
        self.target_x = x
        self.target_y = y
        self.hp = 3
        self.is_moving = False
        self.move_speed = 4
        self.textures_list = [
            arcade.load_texture("PNG/Box1.png"),
            arcade.load_texture("PNG/Box2.png"),
            arcade.load_texture("PNG/Box.png")
        ]

    def update(self, delta_time: float = 1 / 60):
        if self.is_moving:
            if self.center_x < self.target_x:
                self.center_x += self.move_speed
            elif self.center_x > self.target_x:
                self.center_x -= self.move_speed
            elif self.center_y < self.target_y:
                self.center_y += self.move_speed
            elif self.center_y > self.target_y:
                self.center_y -= self.move_speed
            if (abs(self.center_x - self.target_x) < 4 and
                    abs(self.center_y - self.target_y) < 4):
                self.center_x = self.target_x
                self.center_y = self.target_y
                self.is_moving = False

    def push(self, dx, dy, walls, barrels):
        if self.is_moving:
            return False
        new_x = self.center_x + dx * TILE_SIZE
        new_y = self.center_y + dy * TILE_SIZE
        if (new_x < 20 or new_x > SCREEN_WIDTH - 20 or
                new_y < 20 or new_y > SCREEN_HEIGHT - 20):
            return False
        checker = arcade.SpriteSolidColor(32, 32, arcade.color.WHITE)
        checker.center_x = new_x
        checker.center_y = new_y
        if (arcade.check_for_collision_with_list(checker, walls) or
                arcade.check_for_collision_with_list(checker, barrels)):
            return False
        self.target_x = new_x
        self.target_y = new_y
        self.is_moving = True
        return True

    def take_damage(self):
        self.hp -= 1
        if self.hp > 0:
            self.texture = self.textures_list[self.hp - 1]
        return self.hp <= 0

class GridTank(arcade.Sprite):
    def __init__(self, image_file, x, y, speed=4, scale=1.5):
        super().__init__(image_file, scale=scale)
        self.center_x = x
        self.center_y = y
        self.target_x = x
        self.target_y = y
        self.is_moving = False
        self.move_speed = speed
        self.logical_angle = -90
        self.angle = self.logical_angle + ANGLE_OFFSET

    def update(self, delta_time: float = 1 / 60):
        if self.is_moving:
            if self.center_x < self.target_x:
                self.center_x += self.move_speed
            elif self.center_x > self.target_x:
                self.center_x -= self.move_speed
            elif self.center_y < self.target_y:
                self.center_y += self.move_speed
            elif self.center_y > self.target_y:
                self.center_y -= self.move_speed
            if (abs(self.center_x - self.target_x) < 4 and
                    abs(self.center_y - self.target_y) < 4):
                self.center_x = self.target_x
                self.center_y = self.target_y
                self.is_moving = False

    def start_move(self, dx, dy, logical_angle, walls, barrels):
        self.logical_angle = logical_angle
        self.angle = logical_angle + ANGLE_OFFSET
        if self.is_moving:
            return
        new_x = self.center_x + dx * TILE_SIZE
        new_y = self.center_y + dy * TILE_SIZE
        if (new_x < 20 or new_x > SCREEN_WIDTH - 20 or
                new_y < 20 or new_y > SCREEN_HEIGHT - 20):
            return
        checker = arcade.SpriteSolidColor(25, 25, arcade.color.WHITE)
        checker.center_x = new_x
        checker.center_y = new_y
        hit_barrels = arcade.check_for_collision_with_list(checker, barrels)
        if hit_barrels:
            if hit_barrels[0].push(dx, dy, walls, barrels):
                self.target_x = new_x
                self.target_y = new_y
                self.is_moving = True
            return
        if not arcade.check_for_collision_with_list(checker, walls):
            self.target_x = new_x
            self.target_y = new_y
            self.is_moving = True

class Boss(GridTank):
    def __init__(self, x, y):
        super().__init__("PNG/Boss.png", x, y, speed=0, scale=2.0)
        self.hp = 10
        self.shoot_timer = 0
        self.logical_angle = 0

    def update_aim(self, player_x, player_y):
        dx = player_x - self.center_x
        dy = player_y - self.center_y
        rad = math.atan2(dy, dx)
        self.logical_angle = math.degrees(rad)
        self.angle = self.logical_angle - 90

    def take_damage(self):
        self.hp -= 1
        return self.hp <= 0

    def update(self, delta_time: float = 1 / 60):
        super().update()

    def shoot_fan(self, bullet_list):
        for offset in [-20, 0, 20]:
            angle = self.logical_angle + offset
            rad = math.radians(angle)
            bullet = arcade.SpriteSolidColor(8, 8, arcade.color.RED)
            bullet.center_x = self.center_x + math.cos(rad) * 60
            bullet.center_y = self.center_y + math.sin(rad) * 60
            bullet.change_x = math.cos(rad) * (BULLET_SPEED * 1.2)
            bullet.change_y = math.sin(rad) * (BULLET_SPEED * 1.2)
            bullet.is_enemy = True
            bullet_list.append(bullet)

class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.level = 1
        self.lives = 3
        self.score = 0
        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList(use_spatial_hash=True)
        self.barrel_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.particle_list = arcade.SpriteList()
        self.player = None
        self.shoot_sound = arcade.load_sound("Bam.mp3")
        self.hp_sound = arcade.load_sound("HP.mp3")
        self.floating_texts = arcade.SpriteList()
        self.camera = arcade.camera.Camera2D()
        self.is_zoomed = False

    def setup_secret_level(self):
        self.level = 999
        self.player_list.clear()
        self.wall_list.clear()
        self.barrel_list.clear()
        self.enemy_list.clear()
        self.bullet_list.clear()
        self.particle_list.clear()
        self.player = GridTank("PNG/Me.png", 420, 60, speed=4)
        self.player_list.append(self.player)
        self.boss = Boss(420, 540)
        self.enemy_list.append(self.boss)
        for col in range(1, (SCREEN_WIDTH // TILE_SIZE) - 1):
            for row in range(3, (SCREEN_HEIGHT // TILE_SIZE) - 3):
                x = col * TILE_SIZE + 20
                y = row * TILE_SIZE + 20
                if random.random() < 0.15:
                    self.barrel_list.append(Barrel(x, y))

    def setup(self):
        self.player_list.clear()
        self.wall_list.clear()
        self.barrel_list.clear()
        self.enemy_list.clear()
        self.bullet_list.clear()
        self.particle_list.clear()
        self.floating_texts.clear()
        for row_idx, row in enumerate(MAP_DATA):
            for col_idx, cell in enumerate(row):
                if cell == 1:
                    wall = arcade.Sprite("PNG/Wall.png", scale=1.0)
                    wall.center_x = col_idx * TILE_SIZE + 20
                    wall.center_y = SCREEN_HEIGHT - (row_idx * TILE_SIZE + 20)
                    self.wall_list.append(wall)
        self.player = GridTank("PNG/Me.png", 420, 60, speed=4)
        self.player_list.append(self.player)
        for _ in range(10 + self.level * 2):
            while True:
                barrel_x = random.randint(1, 18) * 40 + 20
                barrel_y = random.randint(1, 13) * 40 + 20
                checker = arcade.SpriteCircle(15, arcade.color.WHITE)
                checker.center_x = barrel_x
                checker.center_y = barrel_y
                if not (arcade.check_for_collision_with_list(checker, self.wall_list) or
                        arcade.check_for_collision(checker, self.player)):
                    self.barrel_list.append(Barrel(barrel_x, barrel_y))
                    break
        for i in range(self.level * 2 + 1):
            spawn_points = [(60, 540), (740, 540), (60, 300),
                            (740, 300), (420, 540)]
            pos = spawn_points[i % len(spawn_points)]
            enemy = GridTank("PNG/Enemy.png", pos[0], pos[1],
                             speed=2 + (self.level * 0.4))
            enemy.logical_angle = 270
            enemy.angle = 180
            enemy.shoot_timer = 0
            self.enemy_list.append(enemy)

    def create_explosion(self, x, y, color, count=20):
        for _ in range(count):
            self.particle_list.append(Particle(x, y, color))

    def on_draw(self):
        self.clear()
        with self.camera.activate():
            self.wall_list.draw()
            self.barrel_list.draw()
            self.enemy_list.draw()
            self.bullet_list.draw()
            self.player_list.draw()
            self.particle_list.draw()
            for text_sprite in self.floating_texts:
                text_sprite.draw()
            for barrel in self.barrel_list:
                arcade.draw_text(
                    str(barrel.hp),
                    barrel.center_x,
                    barrel.center_y - 7,
                    arcade.color.WHITE,
                    10,
                    anchor_x="center",
                    bold=True
                )
        self.window.default_camera.use()
        arcade.draw_text(
            f"SCORE: {self.score} | LIVES: {self.lives} | LEVEL: {self.level}",
            10, 575,
            arcade.color.WHITE,
            12,
            bold=True
        )
        arcade.draw_text(
            "M: MENU | R: RESET | F: ZOOM",
            600, 575,
            arcade.color.LIGHT_GRAY,
            10,
            bold=True
        )

    def on_update(self, delta_time):
        for enemy in self.enemy_list:
            if isinstance(enemy, Boss):
                enemy.update_aim(self.player.center_x, self.player.center_y)
        self.player_list.update()
        self.enemy_list.update()
        self.barrel_list.update()
        self.bullet_list.update()
        self.particle_list.update()
        self.floating_texts.update()
        for enemy in self.enemy_list:
            enemy.shoot_timer += delta_time
            if isinstance(enemy, Boss):
                if enemy.shoot_timer > 1.2:
                    enemy.shoot_fan(self.bullet_list)
                    enemy.shoot_timer = 0
            else:
                if not enemy.is_moving:
                    dx, dy, angle = random.choice([(1, 0, 0), (-1, 0, 180), (0, 1, 90), (0, -1, 270)])
                    enemy.start_move(dx, dy, angle, self.wall_list, self.barrel_list)
                if enemy.shoot_timer > SHOOT_COOLDOWN:
                    if (abs(enemy.center_x - self.player.center_x) < 30 or
                            abs(enemy.center_y - self.player.center_y) < 30):
                        self._fire_bullet(enemy, is_enemy=True)
                        enemy.shoot_timer = 0
        for bullet in self.bullet_list[:]:
            if arcade.check_for_collision_with_list(bullet, self.wall_list):
                bullet.remove_from_sprite_lists()
                continue
            hit_barrels = arcade.check_for_collision_with_list(bullet, self.barrel_list)
            if hit_barrels:
                bullet.remove_from_sprite_lists()
                if hit_barrels[0].take_damage():
                    self.create_explosion(hit_barrels[0].center_x, hit_barrels[0].center_y, arcade.color.ORANGE)
                    if random.random() < 0.3:
                        self.lives += 1
                        arcade.play_sound(self.hp_sound)
                        self.floating_texts.append(
                            FloatingText(hit_barrels[0].center_x, hit_barrels[0].center_y, "+1 LIFE"))
                    hit_barrels[0].remove_from_sprite_lists()
                    self.score += 50
                continue
            if getattr(bullet, 'is_enemy', False):
                if arcade.check_for_collision(bullet, self.player):
                    bullet.remove_from_sprite_lists()
                    self.lives -= 1
                    self.create_explosion(self.player.center_x, self.player.center_y, arcade.color.RED_ORANGE, count=30)
                    if self.lives <= 0:
                        save_high_score(self.score)
                        self.window.show_view(GameOverView("DEFEAT", self.score))
                    else:
                        if self.level != 999:
                            self.player.center_x, self.player.center_y = 420, 60
                            self.player.target_x, self.player.target_y = 420, 60
            else:
                hit_enemies = arcade.check_for_collision_with_list(bullet, self.enemy_list)
                if hit_enemies:
                    bullet.remove_from_sprite_lists()
                    target = hit_enemies[0]
                    if isinstance(target, Boss):
                        if target.take_damage():
                            self.create_explosion(target.center_x, target.center_y, arcade.color.GOLD, count=50)
                            target.remove_from_sprite_lists()
                            self.score += 1000
                            self.window.show_view(GameOverView("BOSS DEFEATED!", self.score))
                        else:
                            self.create_explosion(target.center_x, target.center_y, arcade.color.WHITE, count=5)
                    else:
                        self.create_explosion(target.center_x, target.center_y, arcade.color.YELLOW, count=25)
                        target.remove_from_sprite_lists()
                        self.score += 100
        if not self.enemy_list:
            if self.level == 999:
                pass
            elif self.level < MAX_LEVELS:
                self.level += 1
                self.setup()
            else:
                save_high_score(self.score)
                self.window.show_view(GameOverView("VICTORY!", self.score))
        target_zoom = 4.0 if self.is_zoomed else 1.0
        self.camera.zoom = arcade.math.lerp(self.camera.zoom, target_zoom, 0.1)
        target_pos = list(self.player.position)
        if self.is_zoomed:
            view_width = SCREEN_WIDTH / self.camera.zoom
            view_height = SCREEN_HEIGHT / self.camera.zoom
            target_pos[0] = max(view_width / 2, min(target_pos[0], SCREEN_WIDTH - view_width / 2))
            target_pos[1] = max(view_height / 2, min(target_pos[1], SCREEN_HEIGHT - view_height / 2))
        self.camera.position = arcade.math.lerp_2d(self.camera.position, tuple(target_pos), 0.1)

    def _fire_bullet(self, owner, is_enemy=False):
        visual_angle = owner.logical_angle
        actual_angle = visual_angle
        if visual_angle == 0:
            actual_angle = 180
        elif visual_angle == 180:
            actual_angle = 0
        radians_angle = math.radians(actual_angle)
        color = arcade.color.RED if is_enemy else arcade.color.WHITE
        bullet = arcade.SpriteSolidColor(6, 6, color)
        bullet.center_x = owner.center_x + math.cos(radians_angle) * 25
        bullet.center_y = owner.center_y + math.sin(radians_angle) * 25
        bullet.change_x = math.cos(radians_angle) * BULLET_SPEED
        bullet.change_y = math.sin(radians_angle) * BULLET_SPEED
        bullet.is_enemy = is_enemy
        self.bullet_list.append(bullet)
        arcade.play_sound(self.shoot_sound)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.UP:
            self.player.start_move(0, 1, 90,
                                   self.wall_list, self.barrel_list)
        elif key == arcade.key.DOWN:
            self.player.start_move(0, -1, 270,
                                   self.wall_list, self.barrel_list)
        elif key == arcade.key.LEFT:
            self.player.start_move(-1, 0, 0,
                                   self.wall_list, self.barrel_list)
        elif key == arcade.key.RIGHT:
            self.player.start_move(1, 0, 180,
                                   self.wall_list, self.barrel_list)
        elif key == arcade.key.SPACE:
            self._fire_bullet(self.player)
        elif key == arcade.key.M:
            self.window.show_view(MenuView())
        elif key == arcade.key.R:
            self.setup()
        elif key == arcade.key.F:
            self.is_zoomed = not self.is_zoomed
        elif key == arcade.key.B:
            print("Активация секретного уровня!")
            self.setup_secret_level()

class GameOverView(arcade.View):
    def __init__(self, result_text, final_score):
        super().__init__()
        self.result_text = result_text
        self.final_score = final_score

    def on_draw(self):
        self.clear()
        arcade.draw_text(
            self.result_text,
            400, 350,
            arcade.color.GOLD,
            50,
            anchor_x="center"
        )
        arcade.draw_text(
            f"SCORE: {self.final_score}",
            400, 280,
            arcade.color.WHITE,
            20,
            anchor_x="center"
        )
        arcade.draw_text(
            "ENTER: RESTART | M: MENU | R: RESET RECORD",
            400, 200,
            arcade.color.GRAY,
            15,
            anchor_x="center"
        )

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ENTER:
            game_view = GameView()
            game_view.setup()
            self.window.show_view(game_view)
        elif key == arcade.key.M:
            self.window.show_view(MenuView())
        elif key == arcade.key.R:
            reset_high_score()
            self.window.show_view(MenuView())

class MenuView(arcade.View):
    def on_show_view(self):
        self.high_score = load_high_score()

    def on_draw(self):
        self.clear()
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)
        arcade.draw_text(
            "TANCHEKE",
            400, 350,
            arcade.color.GOLD,
            35,
            anchor_x="center"
        )
        arcade.draw_text(
            f"HIGH SCORE: {self.high_score}",
            400, 280,
            arcade.color.CYAN,
            20,
            anchor_x="center"
        )
        arcade.draw_text(
            "ENTER: START | R: RESET RECORD",
            400, 200,
            arcade.color.WHITE,
            20,
            anchor_x="center"
        )

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ENTER:
            game_view = GameView()
            game_view.setup()
            self.window.show_view(game_view)
        elif key == arcade.key.R:
            reset_high_score()
            self.high_score = 0

MAP_DATA = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1],
    [1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 0, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1],
    [1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]

def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.show_view(MenuView())
    arcade.run()

if __name__ == "__main__":
    main()
