# app/music_reasoner/instrument_merger.py

def merge_instruments(
    reasoned_instruments: list[str],
    user_instruments: list[str] | None
) -> list[str]:
    """
    Merge reasoner instruments with user-selected instruments.
    User instruments always win and are never removed.
    """
    if not user_instruments:
        return reasoned_instruments

    merged = []

    for inst in reasoned_instruments:
        if inst not in merged:
            merged.append(inst)

    for inst in user_instruments:
        if inst not in merged:
            merged.append(inst)

    return merged

