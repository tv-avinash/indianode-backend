import subprocess
import os
from pathlib import Path


REAPER_PATH = "/home/supersu/indianode-backend/tools/reaper/REAPER/reaper"
TEMPLATE_PATH = "app/services/mastering/indianode_master_template.rpp"


def master_audio(input_wav: str, output_wav: str):
    """
    Runs Reaper headless to master audio using Ozone template
    """

    input_wav = Path(input_wav).resolve()
    output_wav = Path(output_wav).resolve()

    # Reaper batch render config file
    batch_file = output_wav.with_suffix(".txt")

    batch_file.write_text(f"""
{input_wav}\t{output_wav}
<CONFIG
SRATE 44100
NCH 2
DITHER 3
>
""")

    cmd = [
        REAPER_PATH,
        "-batchconvert",
        str(batch_file)
    ]

    subprocess.run(cmd, check=True)

    batch_file.unlink(missing_ok=True)

    return str(output_wav)

