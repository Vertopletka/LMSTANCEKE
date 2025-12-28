import arcade
import random
import math
import os

# --- Константы ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Tanchiki: Pro Edition (Full Effects)"
SAVE_FILE = "record.txt"

TILE_SIZE = 40
BULLET_SPEED = 7
SHOOT_COOLDOWN = 1.3
MAX_LEVELS = 3
ANGLE_OFFSET = -90


# --- Функции сохранения ---
def load_high_score():
    """Загружает лучший результат из файла."""
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as file:
                content = file.read().strip()
                return int(content) if content else 0
        except (ValueError, IOError):
            return 0
    return 0


def save_high_score(new_score):
    """Сохраняет новый результат, если он лучше текущего."""
    current_high = load_high_score()
    if new_score > current_high:
        with open(SAVE_FILE, "w", encoding="utf-8") as file:
            file.write(str(new_score))


def reset_high_score():
    """Удаляет файл рекорда."""
    if os.path.exists(SAVE_FILE):
        os.remove(SAVE_FILE)


# --- Классы объектов ---
class Particle(arcade.SpriteCircle):
    """Класс для частиц взрыва."""

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
        """Обновляет позицию и прозрачность частицы."""
        self.center_x += self.change_x
        self.center_y += self.change_y
        self.alpha -= self.fade_rate
        if self.alpha <= 0:
            self.remove_from_sprite_lists()


class Barrel(arcade.Sprite):
    """Класс для передвижных бочек."""

    def __init__(self, x, y):
        super().__init__("PNG/Box.png", scale=1.0)
        self.center_x = x
        self.center_y = y
        self.target_x = x
        self.target_y = y
        self.hp = 3
        self.is_moving = False
        self.move_speed = 4

    def update(self, delta_time: float = 1 / 60):
        """Обновляет позицию бочки при движении."""
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
        """Пытается передвинуть бочку в указанном направлении."""
        if self.is_moving:
            return False

        new_x = self.center_x + dx * TILE_SIZE
        new_y = self.center_y + dy * TILE_SIZE

        # Проверка границ экрана
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
        """Наносит урон бочке и возвращает True, если бочка уничтожена."""
        self.hp -= 1
        return self.hp <= 0


class GridTank(arcade.Sprite):
    """Класс для танков с пошаговым движением по сетке."""

    def __init__(self, image_file, x, y, speed=4, scale=1.5):
        super().__init__(image_file, scale=scale)
        self.center_x = x
        self.center_y = y
        self.target_x = x
        self.target_y = y
        self.is_moving = False
        self.move_speed = speed
        self.logical_angle = -90  # Логический угол для движения
        self.angle = self.logical_angle + ANGLE_OFFSET  # Визуальный угол

    def update(self, delta_time: float = 1 / 60):
        """Обновляет позицию танка при движении."""
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
        """Начинает движение танка в указанном направлении."""
        self.logical_angle = logical_angle
        self.angle = logical_angle + ANGLE_OFFSET

        if self.is_moving:
            return

        new_x = self.center_x + dx * TILE_SIZE
        new_y = self.center_y + dy * TILE_SIZE

        # Проверка границ экрана
        if (new_x < 20 or new_x > SCREEN_WIDTH - 20 or
                new_y < 20 or new_y > SCREEN_HEIGHT - 20):
            return

        checker = arcade.SpriteSolidColor(25, 25, arcade.color.WHITE)
        checker.center_x = new_x
        checker.center_y = new_y

        # Проверка столкновения с бочками
        hit_barrels = arcade.check_for_collision_with_list(checker, barrels)
        if hit_barrels:
            if hit_barrels[0].push(dx, dy, walls, barrels):
                self.target_x = new_x
                self.target_y = new_y
                self.is_moving = True
            return

        # Проверка столкновения со стенами
        if not arcade.check_for_collision_with_list(checker, walls):
            self.target_x = new_x
            self.target_y = new_y
            self.is_moving = True


