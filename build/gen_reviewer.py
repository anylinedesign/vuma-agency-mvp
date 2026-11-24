# -*- coding: utf-8 -*-
"""
[2026-11-23] 뷰마 리뷰어 대시보드 데모 — reviewer/index.html 생성
  기획: D:\\WORK\\후기닷컴\\조사\\20261123\\리뷰어대시보드_분석·기획.md
  틀 = 실서버 리뷰어 마이페이지 그대로
    헤더(inc/header.inc.html) + MY디마 사이드바(inc/mypageSidebar.inc.html) + 본문 + 미니 달력(inc/mypage/miniCalendar.inc.html)
    CSS = reviewer/css/ 의 실서버 복사본(variables · reset · common · components · my-campaign · my-minical — 고치지 않음)
          + reviewer/css/rd.css (대시보드 추가분, rd- 접두어)
  JS 없음 — 창은 popover, 미니 달력 날짜는 radio, 달력 서랍은 checkbox(실서버와 같은 방식)
  실행: python -X utf8 -I build/gen_reviewer.py

[2026-11-24 v2] 사용자: "리뷰어 대시보드도 마찬가지로 수정(대행사 대시보드처럼) · 기존 버전 남기고 새 버전으로"
  · v1 = versions/reviewer-v1/ (그대로 보관, 고치지 않음)
  · 상단 써머리(숫자 4칸) · 패널티 띠 제거 → 패널티는 왼쪽 '받은 알림'의 한 줄로
  · 본문 2열: 왼쪽 = 받은 알림(성격별 한 줄, 먼저 확인 / 알아 두기) · 오른쪽 = 지금 할 일 · 진행 현황 · 이번 주 일정 · 내 포인트를 표로
  · 종류 줄을 누르면 오른쪽 패널(popover 서랍)에 그 종류 목록 — JS 없음
  · 선 처리 · 표처럼 = reviewer/css/rd-line.css
"""
import datetime as dt
import hashlib
from html import escape as h
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "reviewer"
TODAY = dt.date(2026, 11, 23)
WEEK = "월화수목금토일"
NICK = "리뷰하는민지"


def md(d):
    return f"{d.month}/{d.day}"


def mdw(d):
    return f"{d.month}.{d.day:02d} ({WEEK[d.weekday()]})"


def dday(d):
    n = (d - TODAY).days
    return "오늘" if n == 0 else (f"D-{n}" if n > 0 else f"{-n}일 지남")


def urg(d):
    n = (d - TODAY).days
    return "hot" if n <= 0 else ("soon" if n <= 3 else "later")


def ver(name):
    return hashlib.md5((OUT / "css" / name).read_bytes()).hexdigest()[:8]


def D(n):
    """오늘에서 n일 뒤"""
    return TODAY + dt.timedelta(days=n)


