import librosa
import numpy as np
import pretty_midi


class SmartAccompaniment:
    """
    Intelligent accompaniment generator.

    Core idea:
    - detect where singer is active
    - add instruments ONLY in gaps
    - avoid melody doubling
    - create real "arrangement", not karaoke

    Result:
    feels composed, not layered
    """

    def __init__(self, sr=22050):
        self.sr = sr

    # ------------------------------------------------
    # Detect vocal activity (energy based)
    # ------------------------------------------------
    def detect_silences(self, y, threshold_db=-35, hop=512):
        rms = librosa.feature.rms(y=y, hop_length=hop)[0]
        db = librosa.amplitude_to_db(rms, ref=np.max)

        silent = db < threshold_db

        times = librosa.frames_to_time(
            np.arange(len(silent)),
            sr=self.sr,
            hop_length=hop
        )

        segments = []
        start = None

        for i, s in enumerate(silent):
            if s and start is None:
                start = times[i]
            elif not s and start is not None:
                segments.append((start, times[i]))
                start = None

        if start is not None:
            segments.append((start, times[-1]))

        return segments

    # ------------------------------------------------
    # Add tanpura drone (always)
    # ------------------------------------------------
    def add_drone(self, pm, root, duration):
        program = pretty_midi.instrument_name_to_program("String Ensemble 1")
        inst = pretty_midi.Instrument(program=program)

        base = pretty_midi.note_name_to_number(root + "2")
        fifth = base + 7

        step = 1.2
        t = 0

        while t < duration:
            inst.notes.append(pretty_midi.Note(55, base, t, t+step))
            inst.notes.append(pretty_midi.Note(45, fifth, t, t+step))
            t += step

        pm.instruments.append(inst)

    # ------------------------------------------------
    # Mridangam only while singing
    # ------------------------------------------------
    def add_percussion(self, pm, tempo, duration):
        drum = pretty_midi.Instrument(program=0, is_drum=True)

        beat = 60 / tempo
        t = 0

        while t < duration:
            drum.notes.append(pretty_midi.Note(90, 36, t, t+0.08))
            drum.notes.append(pretty_midi.Note(65, 38, t+beat/2, t+beat/2+0.08))
            t += beat

        pm.instruments.append(drum)

    # ------------------------------------------------
    # Melody fills ONLY in silent gaps
    # ------------------------------------------------
    def add_fills(self, pm, gaps, root):
        program = pretty_midi.instrument_name_to_program("Violin")
        inst = pretty_midi.Instrument(program=program)

        base = pretty_midi.note_name_to_number(root + "4")

        for start, end in gaps:
            length = end - start

            if length < 0.4:
                continue

            step = 0.25
            t = start

            scale = [0, 2, 4, 7, 9]

            while t < end:
                pitch = base + np.random.choice(scale)
                inst.notes.append(pretty_midi.Note(70, pitch, t, t+step))
                t += step

        pm.instruments.append(inst)

    # ------------------------------------------------
    # MAIN
    # ------------------------------------------------
    def generate(self, vocal_wav, melody_midi, tempo, key, out_midi):

        print("🎤 analyzing vocal for gaps...")

        y, _ = librosa.load(vocal_wav, sr=self.sr)

        gaps = self.detect_silences(y)

        print(f"Detected {len(gaps)} musical gaps")

        base_midi = pretty_midi.PrettyMIDI(melody_midi)
        duration = base_midi.get_end_time()

        pm = pretty_midi.PrettyMIDI(initial_tempo=tempo)

        # copy melody
        for inst in base_midi.instruments:
            pm.instruments.append(inst)

        root = key[0]

        self.add_drone(pm, root, duration)
        self.add_percussion(pm, tempo, duration)
        self.add_fills(pm, gaps, root)

        pm.write(out_midi)

        print("✅ Smart accompaniment written:", out_midi)

