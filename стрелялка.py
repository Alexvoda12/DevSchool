from ursina import *
import random

# ========== НАСТРОЙКИ ==========
WINDOW_SIZE = (1280, 720)           # Размер окна
FULLSCREEN = False                  # Полноэкранный режим
ENEMY_SPAWN_DELAY = 1.5             # Задержка между появлением врагов в волне
ENEMIES_PER_WAVE = 3                # Количество врагов в первой волне
ENEMY_SIZE = 1                      # Размер врага
ROOM_SIZE = 20                      # Размер комнаты
PLAYER_SPEED = 8                    # Скорость движения игрока
MOUSE_SENSITIVITY = (40, 40)        # Чувствительность мыши

# ========== ИНИЦИАЛИЗАЦИЯ ==========
app = Ursina(borderless=FULLSCREEN, fullscreen=FULLSCREEN, size=WINDOW_SIZE)

# Отключаем стандартный курсор
mouse.locked = True
mouse.visible = False

# ========== ИГРОК (от первого лица) ==========
class Player(Entity):
    def __init__(self):
        super().__init__(
            model='cube',           # Для отладки можно добавить модель, но лучше камера без тела
            color=color.white,
            scale=1,
            position=(0, 1, 0),
            collider='box'
        )
        # Камера будет привязана к игроку (обычно это делает FirstPersonController)
        # Мы используем камеру как дочерний объект
        camera.parent = self
        camera.position = (0, 1.5, 0)   # Высота глаз
        camera.rotation = (0, 0, 0)

        self.speed = PLAYER_SPEED
        self.health = 100
        self.score = 0

    def update(self):
        # Движение
        move_direction = Vec3(0, 0, 0)
        if held_keys['w']: move_direction.z += 1
        if held_keys['s']: move_direction.z -= 1
        if held_keys['a']: move_direction.x -= 1
        if held_keys['d']: move_direction.x += 1
        move_direction = camera.right * move_direction.x + camera.forward * move_direction.z
        move_direction.y = 0
        move_direction = move_direction.normalized() * self.speed * time.dt
        self.position += move_direction

        # Ограничение движения комнатой
        self.x = clamp(self.x, -ROOM_SIZE/2 + 1, ROOM_SIZE/2 - 1)
        self.z = clamp(self.z, -ROOM_SIZE/2 + 1, ROOM_SIZE/2 - 1)

        # Поворот камеры мышью
        self.rotation_x += mouse.velocity[1] * MOUSE_SENSITIVITY[1] * time.dt * 20
        self.rotation_y += mouse.velocity[0] * MOUSE_SENSITIVITY[0] * time.dt * 20
        self.rotation_x = clamp(self.rotation_x, -90, 90)

    def shoot(self):
        # Рейкаст из центра экрана вперёд
        hit_info = raycast(camera.world_position, camera.forward, distance=100, ignore=(self,))
        if hit_info.hit:
            enemy = hit_info.entity
            if isinstance(enemy, Enemy):
                destroy(enemy)
                self.score += 1
                # Воспроизведение звука попадания (если есть)
                if hasattr(self, 'hit_sound'):
                    self.hit_sound.play()
                # Проверяем, не закончились ли враги
                if len([e for e in scene.entities if isinstance(e, Enemy)]) == 0:
                    next_wave()

# ========== ВРАГ ==========
class Enemy(Entity):
    def __init__(self, position):
        super().__init__(
            model='cube',
            color=color.red,
            scale=ENEMY_SIZE,
            position=position,
            collider='box'
        )
        self.health = 1

    def update(self):
        # Враг просто стоит, но можно добавить погоню за игроком
        pass

# ========== УПРАВЛЕНИЕ ВОЛНАМИ ==========
current_wave = 1
enemies_to_spawn = ENEMIES_PER_WAVE
spawn_timer = 0

def next_wave():
    global current_wave, enemies_to_spawn, spawn_timer
    current_wave += 1
    enemies_to_spawn = ENEMIES_PER_WAVE + (current_wave - 1) * 2
    spawn_timer = ENEMY_SPAWN_DELAY
    print(f"Wave {current_wave} incoming! {enemies_to_spawn} enemies.")

def spawn_enemy():
    global enemies_to_spawn
    if enemies_to_spawn <= 0:
        return
    # Случайная позиция внутри комнаты, но не слишком близко к игроку
    while True:
        x = random.uniform(-ROOM_SIZE/2 + 2, ROOM_SIZE/2 - 2)
        z = random.uniform(-ROOM_SIZE/2 + 2, ROOM_SIZE/2 - 2)
        pos = Vec3(x, ENEMY_SIZE/2, z)
        if distance(player.position, pos) > 3:
            break
    Enemy(pos)
    enemies_to_spawn -= 1
    if enemies_to_spawn > 0:
        invoke(spawn_enemy, delay=ENEMY_SPAWN_DELAY)

# ========== СОЗДАНИЕ СЦЕНЫ ==========
# Пол
floor = Entity(model='plane', texture='grass', scale=ROOM_SIZE, color=color.gray, position=(0, -0.1, 0), collider='box')
# Стены (необязательно, но для ограничения)
wall_north = Entity(model='cube', scale=(ROOM_SIZE, 5, 0.2), color=color.blue, position=(0, 2, -ROOM_SIZE/2), collider='box')
wall_south = Entity(model='cube', scale=(ROOM_SIZE, 5, 0.2), color=color.blue, position=(0, 2, ROOM_SIZE/2), collider='box')
wall_west = Entity(model='cube', scale=(0.2, 5, ROOM_SIZE), color=color.blue, position=(-ROOM_SIZE/2, 2, 0), collider='box')
wall_east = Entity(model='cube', scale=(0.2, 5, ROOM_SIZE), color=color.blue, position=(ROOM_SIZE/2, 2, 0), collider='box')

# Создаём игрока
player = Player()

# ========== ИНТЕРФЕЙС ==========
score_text = Text(text='Score: 0', position=(-0.85, 0.45), scale=2, color=color.white, origin=(0,0))
wave_text = Text(text='Wave: 1', position=(-0.85, 0.4), scale=2, color=color.white, origin=(0,0))
crosshair = Entity(model='quad', texture='circle', scale=0.03, color=color.white, position=(0,0), parent=camera.ui)

def update_ui():
    score_text.text = f'Score: {player.score}'
    wave_text.text = f'Wave: {current_wave}'

# ========== ОБРАБОТЧИК ВЫСТРЕЛА ==========
def input(key):
    if key == 'left mouse down':
        player.shoot()
        # Проигрывание звука выстрела (опционально)
        # if hasattr(player, 'shoot_sound'): player.shoot_sound.play()

# ========== ЗАПУСК ПЕРВОЙ ВОЛНЫ ==========
def start_first_wave():
    global enemies_to_spawn
    enemies_to_spawn = ENEMIES_PER_WAVE
    spawn_enemy()

start_first_wave()

# ========== ОБНОВЛЕНИЕ UI КАЖДЫЙ КАДР ==========
def update():
    update_ui()

# ========== ЗАПУСК ИГРЫ ==========
if __name__ == '__main__':
    app.run()
