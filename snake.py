#!/usr/bin/env python3
"""
Terminal Snake Game
Controls: WASD or Arrow Keys to move, Q to quit, P to pause
"""

import curses
import random
import time

# Game constants
SPEED_NORMAL = 0.12
SPEED_FAST = 0.07
SCORE_PER_FOOD = 10
SCORE_PER_SPECIAL = 30

DIRECTIONS = {
    curses.KEY_UP:    (-1,  0),
    curses.KEY_DOWN:  ( 1,  0),
    curses.KEY_LEFT:  ( 0, -1),
    curses.KEY_RIGHT: ( 0,  1),
    ord('w'): (-1,  0),
    ord('s'): ( 1,  0),
    ord('a'): ( 0, -1),
    ord('d'): ( 0,  1),
    ord('W'): (-1,  0),
    ord('S'): ( 1,  0),
    ord('A'): ( 0, -1),
    ord('D'): ( 0,  1),
}

OPPOSITE = {
    (-1, 0): (1, 0),
    (1, 0): (-1, 0),
    (0, -1): (0, 1),
    (0, 1): (0, -1),
}


def init_colors():
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_GREEN,   -1)   # snake head
    curses.init_pair(2, curses.COLOR_CYAN,    -1)   # snake body
    curses.init_pair(3, curses.COLOR_RED,     -1)   # normal food
    curses.init_pair(4, curses.COLOR_YELLOW,  -1)   # special food
    curses.init_pair(5, curses.COLOR_WHITE,   -1)   # border / text
    curses.init_pair(6, curses.COLOR_MAGENTA, -1)   # score / title


