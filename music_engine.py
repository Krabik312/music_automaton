# ================================================
# music_engine.py
# ВСЯ ЗВУКОВАЯ ЧАСТЬ — полностью настраиваемая
# Меняй только этот файл, остальная программа не трогается
# ================================================

import pygame
import numpy as np
import random

MAJOR_NOTES = {"C": 261.63, "D": 293.66, "E": 329.63, "F": 349.23,
               "G": 392.00, "A": 440.00, "B": 493.88}
MINOR_NOTES = {"A": 440.00, "B": 493.88, "C": 523.25, "D": 587.33,
               "E": 659.25, "F": 698.46, "G": 783.99}


# ====================== КОНФИГУРАЦИЯ ЗВУКА ======================
# ←←← ВСЁ, ЧТО ТЫ МОЖЕШЬ МЕНЯТЬ, НАХОДИТСЯ ЗДЕСЬ ←←←
SOUNDS_CONFIG = {
    "melody": {
        "enabled": True,
        "volume": 0.85,      # 0.0 - 1.0
        "duration": 0.52,
    },
    "bass": {
        "enabled": True,
        "volume": 0.70,
        "duration": 0.55,
    },
    "kick": {
        "enabled": True,
        "volume": 0.90,
    },
    "snare": {
        "enabled": True,
        "volume": 0.75,
    },
    "hat": {
        "enabled": True,
        "volume": 0.60,
    },
    # Добавь сюда новые слои, например:
    # "pad": {"enabled": False, "volume": 0.4},
}

# ====================== КЛАСС АВТОМАТА ======================
class ProbabilisticAutomaton:
    def __init__(self, scale="major", chaos=0.3):
        self.scale = scale
        self.chaos = chaos
        self.notes_dict = MAJOR_NOTES if scale == "major" else MINOR_NOTES
        self.states = list(self.notes_dict.keys())
        self.current_state = random.choice(self.states)
        self.musical_transitions = self._create_musical_matrix()

    def _create_musical_matrix(self):
        matrix = {}
        n = len(self.states)
        for state in self.states:
            matrix[state] = {}
            i = self.states.index(state)
            for next_state in self.states:
                j = self.states.index(next_state)
                dist = min(abs(i - j), n - abs(i - j))
                prob = 0.42 if dist == 0 else max(0.06, 0.32 - dist * 0.065)
                matrix[state][next_state] = prob
        return matrix

    def get_transition_probs(self):
        trans = {}
        n = len(self.states)
        uniform = 1.0 / n
        for state in self.states:
            trans[state] = {}
            total = 0.0
            for ns in self.states:
                p = (1 - self.chaos) * self.musical_transitions[state][ns] + self.chaos * uniform
                trans[state][ns] = p
                total += p
            for ns in self.states:
                trans[state][ns] /= total
        return trans

    def generate_sequence(self, length=48):
        seq = []
        trans = self.get_transition_probs()
        current = self.current_state
        for _ in range(length):
            seq.append(current)
            probs = list(trans[current].values())
            next_states = list(trans[current].keys())
            current = random.choices(next_states, weights=probs)[0]
        self.current_state = current
        return seq


# ====================== СОЗДАНИЕ ЗВУКОВ ======================
def create_melody_sound(freq, duration=0.52):
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    saw = 2 * (t * freq - np.floor(t * freq + 0.5))
    square = np.sign(np.sin(2 * np.pi * freq * t))
    wave = (saw * 0.6 + square * 0.4) * 0.28
    env = np.exp(-2.8 * t) * 0.9 + 0.1 * np.exp(-12 * t)
    wave = (wave * env * 32767).astype(np.int16)
    sound = pygame.sndarray.make_sound(np.column_stack((wave, wave)))
    sound.set_volume(SOUNDS_CONFIG["melody"]["volume"])
    return sound


def create_bass_sound(freq, duration=0.55):
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    wave = np.sin(2 * np.pi * freq * t) * 0.35 + 0.2 * np.sin(2 * np.pi * freq * 2 * t)
    env = np.exp(-3.5 * t)
    wave = (wave * env * 32767).astype(np.int16)
    sound = pygame.sndarray.make_sound(np.column_stack((wave, wave)))
    sound.set_volume(SOUNDS_CONFIG["bass"]["volume"])
    return sound


