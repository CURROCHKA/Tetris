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
    HOLD_BOARD_SIZE,
    NEXT_BOARD_SIZE,
    SCORE_DATA,
    MAX_LEVEL,
    TETROMINOS,
    SOFT_DROP_DELAY,
)


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
            board_size=BOARD_SIZE,
            )

        self.hold_board = Board(
            x=horizontal_margin / 2 - HOLD_BOARD_SIZE[0] * block_size / 2,
            y=vertical_margin,
            block_size=block_size,
            board_size=HOLD_BOARD_SIZE,
        )

        self.next_board = Board(
            x=WIDTH - horizontal_margin / 2 - NEXT_BOARD_SIZE[0] * block_size / 2,
            y=vertical_margin,
            block_size=block_size,
            board_size=NEXT_BOARD_SIZE,
        )

        self.tetrominos = []
        self.tetromino = None
        self.hold = None
        self.hold_swapped = False

        self.soft_drop = False
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
            elif self.soft_drop:
                self.score += 1  # 1 point per soft drop cell
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
        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[pygame.K_DOWN] or pressed_keys[pygame.K_s]:
            if not self.soft_drop:
                self.soft_drop = True
                self.tetromino.change_fall_delay(SOFT_DROP_DELAY)

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                self.running = False
            if event.type == pygame.KEYDOWN:
                
                if event.key == pygame.K_LEFT:
                    self.tetromino.move(-1, 0)
                elif event.key == pygame.K_RIGHT:
                    self.tetromino.move(1, 0)
                    
                # elif event.key == pygame.K_DOWN:
                #     self.tetromino.move(0, 1)
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

                elif event.key == pygame.K_c:
                    if not self.hold_swapped:
                        self.swap_hold()

            if event.type == pygame.KEYUP:
                if event.key in (pygame.K_DOWN, pygame.K_s):
                    self.soft_drop = False
                    self.tetromino.reset_fall_delay()

    def update_window(self):
        self.win.fill((0, 0, 0))  # Fill the window with black color
    
        self.print_stats()

        self.board.draw(self.win)
        self.hold_board.draw(self.win)
        self.next_board.draw(self.win)

        self.tetromino.draw(self.win)
        pygame.display.flip()  # Update the display

    def get_tetromino(self):
        if len(self.tetrominos) < 7:
            new_bag = list(TETROMINOS.keys())
            shuffle(new_bag)
            self.tetrominos.extend(new_bag)

        tetromino_name = self.tetrominos.pop(0)
        
        self.next_board.reset()

        for idx, shape_name in enumerate(self.tetrominos[:3]):
            temp_tetromino = Tetromino(shape_name=shape_name, board=self.board)
            temp_tetromino.swap_board(self.next_board, y=idx * 4 + 1, lock=True)

        self.hold_swapped = False    
        return Tetromino(shape_name=tetromino_name, board=self.board, level=self.level)
    
    def check_level_up(self):
        new_level = self.total_lines_cleared // 10
        self.level = min(new_level, MAX_LEVEL)

    def calculate_score(self):
        lines = self.board.check_lines()
        if lines > 0:
            self.total_lines_cleared += lines
            self.score += SCORE_DATA[lines] * (self.level + 1)

    def swap_hold(self):
        if self.hold is None:
            self.hold = self.tetromino
            self.hold.swap_board(self.hold_board, y=1, lock=True)
            
            self.tetromino = self.get_tetromino()
        else:
            self.hold, self.tetromino = self.tetromino, self.hold

            self.hold.swap_board(self.hold_board, y=1, board_reset=True, lock=True)

            self.tetromino.swap_board(self.board)
        self.hold_swapped = True

    def print_stats(self):
        score_render = self.font.render(f"Score: {self.score}", 1, "yellow")
        level_render = self.font.render(f"Level: {self.level + 1}", 1, "yellow")
        self.win.blit(score_render, (0, 0))
        self.win.blit(level_render, (0, score_render.get_height() + 5))
        

if __name__ == "__main__":
    game = Game()
    game.run()
