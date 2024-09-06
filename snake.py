"""Snake implemented with pyxel.

This is the game of snake in pyxel version!

Try and collect the tasty apples without running
into the side or yourself.

Controls are the arrow keys ← ↑ → ↓

Q: Quit the game
R: Restart the game

Created by Marcus Croucher in 2018.
"""

from collections import deque, namedtuple

import pyxel

from dataclasses import dataclass

SCALING_RATIO = 4


@dataclass
class Point:
    x: int
    y: int

    @property
    def draw_x(self):
        return self.x * SCALING_RATIO

    @property
    def draw_y(self):
        return self.y * SCALING_RATIO

    def __repr__(self):
        return f"Point({self.x}, {self.y}))"

    def __hash__(self):
        return 1000 * self.x + self.y


# Point = namedtuple("Point", ["x", "y"])  # Convenience class for coordinates

#############
# Constants #
#############

COL_MAGENTA = 1
COL_LIGHT_YELLOW = 2
COL_ORANGE = 3
COL_BLUE = 4
COL_WHITE = 5
COL_BLACK = 6
COL_GREEN = 7
COL_PINK = 8

TEXT_DEATH = ["GAME OVER", "(Q)UIT", "(R)ESTART"]
HEIGHT_DEATH = 5

WIDTH = 30
HEIGHT = 45

DRAW_WIDTH = SCALING_RATIO * WIDTH
DRAW_HEIGHT = SCALING_RATIO * HEIGHT

HEIGHT_SCORE = pyxel.FONT_HEIGHT
HEIGHT_CONTROLS = HEIGHT_SCORE * 2

UP = Point(0, -1)
DOWN = Point(0, 1)
RIGHT = Point(1, 0)
LEFT = Point(-1, 0)

START = Point(5, 5 + HEIGHT_SCORE)

SCORE_SPEED = {
    0: 6,
    3: 5,
    7: 4,
    12: 3,
    20: 2,
    50: 1
}


###################
# The game itself #
###################

def define_colors():
    pyxel.colors[COL_MAGENTA] = 0xCC0066
    pyxel.colors[COL_LIGHT_YELLOW] = 0xC97D23
    pyxel.colors[COL_ORANGE] = 0xD0953B
    pyxel.colors[COL_BLUE] = 0x4b34a3
    pyxel.colors[COL_BLACK] = 0x000000
    pyxel.colors[COL_WHITE] = 0xffffff
    pyxel.colors[COL_GREEN] = 0x74b2b2
    pyxel.colors[COL_PINK] = 0xc43486


