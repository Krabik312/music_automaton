# ================================================
# main.py
# ================================================

import pygame
import sys
import ctypes
import random
from music_engine import (ProbabilisticAutomaton,
                           initialize_sounds,
                           play_step,
                           MAJOR_NOTES,
                           MINOR_NOTES,
                           SOUNDS_CONFIG)

from ui import (draw_ui,
                update_button_positions,
                update_instrument_buttons,   # ← добавлено
                settings_buttons,
                instrument_buttons,          # ← добавлено
                init_fonts)

ctypes.windll.user32.SetProcessDPIAware()

pygame.init()
pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=4096)
pygame.mixer.init()

init_fonts()

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("Вероятностные автоматы: генератор музыки")

clock = pygame.time.Clock()
FPS = 60

# Инициализация
automaton = ProbabilisticAutomaton(scale="major", chaos=0.25)
track_melody = []
track_bass = []
is_playing = False
current_melody_idx = 0
next_step_time = 0
bpm = 120
step_duration_ms = 60000 // (bpm * 4)
drum_step = 0

sounds = initialize_sounds()

update_button_positions(WIDTH, HEIGHT)
update_instrument_buttons(WIDTH, HEIGHT)          # ← важно!


# ====================== ОСНОВНОЙ ЦИКЛ ======================
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos

            # Основные кнопки
            main_btns = [
                {"rect": pygame.Rect(80, HEIGHT-140, 220, 80), "action": "create"},
                {"rect": pygame.Rect(320, HEIGHT-140, 220, 80), "action": "start"},
                {"rect": pygame.Rect(560, HEIGHT-140, 220, 80), "action": "pause"},
                {"rect": pygame.Rect(800, HEIGHT-140, 220, 80), "action": "reset"},
                {"rect": pygame.Rect(WIDTH-300, HEIGHT-140, 220, 80), "action": "exit"},
            ]
            for btn in main_btns:
                if btn["rect"].collidepoint(pos):
                    if btn["action"] == "create":
                        track_melody = automaton.generate_sequence(48)
                        track_bass = [random.choice(list(automaton.notes_dict.keys())) for _ in range(48)]
                        current_melody_idx = 0
                        drum_step = 0
                        is_playing = False
                        pygame.mixer.stop()
                    elif btn["action"] == "start" and track_melody:
                        is_playing = True
                        next_step_time = pygame.time.get_ticks()
                    elif btn["action"] == "pause":
                        is_playing = False
                        pygame.mixer.stop()
                    elif btn["action"] == "reset":
                        is_playing = False
                        pygame.mixer.stop()
                        track_melody = []
                        track_bass = []
                    elif btn["action"] == "exit":
                        running = False

            # Кнопки выбора инструмента
            for btn in instrument_buttons:
                if btn["rect"].collidepoint(pos):
                    new_inst = btn["action"]
                    SOUNDS_CONFIG["melody"]["instrument"] = new_inst
                    sounds = initialize_sounds()
                    print(f"✅ Инструмент изменён на: {new_inst}")

            # Кнопки настроек
            for btn in settings_buttons:
                if btn["rect"].collidepoint(pos):
                    if btn["action"] == "toggle_scale":
                        new_scale = "minor" if automaton.scale == "major" else "major"
                        automaton = ProbabilisticAutomaton(new_scale, automaton.chaos)
                        sounds = initialize_sounds()
                        track_melody = []
                        track_bass = []
                        is_playing = False
                        settings_buttons[0]["text"] = f"Лад: {new_scale.upper()}"
                    elif btn["action"] == "chaos_up":
                        automaton.chaos = min(1.0, automaton.chaos + 0.1)
                    elif btn["action"] == "chaos_down":
                        automaton.chaos = max(0.0, automaton.chaos - 0.1)
                    elif btn["action"] == "bpm_up":
                        bpm = min(200, bpm + 10)
                        step_duration_ms = 60000 // (bpm * 4)
                    elif btn["action"] == "bpm_down":
                        bpm = max(40, bpm - 10)
                        step_duration_ms = 60000 // (bpm * 4)

    if is_playing:
        now = pygame.time.get_ticks()
        if now >= next_step_time:
            play_step(sounds, track_melody, track_bass, current_melody_idx, drum_step)
            next_step_time = now + step_duration_ms
            drum_step += 1
            current_melody_idx += 1

    draw_ui(screen, automaton, track_melody, is_playing, current_melody_idx, bpm, WIDTH, HEIGHT)
    clock.tick(FPS)

pygame.quit()
sys.exit()