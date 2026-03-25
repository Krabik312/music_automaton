# ================================================
# music_engine.py
# ================================================

import pygame
import numpy as np
import random

MAJOR_NOTES = {"C": 261.63, "D": 293.66, "E": 329.63, "F": 349.23,
               "G": 392.00, "A": 440.00, "B": 493.88}
MINOR_NOTES = {"A": 440.00, "B": 493.88, "C": 523.25, "D": 587.33,
               "E": 659.25, "F": 698.46, "G": 783.99}

# ====================== НАСТРОЙКИ ======================
SOUNDS_CONFIG = {
    "melody": {
        "enabled": True,
        "volume": 0.88,
        "duration": 0.55,
        "instrument": "piano"          # по умолчанию
    },
    "bass":  {"enabled": False, "volume": 0.4, "duration": 0.2},
    "kick":  {"enabled": True, "volume": 0.5},
    "snare": {"enabled": True, "volume": 0.15},
    "hat":   {"enabled": True, "volume": 0.1},
}

# ====================== ВЕРОЯТНОСТНЫЙ АВТОМАТ ======================
class ProbabilisticAutomaton:
    # (тот же код, что был раньше — без изменений)
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


# ====================== УЛУЧШЕННЫЕ ЗВУКИ МЕЛОДИИ ======================
def create_melody_sound(freq, duration=0.55, instrument="piano"):
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)

    if instrument == "guitar":
        # Тот вариант гитары, который тебе раньше нравился
        delay = int(sample_rate / freq)
        noise = np.random.uniform(-1, 1, delay) * 0.95
        buf = np.zeros(delay)
        buf[:] = noise
        wave = np.zeros(len(t))
        for i in range(len(t)):
            wave[i] = buf[0]
            avg = (buf[0] + buf[1]) * 0.5
            buf = np.roll(buf, -1)
            buf[-1] = avg * 0.994
        wave += 0.12 * np.sin(2 * np.pi * 80 * t)
        env = np.exp(-3.0 * t) * 0.95

    else:  # piano
        wave = (np.sin(2 * np.pi * freq * t) * 0.62 +
                np.sin(2 * np.pi * freq * 2.01 * t) * 0.28 +
                np.sin(2 * np.pi * freq * 3 * t) * 0.10)
        env = np.exp(-4.1 * t) * 0.93

    wave = (wave * env * 32767).astype(np.int16)
    sound = pygame.sndarray.make_sound(np.column_stack((wave, wave)))
    sound.set_volume(SOUNDS_CONFIG["melody"]["volume"])
    return sound
# Остальные функции (bass, kick, snare, hat) оставляем как были раньше — они уже достаточно хороши.
# Если хочешь, я потом сделаю и для них более «живые» версии.

def create_bass_sound(freq, duration=0.6):
    # ... (тот же код, что был раньше)
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    wave = np.sin(2 * np.pi * freq * t) * 0.4 + 0.15 * np.sin(2 * np.pi * freq * 2.01 * t)
    env = np.exp(-3.2 * t)
    wave = (wave * env * 32767).astype(np.int16)
    sound = pygame.sndarray.make_sound(np.column_stack((wave, wave)))
    sound.set_volume(SOUNDS_CONFIG["bass"]["volume"])
    return sound

def create_kick():
    # ... (тот же код)
    sample_rate = 44100
    dur = 0.35
    t = np.linspace(0, dur, int(sample_rate * dur), endpoint=False)
    freq_sweep = 180 - 170 * t
    wave = np.sin(2 * np.pi * freq_sweep * t) * 0.95
    env = np.exp(-7 * t)
    wave = (wave * env * 32767).astype(np.int16)
    sound = pygame.sndarray.make_sound(np.column_stack((wave, wave)))
    sound.set_volume(SOUNDS_CONFIG["kick"]["volume"])
    return sound

def create_snare():
    # ... (тот же код)
    sample_rate = 44100
    dur = 0.25
    t = np.linspace(0, dur, int(sample_rate * dur), endpoint=False)
    noise = np.random.uniform(-1, 1, len(t)) * 0.75
    tone = np.sin(2 * np.pi * 220 * t) * 0.25
    env = np.exp(-11 * t)
    wave = (noise + tone) * env * 32767
    sound = pygame.sndarray.make_sound(np.column_stack((wave.astype(np.int16), wave.astype(np.int16))))
    sound.set_volume(SOUNDS_CONFIG["snare"]["volume"])
    return sound

def create_hat():
    # ... (тот же код)
    sample_rate = 44100
    dur = 0.08
    t = np.linspace(0, dur, int(sample_rate * dur), endpoint=False)
    noise = np.random.uniform(-1, 1, len(t)) * 0.9
    env = np.exp(-38 * t)
    wave = (noise * env * 32767).astype(np.int16)
    sound = pygame.sndarray.make_sound(np.column_stack((wave, wave)))
    sound.set_volume(SOUNDS_CONFIG["hat"]["volume"])
    return sound


def initialize_sounds():
    melody_sounds = {}
    bass_sounds = {}
    for note, freq in MAJOR_NOTES.items():
        melody_sounds[note] = create_melody_sound(
            freq,
            SOUNDS_CONFIG["melody"]["duration"],
            SOUNDS_CONFIG["melody"]["instrument"]
        )
        bass_sounds[note] = create_bass_sound(freq / 2, SOUNDS_CONFIG["bass"]["duration"])

    return {
        "melody": melody_sounds,
        "bass": bass_sounds,
        "kick": create_kick(),
        "snare": create_snare(),
        "hat": create_hat(),
    }


def play_step(sounds, track_melody, track_bass, current_idx, drum_step):
    idx = current_idx % len(track_melody) if track_melody else 0

    if SOUNDS_CONFIG["melody"]["enabled"] and track_melody:
        note = track_melody[idx]
        pygame.mixer.Channel(0).play(sounds["melody"][note])

    if SOUNDS_CONFIG["bass"]["enabled"] and track_bass:
        bass_note = track_bass[idx]
        pygame.mixer.Channel(1).play(sounds["bass"][bass_note])

    if SOUNDS_CONFIG["kick"]["enabled"] and drum_pattern[drum_step % 16]:
        pygame.mixer.Channel(2).play(sounds["kick"])
    if SOUNDS_CONFIG["snare"]["enabled"] and snare_pattern[drum_step % 16]:
        pygame.mixer.Channel(3).play(sounds["snare"])
    if SOUNDS_CONFIG["hat"]["enabled"] and hat_pattern[drum_step % 16]:
        pygame.mixer.Channel(4).play(sounds["hat"])


drum_pattern = [1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0]
snare_pattern = [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0]
hat_pattern = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]