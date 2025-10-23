#!/usr/bin/env python3
import curses, sys, os

filename = sys.argv[1] if len(sys.argv) > 1 else input('filename? ')
os.system(f"touch '{filename}'")

try:
    lines = open(filename).read().splitlines()
except FileNotFoundError:
    lines = [""]

if not lines:
    lines = [""]  # always have at least one line

def main(stdscr):
    global lines   # we're using the outer variable

    curses.curs_set(1)
    stdscr.keypad(True)
    y, x = 0, 0   # logical line + column
    scroll = 0    # top visible wrapped line

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()
        wrap_width = max(1, width - 1)

        # --- build wrapped screen map ---
        screen_map = []  # [(line_index, chunk_start, chunk_text, is_continuation)]
        for i, line in enumerate(lines):
            if not line:
                screen_map.append((i, 0, "", False))
                continue
            for j in range(0, len(line), wrap_width):
                chunk = line[j:j+wrap_width]
                screen_map.append((i, j, chunk, j > 0))

        # --- find cursor screen position ---
        cursor_y, cursor_x = 0, 0
        for row, (li, start, chunk, cont) in enumerate(screen_map):
            if li == y and start <= x < start + wrap_width:
                cursor_y = row
                cursor_x = x - start
                break

        # --- adjust scroll ---
        if cursor_y < scroll:
            scroll = cursor_y
        elif cursor_y >= scroll + height:
            scroll = cursor_y - height + 1

        # --- draw visible area ---
        for i, (li, start, chunk, cont) in enumerate(screen_map[scroll:scroll+height]):
            try:
                if cont:
                    stdscr.addstr(i, 0, chunk, curses.A_UNDERLINE)
                else:
                    stdscr.addstr(i, 0, chunk)
            except curses.error:
                pass

        # --- place cursor ---
        if 0 <= cursor_y - scroll < height and 0 <= cursor_x < width:
            try:
                stdscr.move(cursor_y - scroll, cursor_x)
            except curses.error:
                pass

        stdscr.refresh()

        # --- input handling ---
        try:
            c = stdscr.get_wch()
        except curses.error:
            continue

        if c == '\x1b':  # ESC quits
            break
        elif c == curses.KEY_UP:
            y = max(0, y - 1)
            x = min(x, len(lines[y]))
        elif c == curses.KEY_DOWN:
            y = min(len(lines) - 1, y + 1)
            x = min(x, len(lines[y]))
        elif c == curses.KEY_LEFT:
            if x > 0:
                x -= 1
            elif y > 0:
                y -= 1
                x = len(lines[y])
        elif c == curses.KEY_RIGHT:
            if x < len(lines[y]):
                x += 1
            elif y < len(lines) - 1:
                y += 1
                x = 0
        elif c in ('\b', '\x7f', curses.KEY_BACKSPACE):
            if x > 0:
                lines[y] = lines[y][:x - 1] + lines[y][x:]
                x -= 1
            elif y > 0:
                x = len(lines[y - 1])
                lines[y - 1] += lines[y]
                lines.pop(y)
                y -= 1
            if not lines:  # keep at least one line
                lines = [""]
                y, x = 0, 0
        elif c == '\n':
            lines.insert(y + 1, lines[y][x:])
            lines[y] = lines[y][:x]
            y += 1
            x = 0
        elif isinstance(c, str):
            lines[y] = lines[y][:x] + c + lines[y][x:]
            x += 1

    open(filename, "w").write("\n".join(lines))

curses.wrapper(main)