def create_kick():
    sample_rate = 44100
    dur = 0.35
    t = np.linspace(0, dur, int(sample_rate * dur), endpoint=False)
    freq_sweep = 180 - 160 * t
    wave = np.sin(2 * np.pi * freq_sweep * t) * 0.9
    env = np.exp(-8 * t)
    wave = (wave * env * 32767).astype(np.int16)
    sound = pygame.sndarray.make_sound(np.column_stack((wave, wave)))
    sound.set_volume(SOUNDS_CONFIG["kick"]["volume"])
    return sound


def create_snare():
    sample_rate = 44100
    dur = 0.25
    t = np.linspace(0, dur, int(sample_rate * dur), endpoint=False)
    noise = np.random.uniform(-1, 1, len(t)) * 0.7
    tone = np.sin(2 * np.pi * 220 * t) * 0.3
    env = np.exp(-12 * t)
    wave = (noise + tone) * env * 32767
    sound = pygame.sndarray.make_sound(np.column_stack((wave.astype(np.int16), wave.astype(np.int16))))
    sound.set_volume(SOUNDS_CONFIG["snare"]["volume"])
    return sound


def create_hat():
    sample_rate = 44100
    dur = 0.08
    t = np.linspace(0, dur, int(sample_rate * dur), endpoint=False)
    noise = np.random.uniform(-1, 1, len(t)) * 0.85
    env = np.exp(-35 * t)
    wave = (noise * env * 32767).astype(np.int16)
    sound = pygame.sndarray.make_sound(np.column_stack((wave, wave)))
    sound.set_volume(SOUNDS_CONFIG["hat"]["volume"])
    return sound


# ====================== ИНИЦИАЛИЗАЦИЯ ВСЕХ ЗВУКОВ ======================
def initialize_sounds():
    """Вызывается один раз из main.py"""
    melody_sounds = {}
    bass_sounds = {}
    for note, freq in MAJOR_NOTES.items():
        melody_sounds[note] = create_melody_sound(freq, SOUNDS_CONFIG["melody"]["duration"])
        bass_sounds[note] = create_bass_sound(freq / 2, SOUNDS_CONFIG["bass"]["duration"])

    return {
        "melody": melody_sounds,
        "bass": bass_sounds,
        "kick": create_kick(),
        "snare": create_snare(),
        "hat": create_hat(),
    }


# ====================== ВОСПРОИЗВЕДЕНИЕ ОДНОГО ШАГА ======================
def play_step(sounds, track_melody, track_bass, current_idx, drum_step):
    """Вся логика воспроизведения в одном месте"""
    idx = current_idx % len(track_melody) if track_melody else 0

    # Мелодия
    if SOUNDS_CONFIG["melody"]["enabled"] and track_melody:
        note = track_melody[idx]
        melody_ch = pygame.mixer.Channel(0)
        melody_ch.play(sounds["melody"][note])

    # Бас
    if SOUNDS_CONFIG["bass"]["enabled"] and track_bass:
        bass_note = track_bass[idx]
        bass_ch = pygame.mixer.Channel(1)
        bass_ch.play(sounds["bass"][bass_note])

    # Барабаны
    if SOUNDS_CONFIG["kick"]["enabled"] and drum_pattern[drum_step % 16]:
        kick_ch = pygame.mixer.Channel(2)
        kick_ch.play(sounds["kick"])

    if SOUNDS_CONFIG["snare"]["enabled"] and snare_pattern[drum_step % 16]:
        snare_ch = pygame.mixer.Channel(3)
        snare_ch.play(sounds["snare"])

    if SOUNDS_CONFIG["hat"]["enabled"] and hat_pattern[drum_step % 16]:
        hat_ch = pygame.mixer.Channel(4)
        hat_ch.play(sounds["hat"])


# Паттерны барабанов (можно тоже вынести в CONFIG позже)
drum_pattern = [1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0]
snare_pattern = [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0]
hat_pattern = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]