class Snake:
    """The class that sets up and runs the game."""

    def __init__(self):
        """Initiate pyxel, set up initial game variables, and run."""

        pyxel.init(
            DRAW_WIDTH, DRAW_HEIGHT, title="Snake!", fps=60, display_scale=8, capture_scale=6
        )
        define_colors()
        define_sound_and_music()
        self.reset()
        pyxel.mouse(visible=True)
        pyxel.run(self.update, self.draw)

    def reset(self):
        """Initiate key variables (direction, snake, apple, score, etc.)"""

        self.direction = RIGHT
        self.snake = deque()
        self.snake.append(START)
        self.death = False
        self.score = 0
        self.generate_fruit()
        self.speed = 6
        self.frame_count = 0
        self.mouse_pressed_button = None

        pyxel.playm(0, loop=True)

    ##############
    # Game logic #
    ##############

    def update(self):
        """Update logic of game.
        Updates the snake and checks for scoring/win condition."""
        self.frame_count += 1
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            self.check_button_hitboxes()
        if not self.death:
            self.update_direction()
            if self.frame_count % self.speed == 0:
                self.update_snake()
                self.check_death()
                self.check_fruit()

        if pyxel.btn(pyxel.KEY_Q):
            pyxel.quit()

        if pyxel.btnp(pyxel.KEY_R) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A):
            self.reset()

    def check_button_hitboxes(self):
        x = pyxel.mouse_x
        y = pyxel.mouse_y
        button_height = HEIGHT_CONTROLS * SCALING_RATIO // 2 - 1
        button_width = DRAW_WIDTH // 3 - 2

        upper_row_high = DRAW_HEIGHT + 1 - HEIGHT_CONTROLS * SCALING_RATIO
        upper_row_low = upper_row_high + button_height

        lower_row_high = DRAW_HEIGHT + 1 - HEIGHT_CONTROLS * SCALING_RATIO // 2
        lower_row_low = lower_row_high + button_height

        first_col_left = 2
        first_col_right = first_col_left + button_width

        second_col_left = DRAW_WIDTH // 3 + 1
        second_col_right = second_col_left + button_width

        third_col_left = 2 * DRAW_WIDTH // 3
        third_col_right = third_col_left + button_width

        hitboxes = dict(
            up=[upper_row_high, upper_row_low, second_col_left, second_col_right],
            down=[lower_row_high, lower_row_low, second_col_left, second_col_right],
            left=[lower_row_high, lower_row_low, first_col_left, first_col_right],
            right=[lower_row_high, lower_row_low, third_col_left, third_col_right])
        print(hitboxes)
        print(x)
        print(y)
        for key, hitbox in hitboxes.items():
            if (hitbox[2] < x < hitbox[3]) & (hitbox[0] < y < hitbox[1]):
                print(key)
                self.mouse_pressed_button = key

        return None
    def update_direction(self):
        """Watch the keys and change direction."""
        if self.mouse_pressed_button:
            match self.mouse_pressed_button:
                case 'up':
                    if self.direction is not DOWN:
                        self.direction = UP
                case 'down':
                    if self.direction is not UP:
                        self.direction = DOWN
                case 'left':
                    if self.direction is not RIGHT:
                        self.direction = LEFT
                case 'right':
                    if self.direction is not LEFT:
                        self.direction = RIGHT
            self.mouse_pressed_button = None
        else:
            if pyxel.btn(pyxel.KEY_UP) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_UP):
                if self.direction is not DOWN:
                    self.direction = UP
            elif pyxel.btn(pyxel.KEY_DOWN) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN):
                if self.direction is not UP:
                    self.direction = DOWN
            elif pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT):
                if self.direction is not RIGHT:
                    self.direction = LEFT
            elif pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT):
                if self.direction is not LEFT:
                    self.direction = RIGHT

    def update_snake(self):
        """Move the snake based on the direction."""

        old_head = self.snake[0]
        new_head = Point(old_head.x + self.direction.x, old_head.y + self.direction.y)
        self.snake.appendleft(new_head)
        self.popped_point = self.snake.pop()

    def check_fruit(self):
        if SCORE_SPEED.get(self.score) is not None:
            self.check_melon()
        else:
            self.check_apple()

    def check_melon(self):
        if {self.snake[0]}.intersection(set(self.melon)):
            self.score += 1
            self.generate_fruit()
            self.snake.append(self.popped_point)
            self.speed = self.speed - 1

            pyxel.play(0, 0)

    def check_apple(self):
        """Check whether the snake is on an apple."""

        if self.snake[0] == self.apple:
            self.score += 1
            self.snake.append(self.popped_point)
            self.generate_fruit()

            pyxel.play(0, 0)

    def generate_fruit(self):
        if SCORE_SPEED.get(self.score) is not None:
            self.generate_melon()
        else:
            self.generate_apple()

    def generate_apple(self):
        """Generate an apple randomly."""
        snake_pixels = set(self.snake)

        self.apple = self.snake[0]
        while self.apple in snake_pixels:
            x = pyxel.rndi(0, WIDTH - 1)
            y = pyxel.rndi(HEIGHT_SCORE + 1, HEIGHT - HEIGHT_CONTROLS - 1)
            self.apple = Point(x, y)

    def melon_points(self, x, y):
        return [Point(x, y), Point(x + 1, y), Point(x, y + 1), Point(x + 1, y + 1)]

    def generate_melon(self):
        """Generate an apple randomly."""
        snake_pixels = set(self.snake)

        self.melon = self.melon_points(self.snake[0].x, self.snake[0].y)
        while set(self.melon).intersection(snake_pixels):
            x = pyxel.rndi(0, WIDTH - 1)
            y = pyxel.rndi(HEIGHT_SCORE + 1, HEIGHT - HEIGHT_CONTROLS - 1)
            self.melon = self.melon_points(x, y)

    def check_death(self):
        """Check whether the snake has died (out of bounds or doubled up.)"""

        head = self.snake[0]
        if head.x < 0 or head.y < HEIGHT_SCORE or head.x >= WIDTH or head.y >= HEIGHT - HEIGHT_CONTROLS:
            self.death_event()
        elif len(self.snake) != len(set(self.snake)):
            self.death_event()

    def death_event(self):
        """Kill the game (bring up end screen)."""
        self.death = True  # Check having run into self

        pyxel.stop()
        pyxel.play(0, 1)

    ##############
    # Draw logic #
    ##############

    def draw(self):
        """Draw the background, snake, score, and apple OR the end screen."""

        if not self.death:
            pyxel.cls(col=COL_MAGENTA)
            self.draw_snake()
            self.draw_score()
            self.draw_fruit()
            self.draw_controls()
            # pyxel.pset(self.apple.x, self.apple.y, col=COL_APPLE)

        else:
            self.draw_death()

    def draw_fruit(self):
        if SCORE_SPEED.get(self.score) is not None:
            self.draw_melon()
        else:
            self.draw_apple()

    def draw_apple(self):
        pyxel.rect(self.apple.draw_x, self.apple.draw_y, w=SCALING_RATIO, h=SCALING_RATIO, col=COL_PINK)
        pyxel.rectb(self.apple.draw_x, self.apple.draw_y, w=SCALING_RATIO, h=SCALING_RATIO, col=COL_LIGHT_YELLOW)

        greenery_offset = SCALING_RATIO // 2
        pyxel.pset(self.apple.draw_x + greenery_offset, self.apple.draw_y - 1, COL_GREEN)
        pyxel.pset(self.apple.draw_x + greenery_offset + 1, self.apple.draw_y - 2, COL_GREEN)
        pyxel.pset(self.apple.draw_x, self.apple.draw_y, col=COL_MAGENTA)

    def draw_melon(self):
        pyxel.rect(self.melon[0].draw_x, self.melon[0].draw_y, w=SCALING_RATIO * 2, h=SCALING_RATIO * 2, col=COL_GREEN)

    def draw_snake(self):
        """Draw the snake with a distinct head by iterating through deque."""

        for i, point in enumerate(self.snake):
            if i == 0:
                colour = COL_ORANGE
            else:
                colour = COL_LIGHT_YELLOW

            pyxel.rect(point.draw_x, point.draw_y, w=SCALING_RATIO, h=SCALING_RATIO, col=colour)

    def draw_score(self):
        """Draw the score at the top."""

        score = f"{self.score:04}"
        pyxel.rect(0, 0, DRAW_WIDTH, HEIGHT_SCORE * SCALING_RATIO, COL_BLACK)
        pyxel.text(1, 1, score, COL_WHITE)

    def draw_controls(self):
        """Draw the score at the top."""

        pyxel.rect(x=0,
                   y=DRAW_HEIGHT - HEIGHT_CONTROLS * SCALING_RATIO,
                   w=DRAW_WIDTH,
                   h=HEIGHT_CONTROLS * SCALING_RATIO,
                   col=COL_BLACK)
        button_width = DRAW_WIDTH // 3 - 2
        button_height = HEIGHT_CONTROLS * SCALING_RATIO // 2 - 1
        upper_row = DRAW_HEIGHT + 1 - HEIGHT_CONTROLS * SCALING_RATIO
        lower_row = DRAW_HEIGHT + 1 - HEIGHT_CONTROLS * SCALING_RATIO // 2
        button_color = COL_MAGENTA
        self.draw_button(DRAW_WIDTH // 3 + 1,
                         y=upper_row,
                         w=button_width,
                         h=button_height,
                         col=button_color, text='UP', text_col=COL_WHITE, pressed_col=COL_PINK)
        self.draw_button(DRAW_WIDTH // 3 + 1,
                         y=lower_row,
                         w=button_width,
                         h=button_height,
                         col=button_color, text='DOWN', text_col=COL_WHITE, pressed_col=COL_PINK)
        self.draw_button(2,
                         y=lower_row,
                         w=button_width,
                         h=button_height,
                         col=button_color, text='LEFT', text_col=COL_WHITE, pressed_col=COL_PINK)
        self.draw_button(2 * DRAW_WIDTH // 3,
                         y=lower_row,
                         w=button_width,
                         h=button_height,
                         col=button_color, text='RIGHT', text_col=COL_WHITE, pressed_col=COL_PINK)
        pyxel.text(1, 1 + DRAW_HEIGHT - HEIGHT_CONTROLS * SCALING_RATIO, 'HELLO', COL_WHITE)

    def draw_button(self, x, y, w, h, col, text, text_col, pressed_col):
        if text.lower == self.mouse_pressed_button:
            col = pressed_col
        pyxel.rect(x, y, w, h, col)
        text_x = self.center_button_text(text, x, w)
        pyxel.text(text_x, y + 3, text, text_col)

    def draw_death(self):
        """Draw a blank screen with some text."""

        pyxel.cls(col=COL_WHITE)
        display_text = TEXT_DEATH[:]
        display_text.insert(1, f"{self.score:04}")
        for i, text in enumerate(display_text):
            y_offset = (pyxel.FONT_HEIGHT + 2) * i
            text_x = self.center_text(text, DRAW_WIDTH)
            pyxel.text(text_x, HEIGHT_DEATH + y_offset, text, COL_MAGENTA)

    @staticmethod
    def center_text(text, page_width, char_width=pyxel.FONT_WIDTH):
        """Helper function for calculating the start x value for centered text."""

        text_width = len(text) * char_width
        return (page_width - text_width) // 2

    @staticmethod
    def center_button_text(text, button_x, button_width, char_width=pyxel.FONT_WIDTH):
        """Helper function for calculating the start x value for centered text."""

        text_width = len(text) * char_width

        return button_x + (button_width - text_width) // 2


