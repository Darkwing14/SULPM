import fcurses
import time
import random
import sys
import os
import maze
from fcurses import Keyboard as key

# --- Constants ---
# Pac-Man emojis handled dynamically below
GHOST_GLYPH = '/\\'
CHERRY = fcurses.color('••', 'red')
DOT = '• '
POWER = fcurses.color('● ', 'yellow')
WALL = fcurses.color('██', 'blue')
EMPTY = '  '

DIRS = {
    'w': (0, -1, 'pacman_n'),
    's': (0, 1, 'pacman_s'),
    'a': (-1, 0, 'pacman_w'),
    'd': (1, 0, 'pacman_e')
}

# --- Maze layout (unchanged) ---
raw_maze = maze.the_map

# --- Build maze ---
maze = []
px = py = 0
ghosts = []
lives = 3
level = 1
score = 0
if len(sys.argv) > 3:
    level = int(sys.argv[1])
    lives = int(sys.argv[2])
    score = int(sys.argv[3])

for y, row in enumerate(raw_maze):
    new_row = []
    i = 0
    while i < len(row):
        cell = row[i:i+2]
        if cell == '||':
            new_row.append(WALL)
        elif cell == '..':
            new_row.append(DOT)
        elif cell == '[[':
            new_row.append(POWER)
        elif cell == '//':
            new_row.append(CHERRY)
        elif cell == '**':
            px, py = len(new_row), y
            sx, sy = len(new_row), y
            new_row.append(EMPTY)
        elif cell == '&&':
            ghosts.append((len(new_row), y))
            new_row.append(EMPTY)
        else:
            new_row.append(EMPTY)
        i += 2
    maze.append(new_row)
    
def lose_life():
    global px
    global py
    global lives
    lives -= 1
    if lives == 0:
        return True
    else:
        px, py = sx, sy
        return False

# Normalize maze width
W = max(len(row) for row in maze)
H = len(maze)
for row in maze:
    while len(row) < W:
        row.append(EMPTY)

while len(ghosts) < 4:
    ghosts.append((W - 2, 1))

# --- Initialize screen ---
screen = fcurses.display(W, H, square=True)
pac_dir = 'pacman_e'  # Default facing right
tick = 0
for r in range(H):
    for c in range(W):
        fcurses.snipe(r, c, maze[r][c], screen)
fcurses.render(screen)
fcurses.play('pacstart.mp3')
time.sleep(4)
scared = 0
# --- Game loop ---
while True:
    tick += 1
    # Draw maze
    for r in range(H):
        for c in range(W):
            fcurses.snipe(r, c, maze[r][c], screen)

    # Draw ghosts
    for i, (gx, gy) in enumerate(ghosts):
        if scared > 40:
            color_choice = 'blue'
        elif scared > 0:
            color_choice = 'white'
        else:
            color_choice = ['red', 'cyan', 'magenta', 'yellow'][i % 4]
        fcurses.snipe(gy, gx, fcurses.color(GHOST_GLYPH, color_choice), screen)

    # Draw Pac-Man
    fcurses.snipe(py, px, pac_dir, screen)
    fcurses.render(screen)
    print(f'Lives: {(fcurses.emoji("pacman_e") + " ") * lives}')
    print(f'Score: {score}')
    print(f'Level: {level}')

    # Move ghosts randomly
    new_ghosts = []
    for gx, gy in ghosts:
        dx, dy = random.choice([(0, -1), (0, 1), (-1, 0), (1, 0)])
        nx, ny = gx + dx, gy + dy
        if 0 <= nx < W and 0 <= ny < H and maze[ny][nx] != WALL:
            new_ghosts.append((nx, ny))
        else:
            new_ghosts.append((gx, gy))
    ghosts = new_ghosts

    # Move Pac-Man via WASD
    if key.is_any_pressed():
        ch = key.last_pressed().lower()
        if ch in DIRS:
            dx, dy, new_dir = DIRS[ch]
            nx, ny = px + dx, py + dy
            if 0 <= nx < W and 0 <= ny < H and maze[ny][nx] != WALL:
                px, py = nx, ny
                pac_dir = new_dir
                if maze[py][px] == DOT:
                    score += 1
                    if tick % 2 == 0 and not scared > 0:
                        fcurses.play('waka.wav')
                    maze[py][px] = EMPTY
                elif maze[py][px] == CHERRY:
                    score += 30
                    fcurses.play('gobble.mp3')
                    lives += 1
                    maze[py][px] = EMPTY
                elif maze[py][px] == POWER:
                    score += 10
                    fcurses.play('gobble.mp3')
                    scared = 60 + (60 / level) # shorter on hard levels.
                    maze[py][px] = EMPTY
                else:
                    if tick % 2 == 0 and not scared > 0:
                        fcurses.play('float.wav')
                        

    # Check collisions
    if scared > 0 and tick % 2 == 0:
        fcurses.play('scare.wav')
    
    if (px, py) in ghosts:
        if scared > 0:
            ghosts.pop(ghosts.index((px, py)))
            fcurses.play('gobble.mp3')
            score += 30
        else:
            time.sleep(1)
            fcurses.play('pacfail.mp3')
            fcurses.snipe(py, px, fcurses.color('--', 'yellow'), screen)
            fcurses.render(screen)
            time.sleep(3)
            if lose_life():
                fcurses.write(0, 0, 'Game Over!', screen)
                fcurses.render(screen)
                time.sleep(2)
                key.reset()
                break

    # Win condition
    if all(cell != DOT for row in maze for cell in row):
        score += 50
        for i in range(len(screen)):
            line = screen[i]
            for j in range(len(line)):
                char = line[j]
                if char == fcurses.color('██', 'blue'):
                    screen[i][j] = fcurses.color('██', 'white')
        fcurses.write(0, 0, 'You Win!', screen)
        fcurses.render(screen)
        time.sleep(2)
        key.reset()
        again = input('Play again? ').lower().startswith('y')
        if again:
            fcurses.play('coffee.mp3')
            time.sleep(11)
            os.system(f'python3 {sys.argv[0]} {level + 1} {lives} {score}')
        break

    time.sleep(0.15)
    scared -= 1
