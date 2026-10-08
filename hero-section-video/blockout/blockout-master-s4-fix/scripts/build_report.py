"""Current report entry point; previous builder is retained in review/close-reveal."""
import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).with_name('build_close_reveal_report.py')),run_name='__main__')
