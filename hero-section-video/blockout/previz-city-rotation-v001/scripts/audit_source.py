import bpy,ast,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];reference=R.parent/'route-b-a-side-v001/review/reproduced-city.blend';current=Path(bpy.data.filepath)
tree=ast.parse((R.parent/'s2-styleframe-match-v001/scripts/verify_title_water.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in {'digest','actions','objects'}],type_ignores=[]),'<pure>','exec'))
# Reuse comparison implementation, not top-level promotion or verification actions.
tree=ast.parse((R/'scripts/verify.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='snap'],type_ignores=[]),'<snapshot>','exec'))
a=snap();bpy.ops.wm.open_mainfile(filepath=str(reference));b=snap();checks={k:a[k]==b[k]for k in a};diffs={k:[n for n in a[k].keys()|b[k].keys()if a[k].get(n)!=b[k].get(n)]for k in ['objects','actions','links','collections']}
report={'source':str(current),'current_sha256':hashlib.sha256(current.read_bytes()).hexdigest(),'reviewed_source_sha256':'149491c3f28cad65865e19c462843d7ffbefda8c9fc892dbdabce2a2f8e3ca80','reference':str(reference),'reference_sha256':hashlib.sha256(reference.read_bytes()).hexdigest(),'checks':checks,'differences':diffs}
(R/'source-audit.json').write_text(json.dumps(report,indent=2));print(json.dumps(report));assert all(checks.values()),checks
