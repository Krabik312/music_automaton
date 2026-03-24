# ================================================
# main.py
# ГЛАВНЫЙ ФАЙЛ
# ================================================

import pygame
import sys
import ctypes
import random
from music_engine import (ProbabilisticAutomaton,
                           create_melody_sound,
                           create_bass_sound,
                           create_kick,
                           create_snare,
                           create_hat,
                           MAJOR_NOTES,
                           MINOR_NOTES)
from ui import (draw_ui,
                update_button_positions,
                settings_buttons,
                init_fonts)

ctypes.windll.user32.SetProcessDPIAware()

pygame.init()
pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=4096)
pygame.mixer.init()

# ←←← ВАЖНО: инициализируем шрифты ТОЛЬКО здесь
init_fonts()

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("Вероятностные автоматы: генератор музыки")

clock = pygame.time.Clock()
FPS = 60

# ====================== ИНИЦИАЛИЗАЦИЯ ======================
automaton = ProbabilisticAutomaton(scale="major", chaos=0.25)
track_melody = []
track_bass = []
is_playing = False
current_melody_idx = 0
next_step_time = 0
bpm = 120
step_duration_ms = 60000 // (bpm * 4)
drum_step = 0

melody_ch = pygame.mixer.Channel(0)
bass_ch    = pygame.mixer.Channel(1)
kick_ch    = pygame.mixer.Channel(2)
snare_ch   = pygame.mixer.Channel(3)
hat_ch     = pygame.mixer.Channel(4)

# Создаём звуки
melody_sounds = {note: create_melody_sound(freq) for note, freq in MAJOR_NOTES.items()}
bass_sounds   = {note: create_bass_sound(freq / 2) for note, freq in MAJOR_NOTES.items()}
kick_sound = create_kick()
snare_sound = create_snare()
hat_sound = create_hat()

drum_pattern = [1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0]
snare_pattern = [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0]
hat_pattern = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

update_button_positions(WIDTH, HEIGHT)


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
                        melody_ch.stop()
                        bass_ch.stop()
                    elif btn["action"] == "start" and track_melody:
                        is_playing = True
                        next_step_time = pygame.time.get_ticks()
                    elif btn["action"] == "pause":
                        is_playing = False
                        melody_ch.stop()
                        bass_ch.stop()
                    elif btn["action"] == "reset":
                        is_playing = False
                        melody_ch.stop()
                        bass_ch.stop()
                        track_melody = []
                        track_bass = []
                    elif btn["action"] == "exit":
                        running = False

            # Кнопки настроек
            for btn in settings_buttons:
                if btn["rect"].collidepoint(pos):
                    if btn["action"] == "toggle_scale":
                        new_scale = "minor" if automaton.scale == "major" else "major"
                        automaton = ProbabilisticAutomaton(new_scale, automaton.chaos)
                        notes_dict = MAJOR_NOTES if new_scale == "major" else MINOR_NOTES
                        melody_sounds.clear()
                        bass_sounds.clear()
                        for note, freq in notes_dict.items():
                            melody_sounds[note] = create_melody_sound(freq)
                            bass_sounds[note] = create_bass_sound(freq / 2)
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
            if drum_pattern[drum_step % 16]:
                kick_ch.play(kick_sound)
            if snare_pattern[drum_step % 16]:
                snare_ch.play(snare_sound)
            if hat_pattern[drum_step % 16]:
                hat_ch.play(hat_sound)

            if track_melody:
                note = track_melody[current_melody_idx % len(track_melody)]
                melody_ch.play(melody_sounds[note])
            if track_bass:
                bass_note = track_bass[current_melody_idx % len(track_bass)]
                bass_ch.play(bass_sounds[bass_note])

            next_step_time = now + step_duration_ms
            drum_step += 1
            current_melody_idx += 1

    draw_ui(screen, automaton, track_melody, is_playing, current_melody_idx, bpm, WIDTH, HEIGHT)
    clock.tick(FPS)

pygame.quit()
sys.exit()