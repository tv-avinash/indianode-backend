from typing import List, Dict


class VocalOrchestrationService:
    """
    Builds a singer-aware vocal timeline from paced lyrics.
    """

    def build(
        self,
        paced_segments: List[Dict],
        singer_type: str
    ) -> List[Dict]:
        """
        Args:
            paced_segments: output from VocalPacingService
            singer_type: male | female | duet

        Returns:
            Timeline for voice synthesis
        """

        timeline = []
        current_time = 0.0

        for idx, seg in enumerate(paced_segments):
            singer = self._assign_singer(idx, singer_type)

            timeline.append({
                "singer": singer,
                "text": seg["text"],
                "start_sec": round(current_time, 2),
                "duration_sec": seg["sing_duration_sec"]
            })

            current_time += seg["sing_duration_sec"] + seg["post_pause_sec"]

        return timeline

    def _assign_singer(self, index: int, singer_type: str) -> str:
        """
        Determines which singer sings a given line.
        """
        if singer_type == "duet":
            # Alternate lines for now (simple & musical)
            return "male" if index % 2 == 0 else "female"

        return singer_type

