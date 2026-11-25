# -*- coding: utf-8 -*-
"""[2026-11-25] 사이트별 파비콘 · SNS(OG) 이미지 — VectorCraft CLI 로 편집 · 내보내기
사용자: "각 사이트별로 파비콘 이미지, sns이미지 만들어줘 배경이 필요하면 comfyUI로, 편집이 필요하면 vectorCraft로"
  사이트 3곳: agency(대행사 사이트) · master(마스터 사이트) · reviewer(리뷰어 사이트)
  [2026-11-25] 사용자: "마스터 사이트 · 리뷰어 사이트 · 대행사 사이트 이 기준으로, url 기입 불필요, 타이틀과 설명 배경요소만으로"
    → OG = 배경 + 대비 막 + 사이트 제목 + 설명 두 줄. 주소 · 데모 표시 · 표식 · 라벨 없음
  배경: comfy_bg.py 가 만든 bg_<site>.png (ComfyUI)
  결과(img/brand/):
    favicon-<site>.svg · favicon-<site>-32.png · apple-touch-<site>.png(180) · favicon-<site>.ico(16·32·48)
    og-<site>.png (1200×630)
  편집 원본(build/brand_src/): fav_<site>.vectorcraft · og_<site>.vectorcraft — VectorCraft 앱에서 열어 고칠 수 있다
  실행: python -X utf8 -I build/brand_src/build_brand.py
"""
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image

VC = r"C:\Users\jeonj\AppData\Local\Programs\ArtCraft\VectorCraft\vectorcraft-cli.exe"
SRC = Path(__file__).resolve().parent
OUT = SRC.parent.parent / "img" / "brand"
FONT = "Noto Sans KR"

# 사이트별 색 · 글자 — 파비콘은 16px 에서도 읽히게 라틴 한 글자
SITES = {
    "agency":   {"letter": "A", "tile": ("#8b64ff", "#5b2fe0"), "ink": "#ffffff", "ring": None,
                 "title": "뷰마 대행사", "sub": ["여러 업체의 체험단 캠페인을", "한곳에서 운영하는 대행사 관리 사이트"],
                 "shade": "#3d1fb0"},
    "master":   {"letter": "M", "tile": ("#2a2350", "#120f26"), "ink": "#b49bff", "ring": None,
                 "title": "뷰마 마스터", "sub": ["캠페인 심사 · 정산 · 회원 관리까지", "뷰마 운영자 관리 사이트"],
                 "shade": "#0b0a1c"},
    "reviewer": {"letter": "R", "tile": ("#a77bff", "#ff8fa8"), "ink": "#ffffff", "ring": None,
                 "title": "뷰마 리뷰어", "sub": ["체험단 신청부터 리뷰 · 포인트까지", "리뷰어를 위한 체험단 플랫폼"],
                 "light_bg": True, "shade": "#ffffff"},
}


class Doc:
    """VectorCraft 명령 목록 쌓기 — 이전 PhotoCraft 배너 작업(build_banner.py)과 같은 방식"""
    def __init__(self):
        self.steps = []

    def c(self, cmd, **p):
        self.steps.append({"command": cmd, "params": p})
        return len(self.steps) - 1

    def name(self, n):
        self.c("object.setProps", name=n)

    def rect(self, nm, x, y, w, h, fill, r=0, stroke=None, sw=0):
        self.c("shape.rectangle", x=x, y=y, width=w, height=h, **({"radius": r} if r else {}))
        self.c("paint.setFill", **(fill if isinstance(fill, dict) else {"color": fill}))
        if stroke:
            self.c("paint.setStroke", color=stroke)
            self.c("stroke.set", weight=sw)
        else:
            self.c("paint.setStroke", none=True)
        self.name(nm)

    def text(self, nm, x, y, s, size, color, style="Bold", tracking=None, justify=None):
        kw = {"justify": justify} if justify else {}
        self.c("text.create", x=x, y=y, text=s, font=FONT, style=style, size=size, color=color, **kw)
        if tracking is not None:
            self.c("text.setStyle", tracking=tracking)
        self.name(nm)


def grad(a, b, angle=-45):
    return {"gradient": {"kind": "linear", "angle": angle, "stops": [{"offset": 0, "color": a}, {"offset": 1, "color": b}]}}