# ── 데이터(시안) ─────────────────────────────────────────────────
# 지금 할 일: (기한, 종류, 캠페인, 설명, 버튼, 창 key)  — 실서버 버튼 문구 그대로
TODO = [
    (D(0), "리뷰 마감", "[성수] 브런치 카페 2인 체험", "체험이 끝났어요. 오늘까지 올리면 패널티가 없어요(유예 마지막 날)", "리뷰등록", "review"),
    (D(2), "반려된 리뷰", "[연남] 신메뉴 시식 리뷰", "반려 사유: 사진 3장 미만 · 필수 키워드 '연남 브런치' 없음", "리뷰 재등록", "review"),
    (D(1), "체험 마감", "[망원] 홈카페 원두 배송", "배송 받은 원두로 체험 중 — 마감까지 리뷰를 올려 주세요", "리뷰등록", "review"),
    (D(3), "방문일자 미등록", "[합정] 파스타 2인 방문", "광고주와 협의한 방문일을 등록해 두세요", "방문일자 등록", "visit"),
    (D(2), "받은 제안", "[강남] 피부관리 체험 · 추가 +5,000P", "광고주가 먼저 제안했어요. 기한 안에 신청하면 추가 포인트를 받아요", "캠페인 보고 신청하기", "offer"),
    (D(24), "연장 요청 가능", "[잠실] 키즈카페 체험", "리뷰 기간이 6일 지났어요. 광고주가 받아 주면 3일 더 올릴 수 있어요", "광고주에게 연장 요청", "extend"),
    (None, "출금 준비", "출금계좌 미등록", "포인트가 1,000P를 넘었어요. 출금하려면 계좌를 등록해 주세요", "출금계좌 등록", "bank"),
]
# 진행 현황: (단계, 수, 보조 신호, 신호 강조?, 실서버 화면)
FLOW = [
    ("신청중", 4, "오늘 발표 1", True, "campaignApplying"),
    ("선정됨", 3, "체험 중 2", False, "campaignSelected"),
    ("리뷰 미완료", 2, "유예 중 1 · 종료 1", True, "campaignMissed"),
    ("검수중", 1, "광고주 확인 중", False, "campaignDone"),
    ("지급대기", 2, "+45,000P 예정", False, "campaignDone"),
    ("완료", 18, "누적", False, "campaignDone"),
]
POINT = {"now": 12500, "due": 45000, "due_n": 2, "last": ("11/10", 30000, "입금완료")}
CHECKS = [("1,000P 이상", True), ("본인 인증", True), ("출금계좌 등록", False)]
# 이번 주 일정: (날짜, 색, 이슈, 캠페인)  — 색 이름은 실서버 달력(scheduleFeed) 그대로
SCHED = [
    (D(0), "orange", "리뷰 마감", "[성수] 브런치 카페 2인 체험"),
    (D(0), "blue", "발표", "[홍대] 인스타 릴스 체험"),
    (D(1), "green", "체험 마감", "[망원] 홈카페 원두 배송"),
    (D(2), "pink", "방문 14:00", "[을지로] 오마카세 런치"),
    (D(2), "orange", "리뷰 마감 (반려 재등록)", "[연남] 신메뉴 시식 리뷰"),
    (D(3), "green", "체험 마감", "[합정] 파스타 2인 방문"),
    (D(3), "blue", "발표", "[강남] 필라테스 1회 체험"),
    (D(5), "green", "체험 시작", "[판교] 젤네일 체험"),
]
# 소식: (아이콘 글자, 제목, 값, 설명, 강조, 실서버 화면)
NEWS = [
    ("제안", "받은 제안", "2건", "추가 +5,000P · 기한 가장 빠른 것 D-2", True, "offers"),
    ("쪽지", "안 읽은 쪽지", "3", "검수 결과 쪽지 1 포함", True, "noteList"),
    ("알림", "안 읽은 알림", "5", "선정 1 · 연장 1 · 공지 3", False, "messageList"),
    ("문의", "1:1 문의", "새 답변 1", "포인트·패널티 문의", True, "inquiry"),
    ("영상", "받은 영상", "게시 대기 1", "릴스 — 주소 등록 전", False, "video"),
    ("SNS", "SNS 연결", "인스타 승인 대기", "블로그 · 유튜브 연결됨", False, "snsConnect"),
    ("찜", "찜한 캠페인", "마감 임박 1", "[분당] 베이커리 클래스 모집마감 D-1", False, "campaignPick"),
]
# [2026-11-24 v2] 받은 알림 — 성격별 (등급, key, 이름, 실서버 화면, [(제목, 설명, 언제)])
AL = [
    ("u", "penalty", "패널티", "penalty", [("누적 패널티 1점", "2점 더 받으면 30일 캠페인 신청 제한", "11/18"),
                                         ("리뷰 기한 초과 +1점", "[부천] 떡볶이 체험 — 기한 안에 리뷰 없음", "11/18")]),
    ("u", "offer", "받은 제안", "offers", [("[강남] 피부관리 체험 · 추가 +5,000P", "제안 기한 D-2", "오늘"),
                                          ("[분당] 베이커리 클래스", "제안 기한 D-5", "어제")]),
    ("u", "note", "안 읽은 쪽지", "noteList", [("검수 결과 안내", "[연남] 신메뉴 시식 리뷰 — 반려 사유", "1시간 전"),
                                              ("방문 일정 확인 부탁드려요", "[합정] 파스타 2인 방문 광고주", "3시간 전"),
                                              ("배송 출발했어요", "[망원] 홈카페 원두 배송 광고주", "어제")]),
    ("u", "inquiry", "1:1 문의 답변", "inquiry", [("포인트 지급일 문의 — 새 답변", "운영팀 답변 도착", "2시간 전")]),
    ("i", "alarm", "안 읽은 알림", "messageList", [("선정 안내", "[홍대] 인스타 릴스 체험에 선정되었어요", "오늘"),
                                                ("연장 승인", "[잠실] 키즈카페 체험 — 3일 연장", "어제"),
                                                ("공지", "리뷰어 개인정보처리방침 개정 안내", "어제"),
                                                ("공지", "12월 정기 점검 안내", "11/20"),
                                                ("공지", "기자단 캠페인 가이드 변경", "11/19")]),
    ("i", "video", "받은 영상", "video", [("릴스 — 게시 대기", "[홍대] 인스타 릴스 체험 · 주소 등록 전", "어제")]),
    ("i", "sns", "SNS 연결", "snsConnect", [("인스타 승인 대기", "블로그 · 유튜브는 연결됨", "11/21")]),
    ("i", "pick", "찜한 캠페인", "campaignPick", [("[분당] 베이커리 클래스", "모집마감 D-1", "오늘")]),
]
AL_LV = {"u": ("먼저 확인", "놓치면 손해"), "i": ("알아 두기", "읽어 두면 되는 것")}
PENALTY = {"pt": 1, "next": 3, "rule": "3점부터 30일 신청 제한(실서버 '패널티 점수별 제재 기준')"}

