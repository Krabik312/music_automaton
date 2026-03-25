# ================================================
# ui.py
# ================================================

import pygame

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DARK_GRAY = (45, 45, 55)

BLUE_BTN = (0, 100, 200)
GREEN_BTN = (0, 160, 80)
YELLOW_BTN = (180, 140, 0)
RED_BTN = (180, 40, 40)

INSTRUMENT_COLOR = (100, 130, 180)

font_large = None
font_medium = None
font_small = None


def init_fonts():
    global font_large, font_medium, font_small
    font_large = pygame.font.SysFont("arial", 48, bold=True)
    font_medium = pygame.font.SysFont("arial", 32)
    font_small = pygame.font.SysFont("arial", 24)


settings_buttons = [
    {"rect": None, "text": "Лад: МАЖОР", "color": (80, 180, 100), "action": "toggle_scale"},
    {"rect": None, "text": "+", "color": (0, 180, 80), "action": "chaos_up"},
    {"rect": None, "text": "-", "color": (200, 60, 60), "action": "chaos_down"},
    {"rect": None, "text": "+", "color": (0, 180, 80), "action": "bpm_up"},
    {"rect": None, "text": "-", "color": (200, 60, 60), "action": "bpm_down"},
]

instrument_buttons = [
    {"rect": None, "text": "Гитара", "color": INSTRUMENT_COLOR, "action": "guitar"},
    {"rect": None, "text": "Пианино", "color": INSTRUMENT_COLOR, "action": "piano"},
]


def update_button_positions(WIDTH, HEIGHT):
    settings_buttons[0]["rect"] = pygame.Rect(100, 170, 280, 75)
    settings_buttons[1]["rect"] = pygame.Rect(430, 245, 55, 55)
    settings_buttons[2]["rect"] = pygame.Rect(500, 245, 55, 55)
    settings_buttons[3]["rect"] = pygame.Rect(430, 325, 55, 55)
    settings_buttons[4]["rect"] = pygame.Rect(500, 325, 55, 55)


def update_instrument_buttons(WIDTH, HEIGHT):
    base_x = 680
    for i, btn in enumerate(instrument_buttons):
        btn["rect"] = pygame.Rect(base_x + i * 160, 180, 140, 55)


def draw_ui(screen, automaton, track_melody, is_playing, current_melody_idx, bpm, WIDTH, HEIGHT,
            current_instrument="piano"):
    screen.fill(BLACK)

    title = font_large.render("Вероятностные автоматы: генератор музыки", True, WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 35))

    pygame.draw.rect(screen, DARK_GRAY, (70, 150, 520, 320), border_radius=20)

    # Кнопки настроек (лад, хаос, bpm)
    for btn in settings_buttons:
        pygame.draw.rect(screen, btn["color"], btn["rect"], border_radius=12)
        pygame.draw.rect(screen, WHITE, btn["rect"], width=4, border_radius=12)
        txt = font_medium.render(btn["text"], True, WHITE) if btn["action"] == "toggle_scale" else font_small.render(
            btn["text"], True, WHITE)
        screen.blit(txt, txt.get_rect(center=btn["rect"].center))

    screen.blit(font_medium.render(f"Хаос: {automaton.chaos:.1f}", True, WHITE), (100, 255))
    screen.blit(font_small.render("0 = музыкальные переходы    1 = полностью случайно", True, (200, 200, 200)),
                (100, 295))
    screen.blit(font_medium.render(f"Темп: {bpm} BPM", True, WHITE), (100, 325))

    # Кнопки инструментов
    for btn in instrument_buttons:
        thickness = 8 if btn["action"] == current_instrument else 4
        pygame.draw.rect(screen, btn["color"], btn["rect"], border_radius=12)
        pygame.draw.rect(screen, WHITE, btn["rect"], width=thickness, border_radius=12)
        txt = font_medium.render(btn["text"], True, WHITE)
        screen.blit(txt, txt.get_rect(center=btn["rect"].center))

    # === УБРАНА ЖЁЛТАЯ НАДПИСЬ ПРО МАРКОВСКУЮ ЦЕПЬ ===

    if track_melody:
        screen.blit(font_medium.render(f"Трек: {len(track_melody)} нот", True, (255, 240, 100)),
                    (WIDTH // 2 - 180, 560))
        notes_str = " → ".join(track_melody[:10]) + (" ..." if len(track_melody) > 10 else "")
        screen.blit(font_small.render(notes_str, True, WHITE), (WIDTH // 2 - 320, 600))

    if is_playing and track_melody:
        note_now = track_melody[current_melody_idx % len(track_melody)]
        screen.blit(font_medium.render(f"Мелодия: {note_now}", True, (100, 255, 140)), (WIDTH // 2 - 160, 670))

    # Основные кнопки снизу
    btns = [
        {"rect": pygame.Rect(80, HEIGHT - 140, 220, 80), "text": "Создать трек", "color": BLUE_BTN},
        {"rect": pygame.Rect(320, HEIGHT - 140, 220, 80), "text": "Запуск", "color": GREEN_BTN},
        {"rect": pygame.Rect(560, HEIGHT - 140, 220, 80), "text": "Пауза", "color": YELLOW_BTN},
        {"rect": pygame.Rect(800, HEIGHT - 140, 220, 80), "text": "Сброс", "color": RED_BTN},
        {"rect": pygame.Rect(WIDTH - 300, HEIGHT - 140, 220, 80), "text": "Выход", "color": RED_BTN},
    ]
    for btn in btns:
        pygame.draw.rect(screen, btn["color"], btn["rect"], border_radius=15)
        pygame.draw.rect(screen, WHITE, btn["rect"], width=4, border_radius=15)
        txt = font_medium.render(btn["text"], True, WHITE)
        screen.blit(txt, txt.get_rect(center=btn["rect"].center))

    hint = font_small.render("ESC — выход", True, (110, 110, 120))
    screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 45))

    pygame.display.flip()