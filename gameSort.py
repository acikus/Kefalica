import pygame
import random
import sys
import os
import threading
import tkinter as tk

# ---------------------------
# Global Constants (UI, etc.)
# ---------------------------
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 700  # Increased to accommodate multi-row layout
FPS = 30

VERTICAL_OFFSET = 120
TUBE_WIDTH = 70
TUBE_SPACING = 25
TOP_MARGIN = 150

# Colors
BG_COLOR = (255, 255, 255)
TUBE_FILL_COLOR = (173, 216, 230)
TUBE_HOVER_FILL_COLOR = (0, 236, 100)
TUBE_OUTLINE_COLOR = (50, 50, 50)
SELECTED_TUBE_OUTLINE_COLOR = (255, 0, 0)
BUTTON_COLOR = (100, 200, 100)
BUTTON_HOVER_COLOR = (150, 250, 0)
BUTTON_TEXT_COLOR = (0, 0, 0)
TEXT_COLOR = (0, 0, 0)

# ---------------------------
# Level Settings
# ---------------------------
LEVELS = {
    1: (3, 3, 1),
    2: (4, 4, 2),
    3: (5, 5, 2),
    4: (6, 4, 2),  # New level: 6 colors, capacity 4, 2 extra tubes
    5: (7, 5, 3)   # New level: 7 colors, capacity 5, 3 extra tubes
}
current_level = 1
MAX_LEVEL_COLORS = max(params[0] for params in LEVELS.values())  # Now 7

# ---------------------------
# Asset Loading
# ---------------------------
try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    current_dir = os.getcwd()

IMAGE_PATH1 = os.path.join(current_dir, "assets", "sort")
BALL_IMAGE_FILES = [os.path.join(IMAGE_PATH1, f"ball_{i}.png") for i in range(MAX_LEVEL_COLORS)]

def load_ball_images():
    images = []
    for filename in BALL_IMAGE_FILES:
        try:
            img = pygame.image.load(filename).convert_alpha()
            images.append(img)
        except pygame.error as e:
            print(f"Error loading image {filename}: {e}")
            pygame.quit()
            sys.exit()
    return images

# ---------------------------
# Game Functions
# ---------------------------
def create_tubes(NUM_COLORS, TUBE_CAPACITY, EXTRA_TUBES):
    NUM_FILLED_TUBES = NUM_COLORS
    color_list = []
    for color in range(NUM_COLORS):
        color_list.extend([color] * TUBE_CAPACITY)
    random.shuffle(color_list)
    total_tubes = NUM_FILLED_TUBES + EXTRA_TUBES
    tubes = [[] for _ in range(total_tubes)]
    idx = 0
    for t in range(NUM_FILLED_TUBES):
        for _ in range(TUBE_CAPACITY):
            tubes[t].append(color_list[idx])
            idx += 1
    return tubes

def is_valid_destination(selected_ball, dest_tube, tubes, TUBE_CAPACITY):
    if len(tubes[dest_tube]) >= TUBE_CAPACITY:
        return False
    if tubes[dest_tube] and tubes[dest_tube][-1] != selected_ball:
        return False
    return True

def check_win_condition(tubes, selected_ball, NUM_COLORS, TUBE_CAPACITY):
    if selected_ball is not None:
        return False
    completed_tubes = 0
    for tube in tubes:
        if len(tube) == TUBE_CAPACITY and all(ball == tube[0] for ball in tube):
            completed_tubes += 1
        elif len(tube) > 0:
            return False
    return completed_tubes == NUM_COLORS

def no_legal_moves(tubes, TUBE_CAPACITY):
    for i, tube in enumerate(tubes):
        if not tube:
            continue
        ball = tube[-1]
        for j, other in enumerate(tubes):
            if i == j:
                continue
            if len(other) < TUBE_CAPACITY and (not other or other[-1] == ball):
                return False
    return True

def reset_game_state(NUM_COLORS, TUBE_CAPACITY, EXTRA_TUBES):
    tubes = create_tubes(NUM_COLORS, TUBE_CAPACITY, EXTRA_TUBES)
    selected_ball = None
    selected_from = None
    return tubes, selected_ball, selected_from

