"""Run the established preservation audit with the continuous tracking join at672."""
from pathlib import Path
source=Path(__file__).with_name('verify_preservation.py').read_text()
source=source.replace('[0,1,380,408,439,439.5,440,648,648.5,649,672,900,1392]',
                      '[0,1,380,408,439,439.5,440,672,672.5,673,696,900,1392]')
exec(compile(source,'preservation-continuous-camera-window','exec'))