# --- Игровой процесс ---
class GameView(arcade.View):
    """Основной игровой экран."""

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

    def setup(self):
        """Инициализация игрового уровня."""
        self.player_list.clear()
        self.wall_list.clear()
        self.barrel_list.clear()
        self.enemy_list.clear()
        self.bullet_list.clear()
        self.particle_list.clear()

        # Создание стен по карте
        for row_idx, row in enumerate(MAP_DATA):
            for col_idx, cell in enumerate(row):
                if cell == 1:
                    wall = arcade.Sprite("PNG/Wall.png", scale=1.0)
                    wall.center_x = col_idx * TILE_SIZE + 20
                    wall.center_y = SCREEN_HEIGHT - (row_idx * TILE_SIZE + 20)
                    self.wall_list.append(wall)

        # Создание игрока
        self.player = GridTank("PNG/Me.png", 420, 60, speed=4)
        self.player_list.append(self.player)

        # Создание бочек
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

        # Создание врагов
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
        """Создает эффект взрыва в указанной позиции."""
        for _ in range(count):
            self.particle_list.append(Particle(x, y, color))

    def on_draw(self):
        """Отрисовка игрового экрана."""
        self.clear()

        # Отрисовка всех спрайтов
        self.wall_list.draw()
        self.barrel_list.draw()
        self.enemy_list.draw()
        self.bullet_list.draw()
        self.player_list.draw()
        self.particle_list.draw()

        # Отрисовка HP бочек
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

        # Статистика игры
        arcade.draw_text(
            f"SCORE: {self.score} | LIVES: {self.lives} | LEVEL: {self.level}",
            10, 575,
            arcade.color.WHITE,
            12,
            bold=True
        )

        arcade.draw_text(
            "M: MENU | R: RESET",
            650, 575,
            arcade.color.LIGHT_GRAY,
            10,
            bold=True
        )

    def on_update(self, delta_time):
        """Обновление игровой логики."""
        self.player_list.update()
        self.enemy_list.update()
        self.barrel_list.update()
        self.bullet_list.update()
        self.particle_list.update()

        # Обновление врагов
        for enemy in self.enemy_list:
            if not enemy.is_moving:
                dx, dy, angle = random.choice([
                    (1, 0, 0), (-1, 0, 180),
                    (0, 1, 90), (0, -1, 270)
                ])
                enemy.start_move(dx, dy, angle,
                                 self.wall_list, self.barrel_list)

            enemy.shoot_timer += delta_time
            if enemy.shoot_timer > SHOOT_COOLDOWN:
                if (abs(enemy.center_x - self.player.center_x) < 30 or
                        abs(enemy.center_y - self.player.center_y) < 30):
                    self._fire_bullet(enemy, is_enemy=True)
                    enemy.shoot_timer = 0

        # Обновление пуль
        for bullet in self.bullet_list[:]:
            # Столкновение со стенами
            if arcade.check_for_collision_with_list(bullet, self.wall_list):
                bullet.remove_from_sprite_lists()
                continue

            # Столкновение с бочками
            hit_barrels = arcade.check_for_collision_with_list(bullet, self.barrel_list)
            if hit_barrels:
                bullet.remove_from_sprite_lists()
                if hit_barrels[0].take_damage():
                    self.create_explosion(
                        hit_barrels[0].center_x, hit_barrels[0].center_y,
                        arcade.color.ORANGE
                    )
                    hit_barrels[0].remove_from_sprite_lists()
                    self.score += 50
                    # Шанс получения дополнительной жизни
                    if random.random() < 0.15:
                        self.lives += 1
                continue

            # Пули врагов
            if getattr(bullet, 'is_enemy', False):
                if arcade.check_for_collision(bullet, self.player):
                    bullet.remove_from_sprite_lists()
                    self.lives -= 1
                    self.create_explosion(
                        self.player.center_x, self.player.center_y,
                        arcade.color.RED_ORANGE, count=30
                    )

                    if self.lives <= 0:
                        save_high_score(self.score)
                        self.window.show_view(
                            GameOverView("DEFEAT", self.score)
                        )
                    else:
                        self.player.center_x = 420
                        self.player.center_y = 60
                        self.player.target_x = 420
                        self.player.target_y = 60

            # Пули игрока
            else:
                hit_enemies = arcade.check_for_collision_with_list(bullet, self.enemy_list)
                if hit_enemies:
                    bullet.remove_from_sprite_lists()
                    self.create_explosion(
                        hit_enemies[0].center_x, hit_enemies[0].center_y,
                        arcade.color.YELLOW, count=25
                    )
                    hit_enemies[0].remove_from_sprite_lists()
                    self.score += 100

        # Проверка завершения уровня
        if not self.enemy_list:
            if self.level < MAX_LEVELS:
                self.level += 1
                self.setup()
            else:
                save_high_score(self.score)
                self.window.show_view(
                    GameOverView("VICTORY!", self.score)
                )

    def _fire_bullet(self, owner, is_enemy=False):
        """Создает пулю от указанного владельца."""
        # Исправление направления пули
        visual_angle = owner.logical_angle
        actual_angle = visual_angle

        # Инвертируем только лево и право
        if visual_angle == 0:  # Танк смотрит НАЛЕВО
            actual_angle = 180  # Пуля летит ВЛЕВО
        elif visual_angle == 180:  # Танк смотрит НАПРАВО
            actual_angle = 0  # Пуля летит ВПРАВО

        # Перевод угла в радианы
        radians_angle = math.radians(actual_angle)

        # Создание пули
        color = arcade.color.RED if is_enemy else arcade.color.WHITE
        bullet = arcade.SpriteSolidColor(6, 6, color)

        # Позиция пули
        bullet.center_x = owner.center_x + math.cos(radians_angle) * 25
        bullet.center_y = owner.center_y + math.sin(radians_angle) * 25

        # Вектор скорости
        bullet.change_x = math.cos(radians_angle) * BULLET_SPEED
        bullet.change_y = math.sin(radians_angle) * BULLET_SPEED

        bullet.is_enemy = is_enemy
        self.bullet_list.append(bullet)

    def on_key_press(self, key, modifiers):
        """Обработка нажатий клавиш."""
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
        elif key == arcade.key.M:  # Выход в меню
            self.window.show_view(MenuView())
        elif key == arcade.key.R:  # Перезапуск уровня
            self.setup()


