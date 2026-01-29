# app/services/karaoke_ai/vocal_analyzer.py

import librosa
import numpy as np
import pretty_midi
import crepe


class VocalAnalyzer:
    """
    Extract musical structure from raw singing:
    - tempo
    - key
    - melody MIDI
    """

    def __init__(self, sr=16000):
        self.sr = sr

    # ---------------------------
    # Load audio
    # ---------------------------
    def load(self, path):
        y, sr = librosa.load(path, sr=self.sr, mono=True)
        return y, sr

    # ---------------------------
    # Tempo detection
    # ---------------------------
    def detect_tempo(self, y, sr):
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        return float(tempo)

    # ---------------------------
    # Key detection (simple chroma)
    # ---------------------------
    def detect_key(self, y, sr):
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        avg = chroma.mean(axis=1)
        note = np.argmax(avg)

        notes = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
        return notes[note]

    # ---------------------------
    # Pitch → MIDI
    # ---------------------------
    def extract_melody_midi(self, y, sr, out_midi_path):
        time, freq, conf, _ = crepe.predict(
            y,
            sr,
            viterbi=True
        )

        pm = pretty_midi.PrettyMIDI()
        inst = pretty_midi.Instrument(program=0)

        step = 0.05  # 50ms resolution

        for t, f, c in zip(time, freq, conf):
            if f <= 0 or c < 0.6:
                continue

            pitch = pretty_midi.hz_to_note_number(f)
            start = float(t)
            end = float(t + step)

            inst.notes.append(
                pretty_midi.Note(
                    velocity=90,
                    pitch=int(pitch),
                    start=start,
                    end=end
                )
            )

        pm.instruments.append(inst)
        pm.write(out_midi_path)

    # ---------------------------
    # Main entry
    # ---------------------------
    def analyze(self, wav_path, midi_path):
        y, sr = self.load(wav_path)

        tempo = self.detect_tempo(y, sr)
        key = self.detect_key(y, sr)

        self.extract_melody_midi(y, sr, midi_path)

        return {
            "tempo": tempo,
            "key": key,
            "midi_path": midi_path
        }