MENU = [  # 실서버 사이드바 순서 그대로 + 맨 위 '대시보드'(새로)
    ("dashboard", "대시보드"), ("campaignApplying", "나의 캠페인"), ("campaignPick", "찜한 캠페인"),
    ("messageList", "알림내역"), ("schedule", "나의 일정"), ("video", "받은 영상"), ("point", "포인트"),
    ("penalty", "패널티"), ("noteList", "쪽지함"), ("infoBasic", "내 정보 관리"), ("snsConnect", "SNS 연결"),
    ("blockedAdvertisers", "차단 광고주"), ("offers", "받은 제안"), ("inquiry", "1:1 문의"), ("withdraw", "회원 탈퇴"),
]
STUB = {k: n for k, n in MENU}
STUB.update({"campaignSelected": "나의 캠페인 › 2.선정됨", "campaignMissed": "나의 캠페인 › 3.리뷰등록미완료",
             "campaignDone": "나의 캠페인 › 4.리뷰등록완료"})
# 버튼 창(실서버 입력창 안내)
POPS = {
    "review": ("리뷰등록", "실서버 '리뷰등록' 창이 열립니다.", "반려 사유 · 검수 조건 · 리뷰 URL · 사진 확인 → [등록]. 네이버 블로그는 자동 판정으로 조건을 못 맞추면 등록되지 않습니다."),
    "visit": ("방문일자 등록", "실서버 '방문일자 등록' 창이 열립니다.", "광고주와 협의한 방문 날짜·시간을 넣으면 나의 일정과 달력에 '방문'으로 표시됩니다."),
    "offer": ("받은 제안", "실서버 '받은 제안' 화면의 그 캠페인으로 갑니다.", "캠페인 보고 신청하기 · 거절. 거절하면 같은 캠페인으로 다시 제안받지 않습니다."),
    "extend": ("광고주에게 연장 요청", "실서버 연장 요청이 보내집니다.", "광고주가 받아 주면 3일 동안 다시 리뷰를 올릴 수 있습니다. 마감 후 30일 안에만 요청할 수 있습니다."),
    "bank": ("출금계좌 등록", "실서버 '내 정보 관리 › 출금계좌'로 갑니다.", "계좌를 바꿀 때는 비밀번호를 다시 입력합니다. 출금은 1,000P부터, 처리 중인 신청이 있으면 새로 신청할 수 없습니다."),
    "withdraw": ("출금 신청", "실서버 '포인트 › 출금 신청' 창이 열립니다.", "신청 금액 · 소득세 · 지방소득세 · 송금 수수료 · 실지급 금액을 보여 줍니다. 포인트는 승인될 때 빠집니다."),
}


# ── 조각 ────────────────────────────────────────────────────────
def header():
    nav = ["홈", "전체캠페인", "블로그", "인스타", "유튜브", "릴스", "쇼츠", "클립", "틱톡", "구매평", "배송형", "기자단", "광고문의"]
    items = "".join((f'<div class="header-nav-sep"></div>' if i > 1 else "") + f'<div class="header-nav-item"><a href="#">{n}</a></div>' for i, n in enumerate(nav))
    bell = ('<svg xmlns="http://www.w3.org/2000/svg" width="15" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">'
            '<path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>')
    me = ('<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">'
          '<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>')
    return f'''<header class="site-header">
<div class="header-notice-bar is-unread"><a href="#" class="header-notice-ticker"><span class="header-notice-badge">선정</span><span class="header-notice-text">축하합니다! [홍대] 인스타 릴스 체험에 선정되었어요.</span></a></div>
<div class="header-inner">
	<div class="header-top">
		<button class="header-advertiser-btn" type="button">광고주 바로가기</button>
		<a href="#" class="header-promo header-promo--top"><span class="header-promo-badge">공지사항</span><span class="header-promo-text">[리뷰어 개인정보처리방침] 2026년 12월 11일 개정 안내</span></a>
		<nav class="header-util-links"><a href="#">공지사항</a><a href="#">자주묻는질문</a><a href="#">도움말</a><a href="#">1:1문의</a><a href="#">로그아웃</a></nav>
	</div>
	<div class="header-middle">
		<div class="header-logo-area"><a href="#" class="header-logo">뷰마</a>
			<div class="header-search"><input type="text" placeholder="검색어를 입력하세요, 캠페인 코드로 검색" maxlength="50"><button type="button" class="header-search-btn" aria-label="검색"><svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#7346F3" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg></button></div>
		</div>
		<div class="header-icons">
			<a href="#" class="header-notice-ticker header-notice-ticker--pc is-unread"><span class="header-notice-badge">선정</span><span class="header-notice-text">축하합니다! [홍대] 인스타 릴스 체험에 선정되었어요.</span></a>
			<a href="#" class="header-icon-btn" aria-label="알림"><span class="header-icon-btn__icon">{bell}<span class="header-icon-btn__badge">5</span></span><span class="header-icon-btn__label">알림</span></a>
			<a href="#" class="header-icon-btn" aria-label="MY"><span class="header-icon-btn__icon">{me}</span><span class="header-icon-btn__label">MY</span></a>
		</div>
	</div>
	<div class="header-nav"><nav class="header-nav-list">{items}</nav></div>
</div>
</header>'''