class GameOverView(arcade.View):
    """Экран окончания игры."""

    def __init__(self, result_text, final_score):
        super().__init__()
        self.result_text = result_text
        self.final_score = final_score

    def on_draw(self):
        """Отрисовка экрана окончания игры."""
        self.clear()

        # Основной текст
        arcade.draw_text(
            self.result_text,
            400, 350,
            arcade.color.GOLD,
            50,
            anchor_x="center"
        )

        # Статистика
        arcade.draw_text(
            f"SCORE: {self.final_score}",
            400, 280,
            arcade.color.WHITE,
            20,
            anchor_x="center"
        )

        # Управление
        arcade.draw_text(
            "ENTER: RESTART | M: MENU | R: RESET RECORD",
            400, 200,
            arcade.color.GRAY,
            15,
            anchor_x="center"
        )

    def on_key_press(self, key, modifiers):
        """Обработка нажатий клавиш на экране окончания."""
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
    """Главное меню игры."""

    def on_show_view(self):
        """Подготовка меню."""
        self.high_score = load_high_score()

    def on_draw(self):
        """Отрисовка меню."""
        self.clear()
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)

        # Заголовок
        arcade.draw_text(
            "TANCHIKI: PRO",
            400, 350,
            arcade.color.GOLD,
            35,
            anchor_x="center"
        )

        # Рекорд
        arcade.draw_text(
            f"HIGH SCORE: {self.high_score}",
            400, 280,
            arcade.color.CYAN,
            20,
            anchor_x="center"
        )

        # Управление
        arcade.draw_text(
            "ENTER: START | R: RESET RECORD",
            400, 200,
            arcade.color.WHITE,
            20,
            anchor_x="center"
        )

    def on_key_press(self, key, modifiers):
        """Обработка нажатий клавиш в меню."""
        if key == arcade.key.ENTER:
            game_view = GameView()
            game_view.setup()
            self.window.show_view(game_view)
        elif key == arcade.key.R:  # Сброс рекорда
            reset_high_score()
            self.high_score = 0


# --- Данные карты ---
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
    """Главная функция для запуска игры."""
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.show_view(MenuView())
    arcade.run()


if __name__ == "__main__":
    main()
