# -*- coding: utf-8 -*-
"""[2026-11-25] 사이트별 파비콘 · SNS(OG) 태그 — 모든 생성기의 <head> 에서 같이 쓴다
사용자: "각 사이트별로 파비콘 이미지, sns이미지 만들어줘"
  이미지: img/brand/ (build/brand_src/build_brand.py — ComfyUI 배경 + VectorCraft 편집)
  head(site, prefix): site = agency | master | reviewer (사이트 3곳 기준), prefix = 페이지에서 사이트 뿌리까지("" 또는 "../")
  og:image · og:url 은 SNS 가 읽도록 절대 주소(GitHub Pages)
"""
from html import escape

BASE = "https://anylinedesign.github.io/vuma-agency-mvp/"
SITE_INFO = {  # [2026-11-25] 사이트 기준 문구 — OG 이미지(build_brand.py)와 같은 말
    "agency":   ("뷰마 대행사", "여러 업체의 체험단 캠페인을 한곳에서 운영하는 대행사 관리 사이트", "dashboard.html"),
    "master":   ("뷰마 마스터", "캠페인 심사 · 정산 · 회원 관리까지, 뷰마 운영자 관리 사이트", "master/"),
    "reviewer": ("뷰마 리뷰어", "체험단 신청부터 리뷰 · 포인트까지, 리뷰어를 위한 체험단 플랫폼", "reviewer/"),
}


def head(site, prefix=""):
    title, desc, path = SITE_INFO[site]
    img = f"{BASE}img/brand/og-{site}.png"
    t, d = escape(title), escape(desc)
    return (f'<link rel="icon" href="{prefix}img/brand/favicon-{site}.svg" type="image/svg+xml">\n'
            f'<link rel="icon" href="{prefix}img/brand/favicon-{site}-32.png" sizes="32x32" type="image/png">\n'
            f'<link rel="alternate icon" href="{prefix}img/brand/favicon-{site}.ico">\n'
            f'<link rel="apple-touch-icon" href="{prefix}img/brand/apple-touch-{site}.png">\n'
            f'<meta name="description" content="{d}">\n'
            f'<meta property="og:type" content="website">\n'
            f'<meta property="og:site_name" content="뷰마 데모">\n'
            f'<meta property="og:title" content="{t}">\n'
            f'<meta property="og:description" content="{d}">\n'
            f'<meta property="og:url" content="{BASE}{path}">\n'
            f'<meta property="og:image" content="{img}">\n'
            f'<meta property="og:image:width" content="1200">\n'
            f'<meta property="og:image:height" content="630">\n'
            f'<meta property="og:image:alt" content="{t}">\n'
            f'<meta name="twitter:card" content="summary_large_image">\n'
            f'<meta name="twitter:title" content="{t}">\n'
            f'<meta name="twitter:description" content="{d}">\n'
            f'<meta name="twitter:image" content="{img}">')
