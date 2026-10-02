"""Synthesize a simple original soundtrack + UI sounds for bizflow-promo (15 s, 120 BPM)."""
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR, DUR = 44100, 15.0
N = int(SR * DUR); t = np.arange(N) / SR
mix = np.zeros(N); rng = np.random.default_rng(7)

def add(sig, at, gain=1.0):
    i = int(at * SR); j = min(N, i + len(sig)); mix[i:j] += sig[: j - i] * gain

def env(n, a=0.005, d=0.2):
    x = np.arange(n) / SR
    return np.minimum(1, x / a) * np.exp(-np.maximum(0, x - a) / d)

def tone(f, dur, a=0.005, d=0.2):
    n = int(dur * SR); x = np.arange(n) / SR
    return np.sin(2 * np.pi * f * x) * env(n, a, d)

def kick():
    n = int(0.28 * SR); x = np.arange(n) / SR
    f = 45 + 75 * np.exp(-x / 0.035)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x / 0.09)

def noise(dur, lo, hi):
    n = int(dur * SR); sos = butter(2, [lo, hi], btype="band", fs=SR, output="sos")
    return sosfilt(sos, rng.standard_normal(n))

def whoosh(dur=0.45):
    n = int(dur * SR); x = np.linspace(0, 1, n)
    return noise(dur, 500, 6000) * np.sin(np.pi * x) ** 2

def pop(f0=420, f1=900, dur=0.09):
    n = int(dur * SR); x = np.arange(n) / SR
    f = np.linspace(f0, f1, n)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x / 0.03)

def bell(f, dur=1.4):
    n = int(dur * SR); x = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * x) + 0.35 * np.sin(2 * np.pi * 2.01 * f * x) * np.exp(-x / 0.25)) * np.exp(-x / 0.45)

# pad: gentle chords, one per 2 bars (4 s) -> C, Am, F, G(short) , C
def pad(freqs, dur):
    n = int(dur * SR); x = np.arange(n) / SR
    s = sum(np.sin(2 * np.pi * f * x) + 0.5 * np.sin(2 * np.pi * f * 1.003 * x) for f in freqs)
    e = np.minimum(1, x / 0.6) * np.minimum(1, (dur - x) / 0.6)
    return s * e / len(freqs)
C, Am, F, G = [130.81, 196.0, 261.63, 329.63], [110.0, 164.81, 220.0, 261.63], [87.31, 174.61, 220.0, 261.63], [98.0, 146.83, 196.0, 246.94]
for ch, at, d in [(C, 0, 4.2), (Am, 4, 4.2), (F, 8, 2.9), (G, 10.5, 2.6), (C, 12.9, 2.1)]:
    add(pad(ch, d), at, 0.11)

# bass pulse + drums from the first morph (2.5 s) to the end card
roots = lambda b: 65.41 if b < 4 else 55.0 if b < 8 else 43.65 if b < 10.5 else 49.0 if b < 12.9 else 65.41
for k in range(5, 26):
    bt = k * 0.5
    add(kick(), bt, 0.55)
    add(tone(roots(bt), 0.22, 0.004, 0.09), bt + 0.25, 0.22)
    add(noise(0.05, 6000, 12000) * env(int(0.05 * SR), 0.001, 0.015), bt + 0.25, 0.10)
for bt in np.arange(8.5, 12.75, 1.0):               # clap-ish on the build
    add(noise(0.12, 1200, 5000) * env(int(0.12 * SR), 0.001, 0.035), bt, 0.16)

# UI sounds aligned to the animation
for at in [0.75, 1.0, 1.25, 1.5]: add(noise(0.14, 2500, 7000) * env(int(0.14 * SR), 0.02, 0.05), at, 0.10)   # pen scratches
for at in [2.0, 5.5]: add(tone(1250, 0.05, 0.001, 0.012), at, 0.35); add(tone(180, 0.09, 0.001, 0.03), at, 0.3)  # taps
for at in [2.0, 2.5, 5.7, 7.75, 10.5, 12.9]: add(whoosh(), at - 0.08, 0.20)
for i, at in enumerate([3.5, 3.75, 4.0]): add(pop(380 + i * 60, 760 + i * 80), at, 0.22)
for at in np.arange(4.25, 4.95, 0.07): add(tone(1800, 0.02, 0.001, 0.006), at, 0.08)          # count-up ticks
for at in [6.5, 7.0]: add(pop(520, 1040, 0.11), at, 0.32)
for i in range(5): add(pop(300 + i * 70, 420 + i * 90, 0.07), 8.3 + i * 0.125, 0.2)       # bars
for at in [9.4, 9.6, 10.05]: add(pop(600, 900, 0.06), at, 0.16)
for i, at in enumerate([10.75, 11.25, 11.75, 12.25]):                                       # word slams
    add(kick(), at, 0.5); add(noise(0.1, 300, 2500) * env(int(0.1 * SR), 0.001, 0.03), at, 0.22)
for i, f in enumerate([523.25, 659.25, 783.99, 1046.5]): add(bell(f), 13.2 + i * 0.11, 0.16)  # logo chime
add(pop(700, 1200, 0.09), 13.85, 0.22)

fade = np.minimum(1, (DUR - t) / 0.5); mix *= fade
mix = np.tanh(mix * 1.1); mix *= 0.7 / np.max(np.abs(mix))
wavfile.write("bizflow-promo.wav", SR, (np.stack([mix, mix], 1) * 32767).astype(np.int16))
print("peak", np.max(np.abs(mix)), "rms", np.sqrt(np.mean(mix ** 2)))
