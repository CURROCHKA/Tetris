from random import shuffle
from math import sqrt

import pygame

from tetromino import Tetromino
from board import Board


from config import (
    WIDTH,
    HEIGHT,
    FPS,
    HORIZONTAL_MARGIN_RATIO,
    VERTICAL_MARGIN_RATIO,
    BOARD_SIZE,
    SCORE_DATA,
    MAX_LEVEL,
    TETROMINOS,
)


# TODO: add 7-bag randomizer
# TODO: add ghost piece
# TODO: add hold piece
# TODO: add soft drop scoring
# TODO: add animations
# TODO: add music and sound effects
# TODO: add pause functionality
# TODO: add start screen and game over screen
# TODO: add high score tracking
# TODO: add settings menu
# TODO: DAS and ARR implementation


class Game:
    def __init__(self):
        pygame.init()
        self.win = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True

        self.font = pygame.font.SysFont("comicsans", 30)

        horizontal_margin = WIDTH / HORIZONTAL_MARGIN_RATIO
        vertical_margin = HEIGHT / VERTICAL_MARGIN_RATIO
        # Calculate block size to fit the board within the window with margins
        # 20x * 10x = S
        # x = sqrt(S / 200)
        block_size = round(sqrt((WIDTH - 2 * horizontal_margin) * (HEIGHT - vertical_margin) / (BOARD_SIZE[0] * BOARD_SIZE[1])))
        self.board = Board(
            x=horizontal_margin,
            y=vertical_margin,
            block_size=block_size,
            )

        self.tetrominos = []
        self.tetromino = None
        self.game_over = False
        self.total_lines_cleared = 0
        self.score = 0
        self.level = 0

        pygame.display.set_caption("TETRIS")

    def run(self):
        while self.running:
            if self.game_over:
                self.running = False
                continue

            if self.tetromino is None:
                self.tetromino = self.get_tetromino()

            block_locked, lock_above = self.tetromino.fall()
            if block_locked:
                self.tetromino = self.get_tetromino()
            if lock_above:
                self.game_over = True
                continue
            
            self.calculate_score()
            self.check_level_up()
            self.check_events()
            self.update_window()
            self.clock.tick(FPS)  # Limit to 60 frames per second

        pygame.quit()

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                self.running = False
            if event.type == pygame.KEYDOWN:
                
                if event.key == pygame.K_LEFT:
                    self.tetromino.move(-1, 0)
                elif event.key == pygame.K_RIGHT:
                    self.tetromino.move(1, 0)
                    
                elif event.key == pygame.K_DOWN:
                    self.tetromino.move(0, 1)
                elif event.key == pygame.K_SPACE:
                    lock_above = self.tetromino.hard_drop()
                    if lock_above:
                        self.game_over = True
                    else:
                        self.tetromino = self.get_tetromino()

                elif event.key == pygame.K_UP:
                    self.tetromino.rotate(1)
                elif event.key == pygame.K_z:
                    self.tetromino.rotate(-1)

    def update_window(self):
        self.win.fill((0, 0, 0))  # Fill the window with black color
        self.print_stats()
        self.board.draw(self.win)
        self.tetromino.draw(self.win)
        pygame.display.flip()  # Update the display

    def get_tetromino(self):
        if not self.tetrominos:
            self.tetrominos = list(TETROMINOS.keys())
            shuffle(self.tetrominos)            
        return Tetromino(shape_name=self.tetrominos.pop(0), board=self.board, level=self.level)
    
    def check_level_up(self):
        new_level = self.total_lines_cleared // 10
        self.level = min(new_level, MAX_LEVEL)

    def calculate_score(self):
        lines = self.board.check_lines()
        if lines > 0:
            self.total_lines_cleared += lines
            self.score += SCORE_DATA[lines] * (self.level + 1)

    def print_stats(self):
        score_render = self.font.render(f"Score: {self.score}", 1, "yellow")
        level_render = self.font.render(f"Level: {self.level + 1}", 1, "yellow")
        self.win.blit(score_render, (0, 0))
        self.win.blit(level_render, (0, score_render.get_height() + 5))
        

if __name__ == "__main__":
    game = Game()
    game.run()
