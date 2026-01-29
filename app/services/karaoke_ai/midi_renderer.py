# app/services/karaoke_ai/midi_renderer.py

import subprocess


class MidiRenderer:
    """
    Render MIDI → WAV using FluidSynth
    """

    def __init__(self, soundfont="/usr/share/sounds/sf2/FluidR3_GM.sf2"):
        self.soundfont = soundfont

    def render(self, midi_path, wav_path):
        cmd = [
            "fluidsynth",
            "-ni",
            self.soundfont,
            midi_path,
            "-F", wav_path,
            "-r", "44100"
        ]

        subprocess.run(cmd, check=True)