###########################
# Music and sound effects #
###########################


def define_sound_and_music():
    """Define sound and music."""

    # Sound effects
    pyxel.sounds[0].set(
        notes="c3e3g3c4c4", tones="s", volumes="4", effects=("n" * 4 + "f"), speed=7
    )
    pyxel.sounds[1].set(
        notes="f3 b2 f2 b1  f1 f1 f1 f1",
        tones="p",
        volumes=("4" * 4 + "4321"),
        effects=("n" * 7 + "f"),
        speed=9,
    )

    melody1 = (
            "c3 c3 c3 d3 e3 r e3 r"
            + ("r" * 8)
            + "e3 e3 e3 f3 d3 r c3 r"
            + ("r" * 8)
            + "c3 c3 c3 d3 e3 r e3 r"
            + ("r" * 8)
            + "b2 b2 b2 f3 d3 r c3 r"
            + ("r" * 8)
    )

    melody2 = (
            "rrrr e3e3e3e3 d3d3c3c3 b2b2c3c3"
            + "a2a2a2a2 c3c3c3c3 d3d3d3d3 e3e3e3e3"
            + "rrrr e3e3e3e3 d3d3c3c3 b2b2c3c3"
            + "a2a2a2a2 g2g2g2g2 c3c3c3c3 g2g2a2a2"
            + "rrrr e3e3e3e3 d3d3c3c3 b2b2c3c3"
            + "a2a2a2a2 c3c3c3c3 d3d3d3d3 e3e3e3e3"
            + "f3f3f3a3 a3a3a3a3 g3g3g3b3 b3b3b3b3"
            + "b3b3b3b4 rrrr e3d3c3g3 a2g2e2d2"
    )

    # Music
    pyxel.sounds[2].set(
        notes=melody1 * 2 + melody2 * 2,
        tones="s",
        volumes=("3"),
        effects=("nnnsffff"),
        speed=20,
    )

    harmony1 = (
            "a1 a1 a1 b1  f1 f1 c2 c2"
            "c2 c2 c2 c2  g1 g1 b1 b1"
            * 3
            + "f1 f1 f1 f1 f1 f1 f1 f1 g1 g1 g1 g1 g1 g1 g1 g1"
    )
    harmony2 = (
            ("f1" * 8 + "g1" * 8 + "a1" * 8 + ("c2" * 7 + "d2")) * 3 + "f1" * 16 + "g1" * 16
    )

    pyxel.sounds[3].set(
        notes=harmony1 * 2 + harmony2 * 2, tones="t", volumes="5", effects="f", speed=20
    )
    pyxel.sounds[4].set(
        notes=("f0 r a4 r  f0 f0 a4 r" "f0 r a4 r   f0 f0 a4 f0"),
        tones="n",
        volumes="6622 6622 6622 6426",
        effects="f",
        speed=20,
    )

    pyxel.musics[0].set([], [2], [3], [4])


Snake()
