import re
from dataclasses import dataclass
from pathlib import Path


TIMESTAMP_PATTERN = re.compile(
    r"(?P<start>\d{2}:\d{2}:\d{2}[,.]\d{3})\s+-->\s+"
    r"(?P<end>\d{2}:\d{2}:\d{2}[,.]\d{3})"
)


@dataclass(frozen=True)
class Cue:
    start_ms: int
    end_ms: int
    text: str = ""


def _timestamp_to_ms(value: str) -> int:
    hours, minutes, seconds = value.replace(",", ".").split(":")
    whole_seconds, milliseconds = seconds.split(".")
    return (
        int(hours) * 3_600_000
        + int(minutes) * 60_000
        + int(whole_seconds) * 1_000
        + int(milliseconds.ljust(3, "0")[:3])
    )


def parse_srt(path: Path) -> list[Cue]:
    text = path.read_text(encoding="utf-8-sig")
    cues = []
    
    matches = list(TIMESTAMP_PATTERN.finditer(text))
    for i, match in enumerate(matches):
        start_ms = _timestamp_to_ms(match.group("start"))
        end_ms = _timestamp_to_ms(match.group("end"))
        if end_ms <= start_ms:
            raise ValueError("An SRT cue has an end time before its start time.")
            
        text_start = match.end()
        text_end = matches[i+1].start() if i + 1 < len(matches) else len(text)
        
        cue_text = text[text_start:text_end].strip()
        lines = cue_text.splitlines()
        while lines and (not lines[-1].strip() or lines[-1].strip().isdigit()):
            lines.pop()
            
        clean_text = "\n".join(lines).strip()
        cues.append(Cue(start_ms=start_ms, end_ms=end_ms, text=clean_text))

    if not cues:
        raise ValueError("The SRT file does not contain any valid timestamp cues.")

    for previous, current in zip(cues, cues[1:]):
        if current.start_ms <= previous.start_ms:
            raise ValueError("SRT cue start times must be in strictly increasing order.")

    return cues
