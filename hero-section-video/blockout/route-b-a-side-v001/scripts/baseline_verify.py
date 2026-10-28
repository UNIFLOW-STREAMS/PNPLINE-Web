from pathlib import Path
R=Path(__file__).resolve().parents[1]
p=R.parent/'previz-styleframe-integrated-v001/scripts/verify.py'
code=p.read_text().replace("(R/'review/integration-verified.json').write_text",repr(str(R/'review/baseline-integration-verified.json'))+'.__PLACEHOLDER__')
code=code.replace(repr(str(R/'review/baseline-integration-verified.json'))+'.__PLACEHOLDER__','Path('+repr(str(R/'review/baseline-integration-verified.json'))+').write_text')
exec(compile(code,str(p),'exec'),{'__file__':str(p),'__name__':'__main__'})
