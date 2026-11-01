#!/usr/bin/env python3
"""Package the White & Cyan review pages with self-contained image previews."""
from __future__ import annotations

import base64
import io
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
V1 = ROOT.parent / "white-cyan-study-v001"
SHOTS = ("0057", "0132", "0390", "0600", "0780", "skyline")

STYLE = """*{box-sizing:border-box}body{margin:0;background:#eaf0f2;color:#182f3a;font:16px/1.6 system-ui,sans-serif}main{max-width:1400px;margin:auto;padding:30px 24px}h1{font-size:28px;margin:0}p{margin:8px 0 22px;color:#52636d}nav{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:18px}button{font:inherit;padding:8px 14px;border:1px solid #adbdc5;border-radius:5px;background:white;color:inherit;cursor:pointer}button[aria-pressed=true]{background:#007da7;color:white;border-color:#007da7}.compare{position:relative;aspect-ratio:16/9;overflow:hidden;background:#c8d5db}.compare img{position:absolute;inset:0;width:100%;height:100%;object-fit:contain}.before{clip-path:inset(0 calc(100% - var(--split,50%)) 0 0)}.line{position:absolute;inset:0 auto 0 var(--split,50%);width:2px;background:#00abe1;pointer-events:none}.label{position:absolute;top:12px;padding:5px 10px;border-radius:4px;background:#ffffffe8;font-size:13px}.old{left:12px}.new{right:12px}.control{display:flex;gap:18px;align-items:center;padding:18px 0}.control input{flex:1;accent-color:#007da7;min-width:80px}a{color:#006e95}footer{font-size:13px;color:#586d78}button:focus-visible,input:focus-visible{outline:3px solid #00abe1;outline-offset:3}.status{padding:8px 12px;color:#9c3525;display:none}.compare.failed .status{display:block}"""


def data_url(path: Path) -> tuple[str, int]:
    if not path.is_file():
        raise FileNotFoundError(path)
    with Image.open(path) as im:
        im = im.convert("RGB")
        if im.width > 1500:
            h = round(im.height * 1500 / im.width)
            im = im.resize((1500, h), Image.Resampling.LANCZOS)
        out = io.BytesIO()
        im.save(out, format="JPEG", quality=90, optimize=True, progressive=True)
    raw = out.getvalue()
    return "data:image/jpeg;base64," + base64.b64encode(raw).decode("ascii"), len(raw)


def build(target: Path, title: str, subtitle: str, before_label: str,
          after_label: str, before_folder: Path, before_prefix: str,
          after_folder: Path, after_prefix: str, blend_path: str,
          record_path: str) -> None:
    sources: dict[str, dict[str, str]] = {}
    weights: dict[str, dict[str, int]] = {}
    for key in SHOTS:
        sources[key], weights[key] = {}, {}
        for side, folder, prefix in (("before", before_folder, before_prefix),
                                     ("after", after_folder, after_prefix)):
            uri, nbytes = data_url(folder / f"{prefix}-{key}.png")
            sources[key][side] = uri
            weights[key][side] = nbytes

    page = f'''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title>
<style>{STYLE}</style><main><h1>{title}</h1><p>{subtitle}</p>
<nav aria-label="비교 장면"><button data-shot="0057">적재 · 57</button><button data-shot="0132">중국 전경 · 132</button><button data-shot="0390">미국 항만 · 390</button><button data-shot="0600">트럭 · 600</button><button data-shot="0780">창고 작업 · 780</button><button data-shot="skyline">상하이 확대</button></nav>
<div class="compare" id="compare"><img id="after" alt="개선 재질"><img id="before" class="before" alt="이전 재질"><div class="line"></div><span class="label old">{before_label}</span><span class="label new">{after_label}</span><div class="status" role="status">검토 이미지를 불러오지 못했습니다. 페이지 파일이 손상되었는지 확인하세요.</div></div>
<div class="control"><button id="show-before">{before_label}</button><label for="split">비교 경계</label><input id="split" type="range" min="0" max="100" value="50"><button id="show-after">{after_label}</button></div>
<footer>같은 CAM_MASTER 프레임 · Cycles OPTIX · 40 samples · 기존 지형·카메라·애니메이션 유지<br><a href="{blend_path}">실험 Blender 파일</a> · <a href="{record_path}">재질 설정과 검증 기록</a><br>이 HTML은 검토 이미지를 내부에 포함합니다. 이미지 파일을 따로 복사하지 않아도 열 수 있습니다.</footer></main>
<script>const images={json.dumps(sources, ensure_ascii=False, separators=(',', ':'))};const panel=document.getElementById('compare'),range=document.getElementById('split');function split(n){{range.value=n;panel.style.setProperty('--split',n+'%');range.setAttribute('aria-valuetext','이전 '+n+'%, 개선 '+(100-n)+'%')}}range.addEventListener('input',()=>split(range.value));document.getElementById('show-before').onclick=()=>split(100);document.getElementById('show-after').onclick=()=>split(0);function shot(key){{document.getElementById('after').src=images[key].after;document.getElementById('before').src=images[key].before;panel.style.aspectRatio=key==='skyline'?'8/5':'16/9';document.querySelectorAll('[data-shot]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.shot===key)));panel.classList.remove('failed')}}document.querySelectorAll('[data-shot]').forEach(b=>b.onclick=()=>shot(b.dataset.shot));document.querySelectorAll('.compare img').forEach(i=>i.onerror=()=>panel.classList.add('failed'));shot('0132');split(50)</script></html>'''
    target.write_text(page, encoding="utf-8")
    total = sum(n for pair in weights.values() for n in pair.values())
    target.with_name("review-package.json").write_text(json.dumps({
        "html": str(target), "embedded": True, "format": "JPEG q90, max width 1500",
        "sourceFrames": weights, "embeddedImageBytes": total,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {target} ({target.stat().st_size:,} bytes; {total:,} compressed preview bytes embedded)")


if __name__ == "__main__":
    build(ROOT / "review" / "index.html",
          "PNPLINE · White & Cyan · Glass and roof contrast",
          "이전 백색 실험본과 유리·지붕 명암을 개선한 결과를 같은 카메라·조명으로 비교합니다. 바다 재질은 유지했습니다.",
          "이전 실험", "유리·지붕 명암 개선", V1 / "review", "white",
          ROOT / "review", "white", "../pnpline-white-cyan-study-v002.blend", "../study.json")
    build(V1 / "review" / "index.html",
          "PNPLINE · White & Cyan",
          "기존 컬러 재질과 흰색·회색 중심의 실험 재질을 같은 카메라·조명으로 비교합니다. 바다 재질은 유지했습니다.",
          "기존 재질", "White & Cyan 실험", V1 / "review", "original",
          V1 / "review", "white", "../pnpline-white-cyan-study-v001.blend", "../study.json")