def sidebar():
    rows = []
    for k, n in MENU:
        if k == "dashboard":
            rows.append(f'<a href="#" class="mc-sidenav__item mc-sidenav__item--active rd-menu-new" aria-current="page">{n}<span class="rd-new">새로</span></a>')
        else:
            rows.append(f'<button type="button" class="mc-sidenav__item rd-menu-btn" popovertarget="rd-stub-{k}">{n}</button>')
    return f'''<aside class="mc-sidebar">
	<div class="mc-sidebar__title">MY디마</div>
	<div class="mc-profile"><span class="mc-profile__name"><strong>{NICK}</strong>님</span></div>
	<nav class="mc-sidenav">{"".join(rows)}</nav>
</aside>'''


def stubs():
    out = []
    for k, n in STUB.items():
        if k == "dashboard":
            continue
        out.append(f'<div id="rd-stub-{k}" class="rd-pop" popover><p class="rd-pop__h">{h(n)}</p>'
                   f'<p>이 화면은 실서버의 <b>/mypage/{k}.html</b> 입니다. 데모는 대시보드 한 장만 만들었습니다.</p>'
                   f'<button type="button" class="rd-btn" popovertarget="rd-stub-{k}" popovertargetaction="hide">닫기</button></div>')
    for k, (t, a, b) in POPS.items():
        out.append(f'<div id="rd-act-{k}" class="rd-pop" popover><p class="rd-pop__h">{h(t)}</p><p><b>{h(a)}</b></p><p>{h(b)}</p>'
                   f'<button type="button" class="rd-btn" popovertarget="rd-act-{k}" popovertargetaction="hide">닫기</button></div>')
    return "\n".join(out)


def alert():
    left = PENALTY["next"] - PENALTY["pt"]
    return (f'<div class="rd-alert" role="note"><b>누적 패널티 {PENALTY["pt"]}점</b> — {left}점 더 받으면 캠페인 신청이 제한돼요. '
            f'<span class="rd-alert__sub">{h(PENALTY["rule"])}</span>'
            f'<button type="button" class="rd-link" popovertarget="rd-stub-penalty">패널티 보기 ›</button></div>')


def kpi():
    hot = sum(1 for t in TODO if t[0] is not None and urg(t[0]) == "hot")
    prog = FLOW[1][1] + FLOW[2][1] + FLOW[3][1]
    cells = [
        ("지금 할 일", f"{len(TODO)}", "건", f"오늘 마감 {hot}건", "hot" if hot else ""),
        ("진행 중 캠페인", f"{prog}", "건", "선정 · 리뷰 · 검수", ""),
        ("지급 예정", f"+{POINT['due']:,}", "P", f"검수 승인 {POINT['due_n']}건", "good"),
        ("현재 포인트", f"{POINT['now']:,}", "P", "출금 1,000P부터", ""),
    ]
    return '<dl class="rd-kpi">' + "".join(
        f'<div class="rd-kpi__c{" is-" + t if t else ""}"><dt>{a}</dt><dd><b>{b}</b>{u}<small>{s}</small></dd></div>' for a, b, u, s, t in cells) + "</dl>"


def todo():
    def key(t):
        return (0, (t[0] - TODAY).days) if t[0] is not None else (1, 99)
    rows = []
    for d, kind, name, desc, btn, pop in sorted(TODO, key=key):
        u = urg(d) if d is not None else "later"
        chip = dday(d) if d is not None else "준비"
        rows.append(f'''<li class="rd-todo__i is-{u}">
	<span class="rd-dd">{chip}</span>
	<div class="rd-todo__t"><p class="rd-todo__k">{h(kind)}</p><p class="rd-todo__n">{h(name)}</p><p class="rd-todo__d">{h(desc)}</p></div>
	<button type="button" class="rd-btn rd-btn--pri" popovertarget="rd-act-{pop}">{h(btn)}</button>
</li>''')
    return (f'<section class="rd-card rd-todo" aria-labelledby="rd-todo-h"><div class="rd-card__h"><h2 id="rd-todo-h">지금 할 일 <em>{len(TODO)}</em></h2>'
            f'<ul class="rd-legend"><li class="is-hot">오늘·지남</li><li class="is-soon">3일 안</li><li class="is-later">그 외</li></ul></div>'
            f'<ul class="rd-todo__l">{"".join(rows)}</ul></section>')


