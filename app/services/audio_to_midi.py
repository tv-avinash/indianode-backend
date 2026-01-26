import librosa
import numpy as np
import pretty_midi


def audio_to_midi(
    wav_path: str,
    midi_path: str,
    sr: int = 22050,
    fmin: float = librosa.note_to_hz("C2"),
    fmax: float = librosa.note_to_hz("C7"),
):
    """
    Convert monophonic audio to MIDI melody
    """

    # 1. Load audio
    y, sr = librosa.load(wav_path, sr=sr)

    # 2. Pitch extraction (robust for melodies)
    f0, voiced_flag, voiced_prob = librosa.pyin(
        y,
        fmin=fmin,
        fmax=fmax,
        sr=sr,
        frame_length=2048,
        hop_length=256
    )

    # 3. Convert Hz → MIDI notes
    midi_notes = librosa.hz_to_midi(f0)
    midi_notes = np.round(midi_notes)

    # 4. Create MIDI
    midi = pretty_midi.PrettyMIDI()
    instrument = pretty_midi.Instrument(program=pretty_midi.instrument_name_to_program("Flute"))

    time_per_frame = 256 / sr
    current_note = None
    note_start = 0.0

    for i, note in enumerate(midi_notes):
        time = i * time_per_frame

        if np.isnan(note):
            if current_note is not None:
                instrument.notes.append(
                    pretty_midi.Note(
                        velocity=80,
                        pitch=int(current_note),
                        start=note_start,
                        end=time
                    )
                )
                current_note = None
            continue

        if current_note is None:
            current_note = note
            note_start = time
        elif note != current_note:
            instrument.notes.append(
                pretty_midi.Note(
                    velocity=80,
                    pitch=int(current_note),
                    start=note_start,
                    end=time
                )
            )
            current_note = note
            note_start = time

    # Flush last note
    if current_note is not None:
        instrument.notes.append(
            pretty_midi.Note(
                velocity=80,
                pitch=int(current_note),
                start=note_start,
                end=len(midi_notes) * time_per_frame
            )
        )

    midi.instruments.append(instrument)
    midi.write(midi_path)

    return midi_path

