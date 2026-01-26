# indianode-midi/render_worker.py

import sys
import subprocess


def render(sfz, midi, wav):
    cmd = [
        "/usr/local/bin/sfizz_render",
        "--sfz", sfz,
        "--midi", midi,
        "--wav", wav,
        "--samplerate", "44100",
        "--quality", "4",   # highest quality resampling
        "--polyphony", "64"
    ]

    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    sfz = sys.argv[1]
    midi = sys.argv[2]
    wav = sys.argv[3]

    render(sfz, midi, wav)

