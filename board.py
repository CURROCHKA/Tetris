import pygame

from config import (
    BOARD_BLOCK_COLOR,
    BOARD_LINE_COLOR,
    BOARD_LINE_THICKNESS,
)


class Board:
    def __init__(self, x: float, y: float, block_size: float, board_size: tuple[int, int]):
        self.x = x
        self.y = y
        self.width, self.height = board_size
        self.block_size = block_size
        self.grid = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.colors = [[BOARD_BLOCK_COLOR for _ in range(self.width)] for _ in range(self.height)]

    def check_lines(self):    
        lines_cleared = 0
        new_grid = []
        new_colors = []
        
        for row, color_row in zip(self.grid, self.colors):
            if not all(row):
                new_grid.append(row)
                new_colors.append(color_row)
            else:
                lines_cleared += 1

        for _ in range(lines_cleared):
            new_grid.insert(0, [0 for _ in range(self.width)])
            new_colors.insert(0, [BOARD_BLOCK_COLOR for _ in range(self.width)])

        self.grid = new_grid
        self.colors = new_colors
        
        return lines_cleared

    def draw(self, surface: pygame.Surface):
        self.draw_blocks(surface)
        self.draw_lines(surface)

    def draw_lines(self, surface: pygame.Surface):
        # Vertical lines
        for x in range(self.width + 1):
            pygame.draw.line(
                surface,
                BOARD_LINE_COLOR,
                (self.x + x * self.block_size, self.y),
                (self.x + x * self.block_size, self.y + self.height * self.block_size),
                width=BOARD_LINE_THICKNESS,
            )
        # Horizontal lines
        for y in range(self.height + 1):
            pygame.draw.line(
                surface,
                BOARD_LINE_COLOR,
                (self.x, self.y + y * self.block_size),
                (self.x + self.width * self.block_size, self.y + y * self.block_size),
                width=BOARD_LINE_THICKNESS,
            )        

    def draw_blocks(self, surface):
        for y in range(self.height):
            for x in range(self.width):
                pygame.draw.rect(
                    surface,
                    self.colors[y][x],
                    (
                        self.x + x * self.block_size + BOARD_LINE_THICKNESS,
                        self.y + y * self.block_size + BOARD_LINE_THICKNESS,
                        self.block_size - BOARD_LINE_THICKNESS,
                        self.block_size - BOARD_LINE_THICKNESS,
                    ),
                )

    def reset(self):
        self.grid = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.colors = [[BOARD_BLOCK_COLOR for _ in range(self.width)] for _ in range(self.height)]
