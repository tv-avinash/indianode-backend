# app/services/karaoke_ai/accompaniment_generator.py

import pretty_midi
import numpy as np
from collections import Counter


class AccompanimentGenerator:
    """
    AI Arranger (NOT karaoke generator)

    Strategy:
    ----------
    1. Read melody midi
    2. Detect key
    3. Detect chords per bar
    4. Generate:
        - bass (root notes)
        - pad (chords)
        - drums (rhythm)
    5. NEVER double melody

    Result:
    ----------
    Real band feel instead of harmonium shadow
    """

    # -------------------------------------------------------
    # Key detection
    # -------------------------------------------------------

    def detect_key(self, melody_notes):
        pitch_classes = [n.pitch % 12 for n in melody_notes]
        most = Counter(pitch_classes).most_common(1)[0][0]
        return most

    # -------------------------------------------------------
    # Chord detection per bar
    # -------------------------------------------------------

    def detect_chords(self, melody_notes, tempo, duration):

        beat = 60 / tempo
        bar = beat * 4

        bars = int(np.ceil(duration / bar))

        chords = []

        for b in range(bars):
            start = b * bar
            end = start + bar

            notes = [
                n.pitch % 12
                for n in melody_notes
                if start <= n.start < end
            ]

            if not notes:
                chords.append(None)
                continue

            root = Counter(notes).most_common(1)[0][0]
            chords.append(root)

        return chords, bar

    # -------------------------------------------------------
    # Bassline (root notes only)
    # -------------------------------------------------------

    def add_bass(self, pm, chords, bar_len):

        program = pretty_midi.instrument_name_to_program("Electric Bass (finger)")
        inst = pretty_midi.Instrument(program=program)

        for i, root in enumerate(chords):
            if root is None:
                continue

            pitch = 36 + root  # bass octave

            start = i * bar_len
            end = start + bar_len

            inst.notes.append(
                pretty_midi.Note(velocity=85, pitch=pitch, start=start, end=end)
            )

        pm.instruments.append(inst)

    # -------------------------------------------------------
    # Pad chords (soft harmony)
    # -------------------------------------------------------

    def add_pad(self, pm, chords, bar_len):

        program = pretty_midi.instrument_name_to_program("Synth Strings 1")
        inst = pretty_midi.Instrument(program=program)

        for i, root in enumerate(chords):
            if root is None:
                continue

            base = 60 + root
            third = base + 4
            fifth = base + 7

            start = i * bar_len
            end = start + bar_len

            for p in [base, third, fifth]:
                inst.notes.append(
                    pretty_midi.Note(velocity=45, pitch=p, start=start, end=end)
                )

        pm.instruments.append(inst)

    # -------------------------------------------------------
    # Drum rhythm (independent, not melody-following)
    # -------------------------------------------------------

    def add_drums(self, pm, tempo, duration):

        drum = pretty_midi.Instrument(program=0, is_drum=True)

        beat = 60 / tempo
        t = 0

        while t < duration:

            # kick
            drum.notes.append(
                pretty_midi.Note(velocity=100, pitch=36, start=t, end=t+0.1)
            )

            # snare
            drum.notes.append(
                pretty_midi.Note(velocity=70, pitch=38, start=t+beat/2, end=t+beat/2+0.1)
            )

            t += beat

        pm.instruments.append(drum)

    # -------------------------------------------------------
    # MAIN GENERATE
    # -------------------------------------------------------

    def generate(self, melody_midi, style, tempo, out_path):

        base = pretty_midi.PrettyMIDI(melody_midi)
        melody_notes = base.instruments[0].notes
        duration = base.get_end_time()

        pm = pretty_midi.PrettyMIDI(initial_tempo=tempo)

        # ---------------------------------------------------
        # detect chords
        # ---------------------------------------------------

        chords, bar_len = self.detect_chords(melody_notes, tempo, duration)

        # ---------------------------------------------------
        # add accompaniment (NO melody doubling)
        # ---------------------------------------------------

        self.add_bass(pm, chords, bar_len)
        self.add_pad(pm, chords, bar_len)
        self.add_drums(pm, tempo, duration)

        pm.write(out_path)

