# ================================================
# music_engine.py
# ОТВЕЧАЕТ ЗА ВСЮ МУЗЫКУ И ТЕОРИЮ ВЕРОЯТНОСТНЫХ АВТОМАТОВ
# Здесь класс Марковской цепи + генерация всех звуков (мелодия, бас, барабаны)
# ================================================

import pygame
import numpy as np
import random

# Ноты для мажора и минора
MAJOR_NOTES = {"C": 261.63, "D": 293.66, "E": 329.63, "F": 349.23,
               "G": 392.00, "A": 440.00, "B": 493.88}
MINOR_NOTES = {"A": 440.00, "B": 493.88, "C": 523.25, "D": 587.33,
               "E": 659.25, "F": 698.46, "G": 783.99}


class ProbabilisticAutomaton:
    """Класс вероятностного автомата (Марковская цепь) — основная тема предмета"""
    def __init__(self, scale="major", chaos=0.3):
        self.scale = scale
        self.chaos = chaos
        self.notes_dict = MAJOR_NOTES if scale == "major" else MINOR_NOTES
        self.states = list(self.notes_dict.keys())
        self.current_state = random.choice(self.states)
        self.musical_transitions = self._create_musical_matrix()

    def _create_musical_matrix(self):
        """Создаёт музыкально-осмысленные вероятности переходов"""
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
        """Смешивает музыкальные переходы с хаосом (равномерное распределение)"""
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
        """Генерирует последовательность нот с помощью автомата"""
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


# ====================== ГЕНЕРАЦИЯ ЗВУКОВ ======================
def create_melody_sound(freq):
    """Жирный синтезаторный звук (saw + square)"""
    sample_rate = 44100
    dur = 0.52
    t = np.linspace(0, dur, int(sample_rate * dur), endpoint=False)
    saw = 2 * (t * freq - np.floor(t * freq + 0.5))
    square = np.sign(np.sin(2 * np.pi * freq * t))
    wave = (saw * 0.6 + square * 0.4) * 0.28
    env = np.exp(-2.8 * t) * 0.9 + 0.1 * np.exp(-12 * t)
    wave = (wave * env * 32767).astype(np.int16)
    return pygame.sndarray.make_sound(np.column_stack((wave, wave)))


def create_bass_sound(freq):
    """Низкий басовый слой"""
    sample_rate = 44100
    dur = 0.55
    t = np.linspace(0, dur, int(sample_rate * dur), endpoint=False)
    wave = np.sin(2 * np.pi * freq * t) * 0.35 + 0.2 * np.sin(2 * np.pi * freq * 2 * t)
    env = np.exp(-3.5 * t)
    wave = (wave * env * 32767).astype(np.int16)
    return pygame.sndarray.make_sound(np.column_stack((wave, wave)))


def create_kick():
    """Кик (ударный бас)"""
    sample_rate = 44100
    dur = 0.35
    t = np.linspace(0, dur, int(sample_rate * dur), endpoint=False)
    freq_sweep = 180 - 160 * t
    wave = np.sin(2 * np.pi * freq_sweep * t) * 0.9
    env = np.exp(-8 * t)
    wave = (wave * env * 32767).astype(np.int16)
    return pygame.sndarray.make_sound(np.column_stack((wave, wave)))


def create_snare():
    """Снейр (хлопок)"""
    sample_rate = 44100
    dur = 0.25
    t = np.linspace(0, dur, int(sample_rate * dur), endpoint=False)
    noise = np.random.uniform(-1, 1, len(t)) * 0.7
    tone = np.sin(2 * np.pi * 220 * t) * 0.3
    env = np.exp(-12 * t)
    wave = (noise + tone) * env * 32767
    return pygame.sndarray.make_sound(np.column_stack((wave.astype(np.int16), wave.astype(np.int16))))


def create_hat():
    """Хай-хэт (закрытый)"""
    sample_rate = 44100
    dur = 0.08
    t = np.linspace(0, dur, int(sample_rate * dur), endpoint=False)
    noise = np.random.uniform(-1, 1, len(t)) * 0.85
    env = np.exp(-35 * t)
    wave = (noise * env * 32767).astype(np.int16)
    return pygame.sndarray.make_sound(np.column_stack((wave, wave)))