"""Apply the existing scene audit with the added camera roll helper excluded."""
from pathlib import Path
source=Path(__file__).with_name('verify_preservation.py').read_text()
source=source.replace("not o.name.startswith('CR_REVEAL_')","not o.name.startswith(('CR_REVEAL_','CR_ROLL_'))")
exec(compile(source,'verify-preservation-with-roll-helper','exec'))