def point():
    chk = "".join(f'<li class="{"is-ok" if ok else "is-no"}">{"✓" if ok else "✕"} {h(t)}</li>' for t, ok in CHECKS)
    ready = all(ok for _t, ok in CHECKS)
    btn = ('<button type="button" class="rd-btn rd-btn--pri" popovertarget="rd-act-withdraw">출금 신청</button>' if ready
           else '<button type="button" class="rd-btn rd-btn--pri" popovertarget="rd-act-bank">출금계좌 등록</button>')
    d, amt, st = POINT["last"]
    return f'''<section class="rd-card rd-point" aria-labelledby="rd-pt-h">
	<div class="rd-card__h"><h2 id="rd-pt-h">내 포인트</h2><button type="button" class="rd-link" popovertarget="rd-stub-point">포인트 내역 ›</button></div>
	<p class="rd-point__now"><b>{POINT["now"]:,}</b> P</p>
	<p class="rd-point__due">지급 예정 <b>+{POINT["due"]:,}P</b> <small>검수 승인 {POINT["due_n"]}건 · 지급되면 바로 더해져요</small></p>
	<p class="rd-sub-h">출금 조건</p>
	<ul class="rd-check">{chk}</ul>
	{btn}
	<p class="rd-point__last">최근 출금 {d} · {amt:,}P · <span class="rd-st is-ok">{st}</span></p>
</section>'''


def flow():
    cells = []
    for i, (n, c, s, warn, scr) in enumerate(FLOW):
        cells.append(f'<li><button type="button" class="rd-flow__c" popovertarget="rd-stub-{scr}"><span class="rd-flow__n">{n}</span>'
                     f'<b>{c}</b><span class="rd-flow__s{" is-warn" if warn else ""}">{h(s)}</span></button></li>')
    return (f'<section class="rd-card" aria-labelledby="rd-fl-h"><div class="rd-card__h"><h2 id="rd-fl-h">진행 현황</h2>'
            f'<button type="button" class="rd-link" popovertarget="rd-stub-campaignApplying">나의 캠페인 ›</button></div>'
            f'<ol class="rd-flow">{"".join(cells)}</ol></section>')


def week():
    by = {}
    for d, c, issue, name in SCHED:
        by.setdefault(d, []).append((c, issue, name))
    rows = []
    for i in range(7):
        d = D(i)
        its = by.get(d, [])
        lab = "오늘" if i == 0 else ("내일" if i == 1 else WEEK[d.weekday()])
        body = ("".join(f'<li class="mcal-c--{c}"><i></i><span class="rd-wk__iss">{h(iss)}</span><span class="rd-wk__nm">{h(nm)}</span></li>' for c, iss, nm in its)
                if its else '<li class="rd-wk__none">일정 없음</li>')
        rows.append(f'<div class="rd-wk__d{" is-today" if i == 0 else ""}"><p class="rd-wk__day"><b>{md(d)}</b> {lab}</p><ul>{body}</ul></div>')
    return (f'<section class="rd-card" aria-labelledby="rd-wk-h"><div class="rd-card__h"><h2 id="rd-wk-h">이번 주 일정</h2>'
            f'<button type="button" class="rd-link" popovertarget="rd-stub-schedule">나의 일정 ›</button></div><div class="rd-wk">{"".join(rows)}</div></section>')


def news():
    rows = "".join(
        f'<li><button type="button" class="rd-news__i{" is-on" if on else ""}" popovertarget="rd-stub-{scr}"><span class="rd-news__ic">{h(ic)}</span>'
        f'<span class="rd-news__t">{h(t)}<small>{h(desc)}</small></span><b class="rd-news__v">{h(v)}</b></button></li>'
        for ic, t, v, desc, on, scr in NEWS)
    return f'<section class="rd-card" aria-labelledby="rd-nw-h"><div class="rd-card__h"><h2 id="rd-nw-h">소식</h2></div><ul class="rd-news">{rows}</ul></section>'


def alcol():
    """[2026-11-24 v2] 왼쪽 '받은 알림' — 묶음 머리(먼저 확인 · 알아 두기) + 종류 한 줄(이름 · 건수 · 최근 · 시각)"""
    groups = []
    for lv, (ln, ld) in AL_LV.items():
        its = [a for a in AL if a[0] == lv]
        rows = "".join(
            f'<li><button type="button" class="rd-ak" popovertarget="rd-al-{k}"><span class="rd-ak__n">{h(n)}</span>'
            f'<em class="rd-ak__c">{len(lst)}</em><span class="rd-ak__s"><span>{h(lst[0][0])}</span><span>{h(lst[0][2])}</span></span></button></li>'
            for _l, k, n, _s, lst in its)
        total = sum(len(a[4]) for a in its)
        groups.append(f'<div class="rd-alg rd-alg--{lv}"><p class="rd-alg__h"><b>{ln}</b><span>{ld}</span><em>{total}</em></p><ul>{rows}</ul></div>')
    alln = sum(len(a[4]) for a in AL)
    return (f'<aside class="rd-alcol" aria-label="받은 알림"><div class="rd-alcol__h"><h2>받은 알림</h2><b>{alln}</b>'
            f'<button type="button" class="rd-alcol__all" popovertarget="rd-al-all">전체 보기</button></div>{"".join(groups)}</aside>')