# ---------------------------
# Main Game Loop
# ---------------------------
def main(parent=None):
    global current_level

    def run_game(dummy_window):
        global current_level
        pygame.init()
        pygame.font.init()
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Sorting")
        clock = pygame.time.Clock()

        NUM_COLORS, TUBE_CAPACITY, EXTRA_TUBES = LEVELS[current_level]
        # Tube height now scales directly with the capacity
        TUBE_HEIGHT = TUBE_CAPACITY * 60
        ball_images = load_ball_images()

        # Load background image
        bg_image_path = os.path.join(IMAGE_PATH1, "backSort.png")
        try:
            bg_image = pygame.image.load(bg_image_path).convert()
            bg_image = pygame.transform.scale(bg_image, (WINDOW_WIDTH, WINDOW_HEIGHT))
        except pygame.error as e:
            print(f"Error loading background image {bg_image_path}: {e}")
            pygame.quit()
            sys.exit()

        # Load tube image and rescale according to TUBE_HEIGHT
        tube_image_path = os.path.join(IMAGE_PATH1, "tube.png")
        try:
            original_tube_image = pygame.image.load(tube_image_path).convert_alpha()
            tube_image = pygame.transform.smoothscale(original_tube_image, (TUBE_WIDTH, TUBE_HEIGHT +40))
        except pygame.error as e:
            print(f"Error loading tube image {tube_image_path}: {e}")
            pygame.quit()
            sys.exit()

        # Level selector radio buttons
        level_buttons = []
        radio_radius = 10
        base_x = 20
        base_y = 20
        spacing = 100
        for lvl in sorted(LEVELS.keys()):
            rect = pygame.Rect(base_x + (lvl - 1) * spacing, base_y, radio_radius*2, radio_radius*2)
            level_buttons.append({'level': lvl, 'rect': rect})

        # Initialize game state
        tubes, selected_ball, selected_from = reset_game_state(NUM_COLORS, TUBE_CAPACITY, EXTRA_TUBES)
        game_over = False
        game_message = ""
        move_count = 0
        move_history = []
        final_time = None
        start_time = pygame.time.get_ticks()

        # Always-visible buttons
        always_button_width = 120
        always_button_height = 40
        undo_button_rect = pygame.Rect(WINDOW_WIDTH - 390, 20, always_button_width, always_button_height)
        restart_button_rect = pygame.Rect(WINDOW_WIDTH - 260, 20, always_button_width, always_button_height)
        exit_button_rect = pygame.Rect(WINDOW_WIDTH - 130, 20, always_button_width, always_button_height)

        # Overlay buttons
        overlay_button_width = 200
        overlay_button_height = 50
        new_game_button_rect = pygame.Rect(0, 0, overlay_button_width, overlay_button_height)
        end_button_rect = pygame.Rect(0, 0, overlay_button_width, overlay_button_height)
        new_game_button_rect.center = (WINDOW_WIDTH // 2 - overlay_button_width//2 - 10, WINDOW_HEIGHT - 70)
        end_button_rect.center = (WINDOW_WIDTH // 2 + overlay_button_width//2 + 10, WINDOW_HEIGHT - 70)

        # Fonts
        label_font = pygame.font.SysFont("Arial", 36)
        button_font = pygame.font.SysFont("Arial", 28)
        small_font = pygame.font.SysFont("Arial", 20)

        # Tube positions with multi-row support
        def recalc_tube_positions():
            max_tubes_per_row = 10
            row_spacing = 20
            tube_positions = []
            total_tubes = len(tubes)
            num_rows = (total_tubes + max_tubes_per_row - 1) // max_tubes_per_row
            for row in range(num_rows):
                tubes_in_this_row = min(max_tubes_per_row, total_tubes - row * max_tubes_per_row)
                total_width_row = tubes_in_this_row * TUBE_WIDTH + (tubes_in_this_row - 1) * TUBE_SPACING
                start_x = (WINDOW_WIDTH - total_width_row) // 2
                ty_row = TOP_MARGIN + VERTICAL_OFFSET + row * (TUBE_HEIGHT + row_spacing)
                for col in range(tubes_in_this_row):
                    tx = start_x + col * (TUBE_WIDTH + TUBE_SPACING)
                    tube_positions.append((tx, ty_row))
            return tube_positions

        tube_positions = recalc_tube_positions()

        running = True
        while running:
            clock.tick(FPS)
            mouse_pos = pygame.mouse.get_pos()

            if not game_over and selected_ball is None:
                if check_win_condition(tubes, selected_ball, NUM_COLORS, TUBE_CAPACITY):
                    game_over = True
                    game_message = "Congratulations! You solved it!"
                    final_time = pygame.time.get_ticks()
                elif no_legal_moves(tubes, TUBE_CAPACITY):
                    game_over = True
                    game_message = "No more legal moves!"
                    final_time = pygame.time.get_ticks()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Check level buttons
                    for btn in level_buttons:
                        if btn['rect'].collidepoint(mouse_pos):
                            if current_level != btn['level']:
                                current_level = btn['level']
                                NUM_COLORS, TUBE_CAPACITY, EXTRA_TUBES = LEVELS[current_level]
                                TUBE_HEIGHT = TUBE_CAPACITY * 60
                                tubes, selected_ball, selected_from = reset_game_state(NUM_COLORS, TUBE_CAPACITY, EXTRA_TUBES)
                                tube_positions = recalc_tube_positions()

                                # Rescale the tube image for the new capacity
                                tube_image = pygame.transform.smoothscale(original_tube_image, (TUBE_WIDTH, TUBE_HEIGHT + 40))

                                move_count = 0
                                move_history = []
                                game_over = False
                                game_message = ""
                                start_time = pygame.time.get_ticks()
                            break

                    # Check always-visible buttons
                    if undo_button_rect.collidepoint(mouse_pos) and selected_ball is None and move_history:
                        last_move = move_history.pop()
                        from_tube, to_tube = last_move
                        ball = tubes[to_tube].pop()
                        tubes[from_tube].append(ball)
                        move_count -= 1
                        game_over = False
                        game_message = ""
                        continue
                    elif restart_button_rect.collidepoint(mouse_pos):
                        tubes, selected_ball, selected_from = reset_game_state(NUM_COLORS, TUBE_CAPACITY, EXTRA_TUBES)
                        tube_positions = recalc_tube_positions()
                        move_count = 0
                        move_history = []
                        start_time = pygame.time.get_ticks()
                        game_over = False
                        game_message = ""
                        final_time = None

                        # Also rescale tube again (since TUBE_CAPACITY might have changed)
                        tube_image = pygame.transform.smoothscale(original_tube_image, (TUBE_WIDTH, TUBE_HEIGHT + 40))
                        continue
                    elif exit_button_rect.collidepoint(mouse_pos):
                        running = False
                        continue

                    # Game-over overlay buttons
                    if game_over:
                        if new_game_button_rect.collidepoint(mouse_pos):
                            tubes, selected_ball, selected_from = reset_game_state(NUM_COLORS, TUBE_CAPACITY, EXTRA_TUBES)
                            tube_positions = recalc_tube_positions()
                            move_count = 0
                            move_history = []
                            start_time = pygame.time.get_ticks()
                            game_over = False
                            game_message = ""
                            final_time = None

                            # Rescale tube for fresh start
                            tube_image = pygame.transform.smoothscale(original_tube_image, (TUBE_WIDTH, TUBE_HEIGHT))
                            continue
                        elif end_button_rect.collidepoint(mouse_pos):
                            running = False
                            continue

                    # Click in tubes (handling ball selection and placement)
                    if not game_over:
                        for i, (tx, ty) in enumerate(tube_positions):
                            tube_rect = pygame.Rect(tx, ty, TUBE_WIDTH, TUBE_HEIGHT)
                            if tube_rect.collidepoint(mouse_pos):
                                if selected_ball is None:
                                    # Pick up the top ball
                                    if tubes[i]:
                                        selected_ball = tubes[i].pop()
                                        selected_from = i
                                else:
                                    # Put down the selected ball (if valid) or cancel
                                    if i == selected_from:
                                        # Cancel selection
                                        tubes[selected_from].append(selected_ball)
                                        selected_ball = None
                                        selected_from = None
                                    elif is_valid_destination(selected_ball, i, tubes, TUBE_CAPACITY):
                                        move_history.append((selected_from, i))
                                        tubes[i].append(selected_ball)
                                        selected_ball = None
                                        selected_from = None
                                        move_count += 1
                                    else:
                                        # Invalid destination, cancel selection
                                        tubes[selected_from].append(selected_ball)
                                        selected_ball = None
                                        selected_from = None
                                break

            # --------------------------
            # Drawing everything
            # --------------------------
            screen.fill(BG_COLOR)

            # Draw the background FIRST so it doesn't cover buttons
            screen.blit(bg_image, (0, 0))

            # Draw level buttons (radio style)
            for btn in level_buttons:
                center = (btn['rect'].x + radio_radius, btn['rect'].y + radio_radius)
                if current_level == btn['level']:
                    pygame.draw.circle(screen, BUTTON_HOVER_COLOR, center, radio_radius)
                else:
                    pygame.draw.circle(screen, BUTTON_COLOR, center, radio_radius, 2)
                label = small_font.render(f"Level {btn['level']}", True, TEXT_COLOR)
                label_rect = label.get_rect(midleft=(btn['rect'].right + 10, center[1]))
                screen.blit(label, label_rect)

            # Timer and moves
            elapsed_ms = (final_time if game_over and final_time else pygame.time.get_ticks()) - start_time
            elapsed_seconds = elapsed_ms // 1000
            minutes = elapsed_seconds // 60
            seconds = elapsed_seconds % 60
            timer_text = f"Time: {minutes:02d}:{seconds:02d}"
            moves_text = f"Moves: {move_count}"
            label_font_render = pygame.font.SysFont("Arial", 36)
            screen.blit(label_font_render.render(timer_text, True, TEXT_COLOR), (20, 60))
            screen.blit(label_font_render.render(moves_text, True, TEXT_COLOR), (20, 100))

            # Always-visible buttons
            for rect, text, active in [
                (undo_button_rect, "Undo", selected_ball is None and bool(move_history)),
                (restart_button_rect, "Restart", True),
                (exit_button_rect, "Exit", True)
            ]:
                color = BUTTON_HOVER_COLOR if rect.collidepoint(mouse_pos) and active else BUTTON_COLOR
                pygame.draw.rect(screen, color, rect)
                text_surface = button_font.render(text, True, BUTTON_TEXT_COLOR)
                text_rect = text_surface.get_rect(center=rect.center)
                screen.blit(text_surface, text_rect)

            # --------------------------
            # Draw TUBES FIRST, then BALLS on top
            # --------------------------
            for i, (tx, ty) in enumerate(tube_positions):
                # 1) Draw the tube behind the balls
                screen.blit(tube_image, (tx, ty))

                # 2) Draw each ball on top of the tube
                for level_index, ball_color_index in enumerate(tubes[i]):
                    # Stack from the bottom upwards:
                    # The bottom slot is at (ty + TUBE_HEIGHT - one_ball_height),
                    # next ball is above that, etc.
                    # one_ball_height is roughly TUBE_HEIGHT//TUBE_CAPACITY,
                    # minus some small margin so they "sit" on each other neatly.
                    one_ball_height = TUBE_HEIGHT // TUBE_CAPACITY
                    ball_surface = ball_images[ball_color_index]
                    # Adjust widths and heights slightly for padding
                    ball_scaled = pygame.transform.smoothscale(
                        ball_surface,
                        (TUBE_WIDTH - 20, one_ball_height - 10)
                    )
                    # Compute the Y-position so they stack on top of each other
                    ball_bottom_y = ty + TUBE_HEIGHT - (level_index * (one_ball_height -15))
                    ball_rect = ball_scaled.get_rect(centerx=tx + TUBE_WIDTH // 2, bottom=ball_bottom_y)
                    screen.blit(ball_scaled, ball_rect)

                # 3) Highlight if this tube is selected
                if i == selected_from:
                    highlight_rect = pygame.Rect(tx, ty, TUBE_WIDTH, TUBE_HEIGHT)
                    pygame.draw.rect(screen, SELECTED_TUBE_OUTLINE_COLOR, highlight_rect, 3)

            # If we're carrying a selected ball, draw it last (so it's above everything)
            if selected_ball is not None:
                ball_surface = ball_images[selected_ball]
                # Scale the carried ball to match the tube's sizing
                one_ball_height = TUBE_HEIGHT // TUBE_CAPACITY
                ball_scaled = pygame.transform.smoothscale(
                    ball_surface,
                    (TUBE_WIDTH - 20, one_ball_height - 10)
                )
                # Position above the selected tube
                tx, ty = tube_positions[selected_from]
                # Just a bit above the top of the tube
                ball_rect = ball_scaled.get_rect(centerx=tx + TUBE_WIDTH // 2, bottom=ty - 10)
                screen.blit(ball_scaled, ball_rect)

            # Overlay if game over
            if game_over:
                overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
                overlay.fill((255, 255, 255, 180))
                screen.blit(overlay, (0, 0))
                message_surface = label_font.render(game_message, True, TEXT_COLOR)
                message_rect = message_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 20))
                screen.blit(message_surface, message_rect)

                for rect, text in [(new_game_button_rect, "New Game"), (end_button_rect, "End")]:
                    color = BUTTON_HOVER_COLOR if rect.collidepoint(mouse_pos) else BUTTON_COLOR
                    pygame.draw.rect(screen, color, rect)
                    text_surface = button_font.render(text, True, BUTTON_TEXT_COLOR)
                    text_rect = text_surface.get_rect(center=rect.center)
                    screen.blit(text_surface, text_rect)

            pygame.display.flip()

        pygame.quit()
        if dummy_window is not None:
            dummy_window.destroy()

    if parent:
        # Create a hidden dummy Toplevel to block the main switchboard.
        dummy = tk.Toplevel(parent)
        dummy.grab_set()
        dummy.withdraw()
        threading.Thread(target=run_game, args=(dummy,), daemon=True).start()
        parent.wait_window(dummy)
    else:
        run_game(None)


if __name__ == "__main__":
    main()
