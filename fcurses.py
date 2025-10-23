# fcurses.py
import os
import random
import time
__all__ = []

_tick = 0

def clear_line(r, screen):
    square = len(screen[0][0]) == 2 if screen[0] else False
    blank = '  ' if square else ' '
    for c in range(len(screen[0])):
        screen[r][c] = blank

def write(r, c, text, screen):
    # Alternative to icons exclusive to write: Kaomoji!
    keywords = {':skull:': '(X_X)', ':happy:': '(^_^)',
                ':sad:': '(*n*)', ':cry:': '(T-T)'}
    hang = False # deprecated feature.
    if not screen or r < 0 or r >= len(screen):
        return screen
    if not screen[0]:
        return screen

    height = len(screen)
    width = len(screen[0])
    first_cell = screen[0][0]
    cell_size = len(first_cell)  # 1 or 2
    blank_cell = ' ' * cell_size

    # --- Helper: safely write a string into a row starting at col c ---
    def _write_line(row_idx, start_col, char_list):
        if not (0 <= row_idx < height):
            return
        for i, ch in enumerate(char_list):
            col = start_col + i
            if col >= width:
                break
            if cell_size == 1:
                screen[row_idx][col] = ch if ch else ' '
            else:  # cell_size == 2
                # ch should be 2 chars; pad if needed
                if len(ch) == 1:
                    ch = ch + ' '
                elif len(ch) == 0:
                    ch = '  '
                elif len(ch) > 2:
                    ch = ch[:2]
                screen[row_idx][col] = ch

    # --- Prepare main text ---
    if hang:
        otext = text
        display_text = text.replace("g", "o").replace("j", ".").replace("y", "v")
    else:
        display_text = text

    # --- Convert display_text to cell list ---
    if cell_size == 1:
        main_cells = list(display_text)
    else:  # cell_size == 2
        padded = display_text if len(display_text) % 2 == 0 else display_text + ' '
        main_cells = [padded[i:i+2] for i in range(0, len(padded), 2)]

    # --- Write main line ---
    _write_line(r, c, main_cells)

    # --- Handle hang (descenders) ---
    if hang:
        descender_cells = []
        orig_chars = list(otext)

        if cell_size == 1:
            for ch in orig_chars:
                descender_cells.append('╯' if ch in 'gjy' else ' ')
        else:  # cell_size == 2
            for i in range(0, len(orig_chars), 2):
                ch1 = orig_chars[i] if i < len(orig_chars) else ' '
                ch2 = orig_chars[i+1] if i+1 < len(orig_chars) else ' '
                has_descender = (ch1 in 'gjy') or (ch2 in 'gjy')
                descender_cells.append('╯ ' if has_descender else '  ')

        _write_line(r + 1, c, descender_cells)

    return screen

def snipe(r, c, char, screen):
    if 0 <= r < len(screen) and 0 <= c < len(screen[0]):
        screen[r][c] = char
    return screen

def peek(r, c, screen):
    if 0 <= r < len(screen) and 0 <= c < len(screen[0]):
        return screen[r][c]
    return None

def draw_box(r1, c1, r2, c2, screen, *, dividers=None, relative=True, horizontal=False):
    # Top border
    snipe(r1, c1, '_lbe', screen)
    for c in range(c1 + 1, c2):
        snipe(r1, c, '_hmb', screen)
    snipe(r1, c2, '_rbe', screen)

    # Middle rows
    for r in range(r1 + 1, r2):
        snipe(r, c1, '_lbm', screen)
        snipe(r, c2, '_rbm', screen)

    # Bottom border
    snipe(r2, c1, '_lbe', screen)
    for c in range(c1 + 1, c2):
        snipe(r2, c, '_hmb', screen)
    snipe(r2, c2, '_rbe', screen)

    # Divider logic
    if dividers:
        if horizontal:
            for dr in dividers:
                row = r1 + dr if relative else dr
                if r1 < row < r2:
                    snipe(row, c1, '_lbe', screen)
                    for c in range(c1 + 1, c2):
                        snipe(row, c, '_hmb', screen)
                    snipe(row, c2, '_rbe', screen)
        else:
            for dc in dividers:
                col = c1 + dc if relative else dc
                if c1 < col < c2:
                    for r in range(r1 + 1, r2):
                        snipe(r, col, '_div', screen)

    return screen