def al_drawers():
    """종류마다 오른쪽 패널 하나 + 전체 — 줄 = 제목 · 설명 · 시각, 아래 [화면 열기](실서버 화면 안내)"""
    def one(key, title, scr, items):
        rows = "".join(f'<li><div><b>{h(t)}</b><span>{h(d)}</span></div><small>{h(w)}</small></li>' for t, d, w in items)
        go = (f'<button type="button" class="rd-btn rd-btn--pri" popovertarget="rd-stub-{scr}">{h(STUB.get(scr, title))} 화면 열기</button>'
              if scr else '<button type="button" class="rd-btn" popovertarget="rd-stub-messageList">알림내역 화면 열기</button>')
        return (f'<aside class="rd-dr" id="rd-al-{key}" popover aria-label="{h(title)}"><header><div><b>{h(title)} {len(items)}건</b>'
                f'<p>받은 알림 — {"이 종류만" if key != "all" else "모든 종류"}</p></div>'
                f'<button type="button" class="rd-x" popovertarget="rd-al-{key}" popovertargetaction="hide" aria-label="닫기">✕</button></header>'
                f'<ul class="rd-dr__l">{rows}</ul><footer>{go}</footer></aside>')
    out = [one(k, n, scr, lst) for _l, k, n, scr, lst in AL]
    out.append(one("all", "받은 알림 전체", None, [(f"{n} · {t}", d, w) for _l, _k, n, _s, lst in AL for t, d, w in lst]))
    return "".join(out)


def todo_tbl():
    """[2026-11-24 v2] 지금 할 일 = 표: 기한 · 할 일 · 캠페인(설명) · 버튼"""
    def key(t):
        return (0, (t[0] - TODAY).days) if t[0] is not None else (1, 99)
    # [2026-11-24] 사용자: "지금할일과 이번 주 일정을 1row로" — 폭이 줄어 '할 일' 칸을 캠페인 칸 위 작은 글자로 합침(3칸)
    trs = "".join(
        f'<tr class="is-{urg(d) if d is not None else "later"}"><td class="rd-t-dd">{dday(d) if d is not None else "준비"}</td>'
        f'<td><span class="rd-t-k">{h(kind)}</span><b>{h(name)}</b><small>{h(desc)}</small></td>'
        f'<td class="rd-t-b"><button type="button" class="rd-btn rd-btn--pri" popovertarget="rd-act-{pop}">{h(btn)}</button></td></tr>'
        for d, kind, name, desc, btn, pop in sorted(TODO, key=key))
    return (f'<section class="rd-tc" aria-labelledby="rd-todo-h"><div class="rd-tc__h"><h2 id="rd-todo-h">지금 할 일 <em>{len(TODO)}</em></h2>'
            f'<ul class="rd-legend"><li class="is-hot">오늘·지남</li><li class="is-soon">3일 안</li><li class="is-later">그 외</li></ul></div>'
            f'<div class="rd-tw"><table class="rd-tbl rd-tbl--todo"><thead><tr><th scope="col">기한</th>'
            f'<th scope="col">할 일 · 캠페인</th><th scope="col"></th></tr></thead><tbody>{trs}</tbody></table></div></section>')


def flow_tbl():
    """진행 현황 = 머리 줄(단계) + 숫자 줄 + 신호 줄 — 칸을 누르면 그 단계 화면
    [2026-11-24] 사용자: "현황서머리 최상단으로, 현황서머리에 포인트를 추가" — 맨 위 + 마지막 칸 = 포인트(현재 · 지급 예정)
                 따로 있던 '내 포인트' 표는 이 칸으로 흡수(출금계좌 등록은 지금 할 일에 있다)"""
    th = "".join(f'<th scope="col">{n}</th>' for n, *_ in FLOW) + '<th scope="col" class="rd-fl-pt">포인트</th>'
    tn = ("".join(f'<td><button type="button" class="rd-fl" popovertarget="rd-stub-{scr}">{c}</button></td>' for _n, c, _s, _w, scr in FLOW)
          + f'<td class="rd-fl-pt"><button type="button" class="rd-fl" popovertarget="rd-stub-point">{POINT["now"]:,}<small>P</small></button></td>')
    ready = all(ok for _t, ok in CHECKS)
    ts = ("".join(f'<td class="{"is-warn" if w else ""}">{h(sg)}</td>' for _n, _c, sg, w, _scr in FLOW)
          + f'<td class="rd-fl-pt"><b class="rd-ok">+{POINT["due"]:,}P 예정</b>'
          + ("" if ready else '<br><button type="button" class="rd-link rd-link--warn" popovertarget="rd-act-bank">출금계좌 미등록 ›</button>') + '</td>')
    return (f'<section class="rd-tc" aria-labelledby="rd-fl-h"><div class="rd-tc__h"><h2 id="rd-fl-h">진행 현황</h2>'
            f'<button type="button" class="rd-link" popovertarget="rd-stub-campaignApplying">나의 캠페인 ›</button></div>'
            f'<div class="rd-tw"><table class="rd-tbl rd-tbl--flow"><thead><tr>{th}</tr></thead>'
            f'<tbody><tr class="rd-fl-n">{tn}</tr><tr class="rd-fl-s">{ts}</tr></tbody></table></div></section>')