def draw_border(win, rows, cols):
    win.attron(curses.color_pair(5))
    win.border()
    title = " 🐍 SNAKE "
    win.addstr(0, (cols - len(title)) // 2, title)
    win.attroff(curses.color_pair(5))


def place_food(snake_set, rows, cols):
    while True:
        pos = (random.randint(1, rows - 2), random.randint(1, cols - 2))
        if pos not in snake_set:
            return pos


def draw_hud(win, score, high_score, level, paused, cols):
    hud = f" Score: {score}  Best: {high_score}  Level: {level} "
    if paused:
        hud += " [PAUSED] "
    win.attron(curses.color_pair(6) | curses.A_BOLD)
    win.addstr(0, 2, hud[:cols - 3])
    win.attroff(curses.color_pair(6) | curses.A_BOLD)


def game_over_screen(win, score, high_score, rows, cols):
    lines = [
        "  GAME OVER  ",
        f" Score: {score} ",
        f" Best:  {high_score} ",
        "",
        " [R] Restart  [Q] Quit ",
    ]
    r = rows // 2 - len(lines) // 2
    for i, line in enumerate(lines):
        c = max(0, (cols - len(line)) // 2)
        try:
            if i == 0:
                win.attron(curses.color_pair(3) | curses.A_BOLD)
                win.addstr(r + i, c, line)
                win.attroff(curses.color_pair(3) | curses.A_BOLD)
            else:
                win.attron(curses.color_pair(5))
                win.addstr(r + i, c, line)
                win.attroff(curses.color_pair(5))
        except curses.error:
            pass
    win.refresh()


def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.keypad(True)
    init_colors()

    rows, cols = stdscr.getmaxyx()
    if rows < 15 or cols < 30:
        stdscr.addstr(0, 0, "Terminal too small! Need at least 15x30.")
        stdscr.refresh()
        stdscr.getch()
        return

    high_score = 0

    while True:
        # --- Init game state ---
        snake = [(rows // 2, cols // 4 + i) for i in range(4, 0, -1)]
        snake_set = set(snake)
        direction = (0, 1)
        pending_dir = direction
        score = 0
        level = 1
        paused = False

        food = place_food(snake_set, rows, cols)
        special_food = None
        special_timer = 0
        special_interval = 50   # steps between special food appearances
        step_count = 0

        speed = SPEED_NORMAL

        game_active = True
        while game_active:
            # Input
            key = stdscr.getch()
            if key == ord('q') or key == ord('Q'):
                return
            if key == ord('p') or key == ord('P'):
                paused = not paused
            if key in DIRECTIONS:
                d = DIRECTIONS[key]
                if d != OPPOSITE.get(direction):
                    pending_dir = d

            if paused:
                time.sleep(0.05)
                stdscr.clear()
                draw_border(stdscr, rows, cols)
                draw_hud(stdscr, score, high_score, level, paused, cols)
                # draw snake & food even when paused
                for seg in snake[1:]:
                    if 0 < seg[0] < rows-1 and 0 < seg[1] < cols-1:
                        stdscr.attron(curses.color_pair(2))
                        stdscr.addch(seg[0], seg[1], ord('o'))
                        stdscr.attroff(curses.color_pair(2))
                head = snake[0]
                stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
                stdscr.addch(head[0], head[1], ord('@'))
                stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)
                stdscr.attron(curses.color_pair(3))
                stdscr.addch(food[0], food[1], ord('*'))
                stdscr.attroff(curses.color_pair(3))
                stdscr.refresh()
                continue

            direction = pending_dir
            step_count += 1

            # Move snake
            head = (snake[0][0] + direction[0], snake[0][1] + direction[1])

            # Wall collision
            if not (0 < head[0] < rows - 1 and 0 < head[1] < cols - 1):
                game_active = False
                break

            # Self collision
            if head in snake_set:
                game_active = False
                break

            snake.insert(0, head)
            snake_set.add(head)

            ate = False
            if head == food:
                score += SCORE_PER_FOOD
                ate = True
                food = place_food(snake_set, rows, cols)
                # Level up every 5 foods
                if score // (SCORE_PER_FOOD * 5) + 1 > level:
                    level += 1
                    speed = max(SPEED_FAST, speed - 0.01)

            elif special_food and head == special_food:
                score += SCORE_PER_SPECIAL
                ate = True
                special_food = None
                special_timer = 0

            if not ate:
                tail = snake.pop()
                snake_set.discard(tail)

            # Manage special food
            if special_food:
                special_timer -= 1
                if special_timer <= 0:
                    special_food = None
            if step_count % special_interval == 0 and not special_food:
                special_food = place_food(snake_set, rows, cols)
                special_timer = 25

            if score > high_score:
                high_score = score

            # Draw
            stdscr.clear()
            draw_border(stdscr, rows, cols)
            draw_hud(stdscr, score, high_score, level, paused, cols)

            # Food
            try:
                stdscr.attron(curses.color_pair(3) | curses.A_BOLD)
                stdscr.addch(food[0], food[1], ord('*'))
                stdscr.attroff(curses.color_pair(3) | curses.A_BOLD)
            except curses.error:
                pass

            # Special food
            if special_food:
                try:
                    stdscr.attron(curses.color_pair(4) | curses.A_BOLD)
                    stdscr.addch(special_food[0], special_food[1], ord('$'))
                    stdscr.attroff(curses.color_pair(4) | curses.A_BOLD)
                except curses.error:
                    pass

            # Snake body
            for seg in snake[1:]:
                try:
                    stdscr.attron(curses.color_pair(2))
                    stdscr.addch(seg[0], seg[1], ord('o'))
                    stdscr.attroff(curses.color_pair(2))
                except curses.error:
                    pass

            # Snake head
            try:
                stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
                stdscr.addch(snake[0][0], snake[0][1], ord('@'))
                stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)
            except curses.error:
                pass

            # Help line at bottom
            help_text = " WASD/Arrows: move  P: pause  Q: quit "
            try:
                stdscr.attron(curses.color_pair(5))
                stdscr.addstr(rows - 1, max(0, (cols - len(help_text)) // 2), help_text[:cols - 1])
                stdscr.attroff(curses.color_pair(5))
            except curses.error:
                pass

            stdscr.refresh()
            time.sleep(speed)

        # Game over
        stdscr.clear()
        draw_border(stdscr, rows, cols)
        game_over_screen(stdscr, score, high_score, rows, cols)
        stdscr.nodelay(False)
        while True:
            k = stdscr.getch()
            if k in (ord('r'), ord('R')):
                break
            if k in (ord('q'), ord('Q')):
                return
        stdscr.nodelay(True)


if __name__ == "__main__":
    curses.wrapper(main)
