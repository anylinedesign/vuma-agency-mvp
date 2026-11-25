# -*- coding: utf-8 -*-
"""[2026-11-25] SNS(OG) 이미지 배경 — ComfyUI(사내 서버)로 글자 없는 배경 생성
사용자: "각 사이트별로 파비콘 이미지, sns이미지 만들어줘 배경이 필요하면 comfyUI로, 편집이 필요하면 vectorCraft로"
  서버: http://192.168.0.18:8188 (z_image_turbo · 이전 PhotoCraft 작업과 같은 노드 구성)
  결과: build/brand_src/bg_<site>.png (1216×640 — VectorCraft 에서 1200×630 판에 채워 넣는다)
  실행: python -X utf8 -I build/brand_src/comfy_bg.py [site ...]
"""
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

BASE = "http://192.168.0.18:8188"
OUT = Path(__file__).resolve().parent
NEG_HINT = "no text, no letters, no logo, no watermark"

# 왼쪽 45% 는 글자가 올라갈 자리 — 비워 두라고 적는다
PROMPTS = {
    "agency": ("minimal 3D illustration, floating glossy rounded white cards and simple table grid panels, violet and lavender accents, "
               "soft purple gradient background, gentle studio lighting, objects grouped on the right side, empty clean space on the left, "
               f"premium SaaS dashboard mood, {NEG_HINT}"),
    "master": ("minimal 3D illustration, deep indigo navy background, glowing violet shield shape and stacked translucent glass panels, "
               "thin neon purple lines, calm control room mood, objects on the right side, dark empty space on the left, "
               f"{NEG_HINT}"),
    "reviewer": ("minimal 3D illustration, soft pastel lavender and peach background, cute glossy speech bubbles, a smartphone, "
                 "small stars and a camera, playful and friendly, objects on the right side, empty clean space on the left, "
                 f"{NEG_HINT}"),
    "demos": ("minimal 3D illustration, three floating rounded glass panels of different heights in violet, lilac and white, "
              "soft purple gradient background, clean studio lighting, objects on the right side, empty space on the left, "
              f"{NEG_HINT}"),
}


def wf(site, prompt, seed):
    return {"client_id": f"vuma-og-{site}", "prompt": {
        "28": {"class_type": "UNETLoader", "inputs": {"unet_name": "z_image_turbo_bf16.safetensors", "weight_dtype": "default"}},
        "11": {"class_type": "ModelSamplingAuraFlow", "inputs": {"model": ["28", 0], "shift": 3}},
        "30": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen_3_4b.safetensors", "type": "lumina2", "device": "default"}},
        "27": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["30", 0], "text": prompt}},
        "33": {"class_type": "ConditioningZeroOut", "inputs": {"conditioning": ["27", 0]}},
        "29": {"class_type": "VAELoader", "inputs": {"vae_name": "ae.safetensors"}},
        "13": {"class_type": "EmptySD3LatentImage", "inputs": {"width": 1216, "height": 640, "batch_size": 1}},
        "3": {"class_type": "KSampler", "inputs": {"model": ["11", 0], "positive": ["27", 0], "negative": ["33", 0], "latent_image": ["13", 0],
                                                   "seed": seed, "steps": 9, "cfg": 1, "sampler_name": "res_multistep", "scheduler": "simple", "denoise": 1}},
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["3", 0], "vae": ["29", 0]}},
        "9": {"class_type": "SaveImage", "inputs": {"images": ["8", 0], "filename_prefix": f"vuma/og_{site}"}},
    }}


def post(path, data):
    req = urllib.request.Request(BASE + path, data=json.dumps(data).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def get(path):
    with urllib.request.urlopen(BASE + path, timeout=60) as r:
        return r.read()


def run(site, seed=1125):
    pid = post("/prompt", wf(site, PROMPTS[site], seed))["prompt_id"]
    for _ in range(180):
        time.sleep(2)
        h = json.loads(get(f"/history/{pid}"))
        if pid in h:
            st = h[pid].get("status", {})
            if st.get("status_str") == "error":
                raise SystemExit(f"{site}: ComfyUI 오류 {st}")
            imgs = [i for o in h[pid]["outputs"].values() for i in o.get("images", [])]
            if imgs:
                i = imgs[0]
                q = urllib.parse.urlencode({"filename": i["filename"], "subfolder": i["subfolder"], "type": i["type"]})
                (OUT / f"bg_{site}.png").write_bytes(get(f"/view?{q}"))
                print(site, "→", OUT / f"bg_{site}.png")
                return
    raise SystemExit(f"{site}: 시간 초과")


if __name__ == "__main__":
    for s in (sys.argv[1:] or list(PROMPTS)):
        run(s)