def tile(d, s, x, y, size, prefix):
    """글자 타일 — 파비콘이자 OG 왼쪽 위 표식"""
    r = round(size * 0.22, 2)
    ring = s["ring"]
    d.rect(f"{prefix}_타일", x, y, size, size, grad(*s["tile"]), r=r, stroke=ring, sw=round(size * 0.06, 2) if ring else 0)
    d.text(f"{prefix}_글자", x + size / 2, y + size * 0.765, s["letter"], round(size * 0.64, 2), s["ink"], style="Black", justify="center")


def run(steps, exports, tag):
    f = SRC / f"_cmds_{tag}.json"
    f.write_text(json.dumps(steps, ensure_ascii=False), encoding="utf-8")
    args = [VC, "run", "--commands", str(f)]
    for e in exports:
        args += ["--export", str(e)]
    r = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace")
    bad = [ln for ln in r.stdout.splitlines() if '"ok":false' in ln.replace(" ", "") or '"error"' in ln]
    if r.returncode or bad:
        print(r.stdout[-2000:], r.stderr[-2000:])
        raise SystemExit(f"{tag}: VectorCraft 실패")
    f.unlink()


def convert(src, dst, *extra):
    r = subprocess.run([VC, "convert", str(src), str(dst), *extra], capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode:
        print(r.stdout[-1500:], r.stderr[-1500:])
        raise SystemExit(f"convert 실패 {dst}")


def favicon(site, s):
    d = Doc()
    d.c("file.new", name=f"favicon-{site}", width=64, height=64, units="Pixels", colorMode="rgb")
    d.c("layer.setProps", name="파비콘")
    tile(d, s, 2, 2, 60, "파비콘")
    vc = SRC / f"fav_{site}.vectorcraft"
    run(d.steps, [vc], f"fav_{site}")
    convert(vc, OUT / f"favicon-{site}.svg", "--outline-text")       # 글꼴 없이도 같은 모양
    convert(vc, OUT / f"favicon-{site}-32.png", "--scale", "0.5")
    convert(vc, OUT / f"apple-touch-{site}.png", "--scale", "2.8125")  # 180px
    big = SRC / f"_fav_{site}_256.png"
    convert(vc, big, "--scale", "4")
    Image.open(big).convert("RGBA").save(OUT / f"favicon-{site}.ico", sizes=[(16, 16), (32, 32), (48, 48)])
    big.unlink()


def og(site, s):
    W, H = 1200, 630
    d = Doc()
    d.c("file.new", name=f"og-{site}", width=W, height=H, units="Pixels", colorMode="rgb")
    d.c("layer.setProps", name="01 배경 (ComfyUI)")
    d.c("file.place", path=str(SRC / f"bg_{site}.png"), rect=[-8, -5, 1216, 640], link=False)
    d.name(f"배경 bg_{site}.png")
    # 글자 자리(왼쪽)를 눌러 대비를 맞춘다 — 왼쪽 진하게 → 60% 지점에서 사라짐
    d.c("layer.new", name="02 대비 막")
    if s.get("light_bg"):
        stops = [{"offset": 0, "color": "#ffffff", "opacity": 0.78}, {"offset": 0.58, "color": "#ffffff", "opacity": 0}]
    else:
        stops = [{"offset": 0, "color": s["shade"], "opacity": 0.72}, {"offset": 0.6, "color": s["shade"], "opacity": 0}]
    d.rect("왼쪽 대비 막", 0, 0, W, H, {"gradient": {"kind": "linear", "angle": 0, "stops": stops}})

    d.c("layer.new", name="03 글자 (제목 · 설명만)")
    ink = "#241a52" if s.get("light_bg") else "#ffffff"
    sub = "#4a3f7a" if s.get("light_bg") else "#ece6ff"
    d.text("제목", 76, 292, s["title"], 92, ink, style="Black", tracking=-30)
    for i, line in enumerate(s["sub"]):
        d.text(f"설명{i + 1}", 80, 368 + i * 48, line, 32, sub, style="Medium", tracking=-15)
    vc = SRC / f"og_{site}.vectorcraft"
    run(d.steps, [vc, OUT / f"og-{site}.png"], f"og_{site}")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    only = sys.argv[1:] or list(SITES)
    for k in only:
        favicon(k, SITES[k])
        og(k, SITES[k])
        print("ok", k)