def _even_or_odd_tick():
    return _tick % 2 == 0

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

class pyscreen:
    @staticmethod
    def clear():
        os.system('cls' if os.name == 'nt' else 'clear')

    @staticmethod
    def display(w, h):
        return [[False] * w for _ in range(h)]

    @staticmethod
    def snipe(r, c, screen):
        screen[r][c] = not screen[r][c]
        return screen

    @staticmethod
    def rendersingle(top, bottom):
        if top:
            return "█" if bottom else "▀"
        else:
            return "▄" if bottom else " "

    @staticmethod
    def render(screen):
        rows = len(screen)
        columns = len(screen[0])
        if len(screen) % 2 != 0:
            rows += 1
            screen.append([False] * columns)
        for i in range(rows // 2):
            for j in range(columns):
                print(pyscreen.rendersingle(screen[i * 2][j], screen[(i * 2) + 1][j]), end="")
            print()

def display(w, h, *, square=False):
    if square:
        return [['  '] * w for _ in range(h)]
    else:
        return [[' '] * w for _ in range(h)]
    
def render(screen):
    clear()
    rows = len(screen)
    columns = len(screen[0])
    for i in screen:
        for j in i:
            if j in emojis:
                print(emoji(j), end='')
            else:
                print(j, end='')
        print()
    global _tick
    _tick += 1
        
def bold(text):
    if text.endswith('\033[0m'):
        return f"\033[1m{text}"
    else:
        return f"\033[1m{text}\033[0m"
    
def italic(text):
    if text.endswith('\033[0m'):
        return f"\033[3m{text}"
    else:
        return f"\033[3m{text}\033[0m"

def underline(text):
    if text.endswith('\033[0m'):
        return f"\033[4m{text}"
    else:
        return f"\033[4m{text}\033[0m"
    
def invert(text):
    if text.endswith('\033[0m'):
        return f"\033[7m{text}"
    else:
        return f"\033[7m{text}\033[0m"
    
def strikethrough(text):
    if text.endswith('\033[0m'):
        return f"\033[9m{text}"
    else:
        return f"\033[9m{text}\033[0m"
    
def color(text, color):
    colors = {
        'black': 30,
        'red': 31,
        'yellow': 93,
        'green': 92,
        'cyan': 96,
        'blue': 34,
        'magenta': 95,
        'white': 97,
        'grey': 90,
        'gray': 90
        }
    if text.endswith('\033[0m'):
        return f"\033[{str(colors[color])}m{text}"
    else:
        return f"\033[{str(colors[color])}m{text}\033[0m"

def bullet():
    return '•'

def schar(identifier):
    schars = list('•°¿¡¶§٭♥🛡⚔')
    return schars[identifier]

def emoji(name):
    icon = emojis[name]
    if callable(icon):
        return icon()
    else:
        return icon
    
def _try_bash(cmd):
    cmd = os.system(cmd)
    if cmd != 0:
        return False
    return True

_try = True

def play(sound):
    global _try
    if _try_bash(f'play -q ~/.pyenv/sounds/{sound} &'):
        pass
    elif _try:
        Keyboard.reset()
        i_want_to_install = input('Would you like to APT install play?').lower().startswith('y')
        if i_want_to_install:
            _try = False
            if _try_bash('sudo apt install sox libsox-fmt-all'):
                pass
            elif _try_bash('sudo pacman -S sox'):
                pass
            elif _try_bash('sudo dnf install sox'):
                pass
            elif _try_bash('sudo zypper install sox'):
                pass
            elif _try_bash('sudo apk add sox'):
                pass
            else:
                print('FCURSES`s sound feature is not supported on your OS, we apologize for the inconvenience.')

        else:
            _try = False

emojis = { # Also known as icons
      'penguin': color('<', 'yellow') + bullet(),
      'smile': '(:',
      'happy': '(:',
      'sad': '):',
      'frown': '):',
      'mad': color(")<", 'red'),
      'angry': color(")<", 'red'),
      'mad': color(")<", 'red'),
      'fire': color("/\\", 'red'),
      'drop': color("L\\", 'blue'),
      'left': color('<-', 'magenta'),
      'right': color('->', 'magenta'),
      'up': color('/\\', 'magenta'),
      'down': color('\\/', 'magenta'),
      'perpendicular': color('-|', 'magenta'),
      'parallel': color('==', 'magenta'),
      'bullet': bullet() + " ",
      'star': lambda: color(random.choice([" +", "- ", " `", ". ", bullet() + " "]), "yellow"), # Thanks to qwen for reccomending LAMBDAs. Originally had bare code.
      'chicken': lambda: color("o", "red") + random.choice(["/", "\\"]),
      'gear': lambda: color(["x ", "+ "][_even_or_odd_tick()], "grey"),
      'nope': color('><', 'red'),
      'yeah': color('v/', 'green'),
      'orange': lambda: color("██", ["red", "yellow"][_even_or_odd_tick()]), # Please don't use this anyway.
      # Give it up for... BOX DRAWING EMOJIS! Now with 50% more keyboard-freindliness!
      '_hmb': '--', # Horizontal Middle of Box
      '_lbe': '+-', # Left Box End
      '_rbe': '-+', # Right Box End
      '_lbm': '| ', # Left Box Middle (vertical)
      '_rbm': ' |', # Right Box Middle (vertical)
      '_div': '||', # Divider
      '_crossing': '++', # Crossing (Intersection of _hmb and _div)
      # That was the last box drawing character
      'pacman_w': lambda: color(['()', '>)'][_tick % 2], 'yellow'),
      'pacman_e': lambda: color(['()', '(<'][_tick % 2], 'yellow'),
      'pacman_n': lambda: color(['()', '\\/'][_tick % 2], 'yellow'),
      'pacman_s': lambda: color(['()', '/\\'][_tick % 2], 'yellow'),
    }

def play_effect(screen, effect='firework', y=0, x=0, colo='red'):
    import copy, time  # local imports only

    backup = copy.deepcopy(screen)

    match effect:
        case 'firework':
            snipe(y, x, 'orange', screen)
            render(screen)
            time.sleep(0.2)

            # Ensure the base characters for color match the expected cell size if using square=True (2 chars)
            # color('==', colo) -> original '==' is 2 chars
            # color('//', colo) -> original '//' is 2 chars
            # color('\\\\', colo) -> original '\\\\' is 2 chars (literal backslash)
            # color('||', colo) -> original '||' is 2 chars
            line(y, x, '/', 2, color('//', colo), screen)
            line(y, x, '\\', 2, color('\\\\', colo), screen)
            line(y, x, '-', 2, color('==', colo), screen)
            line(y, x, '|', 2, color('||', colo), screen)
            snipe(y, x, '><', screen)
            render(screen)
            time.sleep(0.2)

        case 'sparkle':
            snipe(y, x, 'star', screen)
            render(screen)
            time.sleep(0.1)

        case 'eat':
            num_rows = len(screen)
            if num_rows == 0:
                # Nothing to "eat" if the screen has no rows
                return screen # Or continue to restore/render

            num_cols = len(screen[0]) if num_rows > 0 else 0 # Get number of columns from the first row
            if num_cols == 0:
                 # Nothing to "eat" if the rows have no columns
                 return screen # Or continue to restore/render

            # Iterate through each row of the screen
            for i in range(num_rows):
                current_row = screen[i]
                # Iterate through each column (cell) index in the current row
                for j in range(num_cols):
                    # Clear the cell at the current position (i, j)
                    snipe(i, j, '  ', screen) # Clear the current cell being "eaten"

                    # Place 'pacman_e' in the next cell (i, j+1) if it exists and if we are not on the last cell of the row
                    # This creates the effect of Pacman clearing the current cell and moving into the next
                    if j + 1 < num_cols:
                        snipe(i, j + 1, 'pacman_e', screen)

                    # Add a small delay to visualize the "eating" motion
                    time.sleep(0.01)
                    # Re-render the screen after each small step
                    render(screen)

                # After the inner loop finishes for row 'i', the last cell (i, num_cols-1) has been cleared ('  ').
                # The 'pacman_e' that was drawn in the previous step (when j=num_cols-2) is now in the last cell (i, num_cols-1).
                # We need to clear this trailing 'pacman_e' to finish processing this row.
                if num_cols > 0: # Check if there was at least one column to clear the potential trailing pac_e
                    snipe(i, num_cols - 1, "  ", screen)
                    render(screen) # Render again after clearing the trailing pac_e for this row
            # After all rows are processed, the whole screen should be blank ('  '),
            # and no trailing 'pacman_e' should remain.
            # The main backup/restore logic at the end of play_effect will handle reverting the screen.
        case 'target':
            snipe(y - 1, x, '||', screen)
            snipe(y + 1, x, '||', screen)
            snipe(y, x - 1, '--', screen)
            snipe(y, x + 1, '--', screen)
            render(screen)

    # restore old frame visually
    for r in range(len(screen)):
        for c in range(len(screen[0])):
            screen[r][c] = backup[r][c]

    clear()
    render(screen)
    return screen
            
def line(y, x, direction, radius, character='o', screen=None):
    """
    Draws a centered (bidirectional) line on the screen.

    Args:
        x, y: Center coordinates (column, row).
        direction: One of '-', '/', '|', or '\\'.
        radius: Half-length of the line (extends equally both ways).
        character: Character or emoji key to draw with.
        screen: The screen matrix to draw on.
    """
    if screen is None:
        raise ValueError("Screen not provided.")

    dirs = {
        '-': (1, 0),    # horizontal
        '|': (0, 1),    # vertical
        '/': (1, -1),   # upward-right
        '\\': (1, 1)    # downward-right
    }

    if direction not in dirs:
        raise ValueError("Invalid direction. Use '-', '/', '|', or '\\'.")

    dx, dy = dirs[direction]

    # Draw both sides from the center
    for i in range(-radius, radius + 1):
        cx = x + dx * i
        cy = y + dy * i
        snipe(cy, cx, character, screen)

    return screen

# --- fcurses Keyboard class ---
import sys
import os
_fallback = False

if os.name == 'nt':
    try:
        import msvcrt
    except ImportError:
        _fallback = True
else:
    try:
        import termios, tty, select, atexit
    except ImportError:
        _fallback = True

class Keyboard:
    _last = None
    _held = set()
    _raw_enabled = False
    _fd = None
    _old_settings = None

    @classmethod
    def _enable_raw(cls):
        if cls._raw_enabled or _fallback or os.name == 'nt':
            return
        cls._fd = sys.stdin.fileno()
        cls._old_settings = termios.tcgetattr(cls._fd)
        tty.setcbreak(cls._fd)
        cls._raw_enabled = True

        # Ensure terminal is restored at exit
        atexit.register(cls._restore)

    @classmethod
    def _restore(cls):
        if cls._raw_enabled and cls._fd and cls._old_settings:
            termios.tcsetattr(cls._fd, termios.TCSADRAIN, cls._old_settings)
            cls._raw_enabled = False

    @classmethod
    def _update(cls):
        if _fallback:
            return  # auto-answer mode

        cls._enable_raw()

        if os.name == 'nt':
            while msvcrt.kbhit():
                ch = msvcrt.getwch()
                if ch in ('\x03', '\x1A'):  # ignore Ctrl+C/Z
                    continue
                cls._last = ch
                cls._held.add(ch)
        else:
            # Unix non-blocking read
            while select.select([sys.stdin], [], [], 0)[0]:
                ch = sys.stdin.read(1)
                if ch in ('\x03', '\x1A'):
                    continue
                cls._last = ch
                cls._held.add(ch)

    @classmethod
    def last_pressed(cls):
        cls._update()
        if _fallback:
            return None
        return cls._last

    @classmethod
    def is_pressed(cls, key):
        cls._update()
        if _fallback:
            return True
        return key in cls._held
    
    @classmethod
    def s_is_pressed(cls, key):
        cls._update()
        if _fallback:
            return False
        if cls.is_any_pressed():
            if cls.last_pressed() == key:
                return True
            else:
                return False

    @classmethod
    def is_any_pressed(cls):
        cls._update()
        if _fallback:
            return True
        return bool(cls._held)

    @classmethod
    def clear(cls):
        cls._held.clear()
        cls._last = None
    
    @staticmethod
    def reset(): # If your program uses the keyboard, but not this, I am super dissapointed in you.
        if os.name != 'nt':
            os.system('reset')  # Unix only