def week_tbl():
    """이번 주 일정 = 날짜 · 일정 표"""
    by = {}
    for d, c, issue, name in SCHED:
        by.setdefault(d, []).append((c, issue, name))
    trs = []
    for i in range(7):
        d = D(i)
        its = by.get(d, [])
        lab = "오늘" if i == 0 else ("내일" if i == 1 else WEEK[d.weekday()])
        body = ("".join(f'<p class="mcal-c--{c}"><i></i><b>{h(iss)}</b> <span>{h(nm)}</span></p>' for c, iss, nm in its)
                if its else '<p class="rd-none">일정 없음</p>')
        trs.append(f'<tr{" class=\"is-today\"" if i == 0 else ""}><th scope="row">{md(d)} <small>{lab}</small></th><td>{body}</td></tr>')
    return (f'<section class="rd-tc" aria-labelledby="rd-wk-h"><div class="rd-tc__h"><h2 id="rd-wk-h">이번 주 일정</h2>'
            f'<button type="button" class="rd-link" popovertarget="rd-stub-schedule">나의 일정 ›</button></div>'
            f'<table class="rd-tbl rd-tbl--wk"><tbody>{"".join(trs)}</tbody></table></section>')


def point_tbl():
    """내 포인트 = 키-값 표 + 버튼"""
    chk = " · ".join(f'<span class="{"is-ok" if ok else "is-no"}">{"✓" if ok else "✕"} {h(t)}</span>' for t, ok in CHECKS)
    ready = all(ok for _t, ok in CHECKS)
    btn = ('<button type="button" class="rd-btn rd-btn--pri" popovertarget="rd-act-withdraw">출금 신청</button>' if ready
           else '<button type="button" class="rd-btn rd-btn--pri" popovertarget="rd-act-bank">출금계좌 등록</button>')
    d, amt, st = POINT["last"]
    rows = [("현재 포인트", f'<b class="rd-big">{POINT["now"]:,}</b> P'),
            ("지급 예정", f'<b class="rd-ok">+{POINT["due"]:,}P</b> <small>검수 승인 {POINT["due_n"]}건</small>'),
            ("출금 조건", chk),
            ("최근 출금", f'{d} · {amt:,}P · <span class="rd-ok">{st}</span>')]
    trs = "".join(f'<tr><th scope="row">{a}</th><td>{b}</td></tr>' for a, b in rows)
    return (f'<section class="rd-tc" aria-labelledby="rd-pt-h"><div class="rd-tc__h"><h2 id="rd-pt-h">내 포인트</h2>'
            f'<button type="button" class="rd-link" popovertarget="rd-stub-point">포인트 내역 ›</button></div>'
            f'<table class="rd-tbl rd-tbl--kv"><tbody>{trs}</tbody></table><div class="rd-tc__f">{btn}</div></section>')


def minical():
    """실서버 miniCalendar.inc.html 과 같은 마크업(정적) — 2026년 11월"""
    first = dt.date(2026, 11, 1)
    start = first - dt.timedelta(days=(first.weekday() + 1) % 7)
    last = dt.date(2026, 11, 30)
    end = last + dt.timedelta(days=(5 - last.weekday()) % 7)
    by = {}
    for d, c, issue, name in SCHED:
        by.setdefault(d, []).append((c, issue, name))
    by.setdefault(D(-3), []).append(("green", "체험", "[성수] 브런치 카페 2인 체험"))
    by.setdefault(D(-9), []).append(("teal", "포인트 지급", "+30,000P"))
    wk = "".join(f'<span class="mcal__wk{" is-sun" if i == 0 else (" is-sat" if i == 6 else "")}">{n}</span>' for i, n in enumerate("일월화수목금토"))
    cells = []
    d = start
    while d <= end:
        w = (d.weekday() + 1) % 7
        cls = "mcal__day" + (" is-out" if d.month != 11 else "") + (" is-today" if d == TODAY else "") + (" is-sun" if w == 0 else "") + (" is-sat" if w == 6 else "")
        its = by.get(d, [])
        dots = ('<span class="mcal__dots">' + "".join(f'<i class="mcal-c--{c}"></i>' for c, _i, _n in its[:3]) + "</span>") if its else ""
        cards = "".join(f'<a class="mcal-card mcal-c--{c}" href="#"><span class="mcal-card__issue">{h(i)}</span><span class="mcal-card__name">{h(n)}</span></a>' for c, i, n in its)
        empty = '' if its else '<p class="mcal__empty">이날은 일정이 없어요.</p>'
        did = f"mcalD{d:%Y%m%d}"
        cells.append(f'<div class="mcal__cell"><input type="radio" name="mcalDay" id="{did}" class="mcal__pick"{" checked" if d == TODAY else ""}>'
                     f'<label for="{did}" class="{cls}">{d.day}{dots}</label><div class="mcal__list"><p class="mcal__list-date">{d.month:02d}.{d.day:02d} ({"일월화수목금토"[w]}) <em>{len(its)}건</em></p>{empty}{cards}</div></div>')
        d += dt.timedelta(days=1)
    return f'''<input type="checkbox" id="mcalOpen" class="mcal-toggle">
<label for="mcalOpen" class="mcal-fab">달력</label>
<label for="mcalOpen" class="mcal-dim" aria-hidden="true"></label>
<aside class="mcal" aria-label="나의 일정 달력"><div class="mcal__inner">
	<div class="mcal__head"><a href="#" class="mcal__nav mcal__nav--prev" aria-label="이전 달"></a><strong class="mcal__ym">2026.11</strong><a href="#" class="mcal__nav mcal__nav--next" aria-label="다음 달"></a><label for="mcalOpen" class="mcal__close">닫기</label></div>
	<div class="mcal__grid">{wk}{"".join(cells)}</div>
	<a href="#" class="mcal__more">나의 일정 크게 보기 · 개인 일정 등록</a>
</div></aside>'''


