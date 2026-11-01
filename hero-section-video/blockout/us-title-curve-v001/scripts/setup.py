from pathlib import Path
R=Path(__file__).resolve().parents[1]
old=R.parent/'us-city-density-v001'
code=(old/'scripts/audit_preservation.py').read_text(encoding='utf-8')
code=code.replace("SOURCE=BLOCKOUT/'cn-shanghai-density-v001/pnpline-cn-shanghai-density-v001.blend'","SOURCE=BLOCKOUT/'us-city-density-v001/pnpline-us-city-density-v001.blend'")
code=code.replace('c0f7d784dbb67562614cfd46cc3a493418de6f6712db2aef2d8933fbee5672ce','90cf22b0693b0d3702236f88a3871da371491090c7b9a2d1d70d58047f22da9a')
code=code.replace("CANDIDATE=ROOT/'pnpline-us-city-density-v001.blend'","CANDIDATE=ROOT/'pnpline-us-title-curve-v001.blend'")
code=code.replace("startswith('USD_')","startswith('UST_')").replace('new_objects_all_USD_prefix','new_objects_all_UST_prefix')
(R/'scripts/audit_preservation.py').write_text(code,encoding='utf-8')
(R/'scripts/render_review.py').write_text((old/'scripts/render_review.py').read_text(encoding='utf-8'),encoding='utf-8')

