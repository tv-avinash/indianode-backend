import librosa
import numpy as np
import pretty_midi
import subprocess
import soundfile as sf
import crepe

INPUT = "vocal.wav"
SF2 = "FluidR3_GM.sf2"

# -------------------------------------------------
# Step 1 — load audio
# -------------------------------------------------
y, sr = librosa.load(INPUT, sr=16000)

print("Detecting tempo...")
tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
tempo = float(np.mean(tempo))

print("Tempo:", tempo)

# -------------------------------------------------
# Step 2 — pitch detection (melody)
# -------------------------------------------------
print("Extracting melody with CREPE...")

time, freq, conf, _ = crepe.predict(
    y,
    sr,
    step_size=20,
    viterbi=True
)

# convert freq → midi
midi_notes = librosa.hz_to_midi(freq)
midi_notes[conf < 0.6] = 0

# -------------------------------------------------
# Step 3 — create MIDI
# -------------------------------------------------
pm = pretty_midi.PrettyMIDI(initial_tempo=tempo)

melody_inst = pretty_midi.Instrument(program=pretty_midi.instrument_name_to_program("Flute"))
bass_inst = pretty_midi.Instrument(program=pretty_midi.instrument_name_to_program("Acoustic Bass"))
pad_inst = pretty_midi.Instrument(program=pretty_midi.instrument_name_to_program("String Ensemble 1"))

step = 0.02  # 20ms

last_pitch = None
start = 0

for i, pitch in enumerate(midi_notes):
    t = i * step

    if pitch > 0:
        if last_pitch is None:
            start = t
            last_pitch = pitch
    else:
        if last_pitch is not None:
            note = pretty_midi.Note(velocity=90, pitch=int(last_pitch), start=start, end=t)
            melody_inst.notes.append(note)
            last_pitch = None

# -------------------------------------------------
# Step 4 — simple accompaniment logic
# -------------------------------------------------

duration = len(y) / sr
beat_len = 60 / tempo

print("Generating accompaniment...")

t = 0
while t < duration:
    # bass root note
    bass_note = pretty_midi.Note(
        velocity=70,
        pitch=48,  # C2 root bass
        start=t,
        end=t + beat_len
    )
    bass_inst.notes.append(bass_note)

    # pad chord
    for p in [60, 64, 67]:  # C major chord
        pad_inst.notes.append(
            pretty_midi.Note(50, p, t, t + beat_len*2)
        )

    t += beat_len

pm.instruments.extend([melody_inst, bass_inst, pad_inst])

pm.write("accompaniment.mid")

# -------------------------------------------------
# Step 5 — render with fluidsynth
# -------------------------------------------------
print("Rendering audio...")
subprocess.run(
    f"fluidsynth -ni {SF2} accompaniment.mid -F bgm.wav -r 32000",
    shell=True
)

# -------------------------------------------------
# Step 6 — mix
# -------------------------------------------------
print("Mixing...")

subprocess.run(
    'ffmpeg -y -i vocal.wav -i bgm.wav '
    '-filter_complex "amix=inputs=2:weights=1 1.3,loudnorm" final_mix.wav',
    shell=True
)

print("Done → final_mix.wav")

