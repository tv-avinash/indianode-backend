# app/services/presets.py

PRESETS = {
    # =====================================================
    # EXISTING INTERNAL PRESETS (KEEP AS-IS)
    # =====================================================

    "devotional_flute_tabla": {
        "base_prompt": (
            "Indian classical devotional instrumental music, "
            "slow tempo, peaceful spiritual mood, "
            "bansuri flute lead melody, "
            "soft tabla accompaniment, "
            "tanpura drone in background, "
            "meditative atmosphere, "
            "no vocals, studio quality recording"
        ),
        "temperature": 0.9
    },

    "carnatic_classical": {
        "base_prompt": (
            "South Indian Carnatic classical instrumental music, "
            "traditional ornamentation and phrasing, "
            "violin lead melody, "
            "mridangam or soft tabla rhythm, "
            "medium slow tempo, "
            "concert hall ambience, "
            "no vocals"
        ),
        "temperature": 0.95
    },

    "romantic_fusion": {
        "base_prompt": (
            "Indian classical and western fusion instrumental music, "
            "violin and sitar melodic lead, "
            "piano harmonic support, "
            "soft cinematic percussion, "
            "romantic emotional mood, "
            "slow tempo, "
            "film score style, "
            "no vocals"
        ),
        "temperature": 1.05
    },

    "cinematic_epic": {
        "base_prompt": (
            "Indian and western cinematic orchestral fusion instrumental, "
            "grand emotional build up, "
            "strings and layered percussion, "
            "epic inspirational mood, "
            "medium tempo, "
            "movie trailer background score, "
            "no vocals"
        ),
        "temperature": 1.1
    },

    # =====================================================
    # UI PRESETS (MATCH FRONTEND EXACTLY)
    # =====================================================

    "Carnatic Ensemble": {
        "base_prompt": (
            "South Indian Carnatic classical instrumental music, "
            "veena lead melody, "
            "mridangam rhythmic accompaniment, "
            "tanpura drone, "
            "bansuri flute phrases, "
            "raga-based improvisation, "
            "traditional concert performance, "
            "no vocals"
        ),
        "temperature": 0.95
    },

    "Devotional Bhajan": {
        "base_prompt": (
            "Indian devotional instrumental bhajan style music, "
            "harmonium and bansuri flute melody, "
            "soft tabla rhythm, "
            "tanpura drone, "
            "peaceful spiritual ambience, "
            "temple or prayer hall mood, "
            "no vocals"
        ),
        "temperature": 0.9
    },

    "Romantic Film": {
        "base_prompt": (
            "Romantic Indian film instrumental music, "
            "piano and string sections, "
            "gentle flute accents, "
            "emotional melodic flow, "
            "soft cinematic percussion, "
            "slow tempo, "
            "movie soundtrack style, "
            "no vocals"
        ),
        "temperature": 1.0
    },

    "Cinematic Epic": {
        "base_prompt": (
            "Epic cinematic orchestral instrumental music, "
            "grand string ensemble, "
            "choir-style pads without vocals, "
            "powerful drums and percussion, "
            "dramatic build-ups, "
            "inspirational heroic mood, "
            "film trailer score style"
        ),
        "temperature": 1.1
    },

    "Lo-Fi Chill": {
        "base_prompt": (
            "Lo-fi chill instrumental music, "
            "soft piano chords, "
            "warm analog synth pads, "
            "subtle ambient textures, "
            "relaxed modern mood, "
            "slow tempo, "
            "no vocals"
        ),
        "temperature": 0.65
    }
}

