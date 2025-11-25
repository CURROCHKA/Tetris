from random import choice, randint

import pygame

from config import (
    WALL_KICK_DATA,
    TETROMINOS, 
    TETROMINOS_COLORS,
    BOARD_LINE_THICKNESS,
    LEVEL_SPEEDS,
    MOVE_DELAY,
)


class Tetromino:
    def __init__(self, shape_name: str, board, level: int = 0):
        self.shape_name = shape_name
        self.board = board
        self.block_size = board.block_size
        self.color = TETROMINOS_COLORS[self.shape_name]
        self._level = level
        
        self.x, self.y = 0, 0
        self.rotation = 0
        self.reset_position()

        self.last_move = pygame.time.get_ticks() / 1000

        self.last_fall = pygame.time.get_ticks() / 1000
        self.falling_delay = LEVEL_SPEEDS[level]
    
    def is_valid_position(self, dx=0, dy=0, rotation=None):
        """Проверяет валидность позиции фигуры"""
        temp_rotation = rotation if rotation is not None else self.rotation
        shape = TETROMINOS[self.shape_name][temp_rotation]
        
        for row_idx, row in enumerate(shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    new_x = self.x + col_idx + dx
                    new_y = self.y + row_idx + dy
                    
                    # Проверка границ
                    if new_x < 0 or new_x >= self.board.width or new_y >= self.board.height:
                        return False
                    # Проверка столкновений с другими блоками (если y >= 0)
                    if new_y >= 0 and self.board.grid[new_y][new_x]:
                        return False
        return True
    
    def fall(self) -> tuple[bool, bool]:
        current_time = pygame.time.get_ticks() / 1000
        if current_time - self.last_fall >= self.falling_delay:
            if not self.move(0, 1):
                locked_above = self.lock()
                return True, locked_above  # Фигура зафиксирована
            self.last_fall = current_time
        return False, False  # Фигура не зафиксирована

    def rotate(self, direction=1):
        old_rotation = self.rotation
        old_x, old_y = self.x, self.y

        self.rotation = (self.rotation + direction) % 4
        transition = (old_rotation, self.rotation)

        # Получаем данные для wall kick
        kick_data = WALL_KICK_DATA["I"] if self.shape_name == "I" else WALL_KICK_DATA["default"]
        kicks = kick_data.get(transition, [(0, 0)])

        # Пробуем все возможные сдвиги
        for dx, dy in kicks:
            self.x = old_x + dx
            self.y = old_y + dy

            if self.is_valid_position():
                return True  # Вращение успешно

        # Если ни один вариант не подошел - откатываем
        self.rotation = old_rotation
        self.x, self.y = old_x, old_y
        return False
    
    def lock(self) -> bool:
        locked_above = False
        for x, y in self.get_cells():
            if y < 0:
                locked_above = True
                continue
            if 0 <= x < self.board.width and 0 <= y < self.board.height:
                self.board.grid[y][x] = 1  # Блок занят
                self.board.colors[y][x] = self.color
        return locked_above

    def move(self, dx, dy) -> bool:
        if self.is_valid_position(dx, dy):
            if dx != 0:
                current_time = pygame.time.get_ticks() / 1000
                if current_time - self.last_move >= MOVE_DELAY:
                    self.x += dx
                    self.last_move = current_time
            self.y += dy
            return True
        return False
    
    def hard_drop(self) -> bool:
        while self.move(0, 1):
            pass
        locked_above = self.lock()
        return locked_above

    def get_cells(self):
        cells = []
        shape = self.shape
        for row_idx, row in enumerate(shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    cells.append((self.x + col_idx, self.y + row_idx))
        return cells
    
    def _draw_block(self, surface: pygame.Surface, row_idx: int, col_idx: int, color: tuple[int, int, int]):
        pygame.draw.rect(
            surface,
            color,
            (
                self.board.x + (self.x + col_idx) * self.block_size + BOARD_LINE_THICKNESS,
                self.board.y + (self.y + row_idx) * self.block_size + BOARD_LINE_THICKNESS,
                self.block_size - BOARD_LINE_THICKNESS,
                self.block_size - BOARD_LINE_THICKNESS,
            ),
        )
    
    def draw(self, surface):
        shape = self.shape
        old_x, old_y = self.x, self.y

        for row_idx, row in enumerate(shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    if self.y + row_idx >= 0:
                        self._draw_block(surface, row_idx, col_idx, self.color)
                    while self.is_valid_position(0, 1):
                        self.y += 1
                    if self.y == old_y:
                        continue
                    self._draw_block(surface, row_idx, col_idx, (128, 128, 128))
                    self.x, self.y = old_x, old_y

    @property
    def shape(self):
        return TETROMINOS[self.shape_name][self.rotation]
    
    def reset_position(self, y: int = -1):
        if self.shape_name == "O":
            self.x = self.board.width // 2 - 1
        else:
            self.x = self.board.width // 2 - 2
        self.y = y
        self.rotation = 0

    def swap_board(self, new_board, y: int = -1, board_reset: bool = False, lock: bool = False):
        self.board = new_board
        self.block_size = new_board.block_size
        self.reset_position(y)
        if board_reset:
            self.board.reset()
        if lock:
            self.lock()

    def change_fall_delay(self, new_delay: float):
        self.falling_delay = new_delay

    def reset_fall_delay(self):
        self.falling_delay = LEVEL_SPEEDS[self._level]