def footer():
    return '''<footer class="site-footer"><div class="footer-inner">
	<nav class="footer-links"><a href="#">이용약관</a><span class="footer-link-sep"></span><a href="#">개인정보처리방침</a><span class="footer-link-sep"></span><a href="#">공지사항</a></nav>
	<div class="footer-info">
		<div class="footer-info-row"><span class="footer-info-text">기업명 : 애니라이즈 주식회사</span></div>
		<div class="footer-info-row"><span class="footer-info-text">고객센터 : 1833-3675(평일 09:30-17:30, 점심 12시-13시 제외)</span></div>
	</div>
	<div class="footer-copyright"><div class="footer-logo"><img src="img/logo1.png" alt="ANYRIZE" style="height:24px"></div><p class="footer-copyright-text">Copyright ⓒ ANYRIZE All Rights Reserved.</p></div>
</div></footer>'''


def page():
    css = ["variables.css", "reset.css", "common.css", "components.css", "my-campaign.css", "my-minical.css", "rd.css"]
    links = "\n".join(f'<link rel="stylesheet" href="css/{c}?v={ver(c)}">' for c in css)
    return f'''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>대시보드 · MY디마 · 뷰마 리뷰어 (데모)</title>
{links}
<link rel="stylesheet" href="css/rd-line.css?v={ver("rd-line.css")}">
</head>
<body>
<!-- [2026-11-23] 뷰마 리뷰어 대시보드 데모 — build/gen_reviewer.py 로 생성(직접 수정 금지)
     틀(헤더 · MY디마 사이드바 · 미니 달력)과 CSS 는 실서버 리뷰어 사이트 그대로. 대시보드 본문만 새로(rd-) -->
<div class="page-wrapper">
{header()}
<div class="page-main"><div class="mc-panel">
	<div class="mc-breadcrumb-wrap"><nav class="mc-breadcrumb"><a href="#">홈</a><span class="mc-breadcrumb__sep">›</span><a href="#">MY디마</a><span class="mc-breadcrumb__sep">›</span><span>대시보드</span></nav></div>
	<div class="mc-layout">
{sidebar()}
<!-- [2026-11-24] 사용자: "리뷰어사이트 대시보드에서는 우측달력 필요없을듯" — 대시보드에선 미니 달력 뺌(이번 주 일정이 대신) -->
<main class="mc-content rd">
	<div class="rd-head"><h1 class="mc-content__title"><em>{NICK}님의</em> 대시보드</h1><p class="rd-date">{TODAY.month}월 {TODAY.day}일 ({WEEK[TODAY.weekday()]}) 기준 · 데모 데이터</p></div>
	<!-- [2026-11-24 v2] 상단 써머리(숫자 4칸) · 패널티 띠 제거 → 2열: 받은 알림 | 표. v1 의 alert · kpi · todo · point · flow · week · news 는 쓰지 않는다 -->
	<div class="rd-lay">{alcol()}<div class="rd-main">{flow_tbl()}<div class="rd-two">{todo_tbl()}{week_tbl()}</div></div></div>
	<p class="rd-foot">데모 v2 — 버튼과 메뉴는 실서버의 어느 화면·창으로 이어지는지만 안내합니다. <a href="../versions/reviewer-v1/index.html">이전 버전 v1</a> · <a href="../index.html">데모 모음</a></p>
</main>
	</div>
</div></div>
{footer()}
</div>
{stubs()}
{al_drawers()}
</body>
</html>
'''


if __name__ == "__main__":
    (OUT / "index.html").write_text(page(), encoding="utf-8")
    print("written reviewer/index.html")
