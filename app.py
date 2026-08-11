from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# ─────────────────────────────────────────────
# 정책 DB (2026년 대전청년포털 기준)
# category: 주거 / 취업 / 자산 / 복지
# ─────────────────────────────────────────────
policies = [
    # ── 주거 ──────────────────────────────────
    {
        "name": "대전 청년 월세 지원",
        "category": "주거",
        "description": "무주택 청년 가구 월세 최대 20만원, 최대 12개월 지원 (생애 1회)",
        "support_amount": "월 최대 20만원 × 최대 12개월",
        "target_age": [19, 39],
        "target_status": ["재학생", "취업준비생", "재직중"],
        "target_living": ["자취중"],
        "target_income": ["100만원 미만", "100~200만원", "200~300만원"],
        "note": "무주택 세대주 본인 명의 임대차 계약 필수. 2026년 8월 말 공고 예정.",
        "url": "https://djhousing.or.kr"
    },
    {
        "name": "청년 주택임차보증금 이자 지원",
        "category": "주거",
        "description": "전세·월세 보증금 대출 이자 연 2% 지원 (최대 1억 보증금, 월세 60만원 이하)",
        "support_amount": "연 2% 이자 지원",
        "target_age": [19, 39],
        "target_status": ["재학생", "취업준비생", "재직중"],
        "target_living": ["자취중"],
        "target_income": ["100만원 미만", "100~200만원", "200~300만원"],
        "note": "대전 주소지 또는 대전 소재 대학·직장 재직자 신청 가능.",
        "url": "https://djhousing.or.kr"
    },
    {
        "name": "청년 신혼부부 주택 전세자금 대출 이자 지원",
        "category": "주거",
        "description": "신혼부부 전세자금 대출 이자 지원",
        "support_amount": "이자 지원 (세부 공고 확인)",
        "target_age": [19, 39],
        "target_status": ["재직중", "취업준비생"],
        "target_living": ["자취중"],
        "target_income": ["100만원 미만", "100~200만원", "200~300만원", "300만원 이상"],
        "target_marriage": ["기혼"],
        "note": "신혼부부 대상. 대전청년포털에서 공고 확인 필요.",
        "url": "https://www.daejeonyouthportal.kr"
    },
    # ── 취업 ──────────────────────────────────
    {
        "name": "대전 청년 취업 컨설팅",
        "category": "취업",
        "description": "1:1 맞춤 취업 상담 무료 제공 (이력서·면접·직무 등)",
        "support_amount": "무료",
        "target_age": [18, 34],
        "target_status": ["취업준비생"],
        "target_living": ["자취중", "가족과 거주"],
        "target_income": ["100만원 미만", "100~200만원", "200~300만원", "300만원 이상"],
        "url": "https://www.djbea.or.kr"
    },
    {
        "name": "청년 도전 지원사업",
        "category": "취업",
        "description": "구직단념청년 대상 맞춤형 취업 지원 프로그램. 단기(50만원)·중기(최대 150만원)·장기(최대 250만원) 참여 수당 지급.",
        "support_amount": "단기 50만원 / 중기 최대 150만원 / 장기 최대 250만원",
        "target_age": [18, 34],
        "target_status": ["취업준비생"],
        "target_living": ["자취중", "가족과 거주"],
        "target_income": ["100만원 미만", "100~200만원"],
        "note": "최근 6개월 취업·훈련 이력 없는 구직단념청년 대상. 상시 모집.",
        "url": "https://www.djbea.or.kr"
    },
    {
        "name": "대전 청년 인턴 사업",
        "category": "취업",
        "description": "지역기업 인턴 연계 및 수당 지원",
        "support_amount": "인턴 수당 지원 (세부 공고 확인)",
        "target_age": [18, 34],
        "target_status": ["취업준비생", "재학생"],
        "target_living": ["자취중", "가족과 거주"],
        "target_income": ["100만원 미만", "100~200만원", "200~300만원"],
        "url": "https://www.daejeonyouthportal.kr"
    },
    {
        "name": "청년 행정체험연수",
        "category": "취업",
        "description": "대전시청·사업소 등에서 5주간 행정 실무 체험. 실지급액 약 157만원(만근 기준, 생활임금 시간당 12,043원 적용).",
        "support_amount": "약 1,575,380원 (5주 만근 기준)",
        "target_age": [18, 39],
        "target_status": ["재학생", "취업준비생"],
        "target_living": ["자취중", "가족과 거주"],
        "target_income": ["100만원 미만", "100~200만원", "200~300만원", "300만원 이상"],
        "note": "본인 또는 부모가 대전시 주민등록 필수. 연 1회 공고 (2026 하계: 7.1~7.27).",
        "url": "https://www.daejeonyouthportal.kr"
    },
    # ── 자산 ──────────────────────────────────
    {
        "name": "대전 미래두배 청년통장",
        "category": "자산",
        "description": "근로 청년이 월 10만원 또는 15만원씩 3년 적립하면 대전시가 동일 금액 매칭. 만기 시 최대 720만원+이자 수령.",
        "support_amount": "최대 720만원 + 이자 (3년 만기, 1:1 매칭)",
        "target_age": [18, 39],
        "target_status": ["재직중"],
        "target_living": ["자취중", "가족과 거주"],
        "target_income": ["100만원 미만", "100~200만원", "200~300만원"],
        "note": "중위소득 140% 이하 근로 청년. 3개월 이상 근무 필수. 유사 자산형성사업 중복 불가.",
        "url": "https://youthaccount.or.kr"
    },
    # ── 복지 ──────────────────────────────────
    {
        "name": "대전 청년수당 (청년내일희망카드)",
        "category": "복지",
        "description": "미취업 청년 월 50만원, 최대 6개월 지원 (총 최대 300만원)",
        "support_amount": "월 50만원 × 최대 6개월",
        "target_age": [18, 34],
        "target_status": ["취업준비생"],
        "target_living": ["자취중", "가족과 거주"],
        "target_income": ["100만원 미만", "100~200만원", "200~300만원"],
        "target_marriage": ["미혼", "기혼"],
        "url": "https://www.daejeonyouthportal.kr"
    },
    {
        "name": "2026 청년 맞춤형 재무 상담서비스",
        "category": "복지",
        "description": "청년 대상 무료 1:1 재무·금융 상담 서비스",
        "support_amount": "무료",
        "target_age": [19, 39],
        "target_status": ["재학생", "취업준비생", "재직중"],
        "target_living": ["자취중", "가족과 거주"],
        "target_income": ["100만원 미만", "100~200만원", "200~300만원", "300만원 이상"],
        "note": "2026년 7월 모집. 대전청년포털 공지 확인.",
        "url": "https://www.daejeonyouthportal.kr"
    },
    {
        "name": "대전시 인재육성 장학사업",
        "category": "복지",
        "description": "대전시 청년 대학생 대상 장학금 지원 및 국외 진로탐방 프로그램",
        "support_amount": "장학금 (금액 공고 확인)",
        "target_age": [18, 34],
        "target_status": ["재학생"],
        "target_living": ["자취중", "가족과 거주"],
        "target_income": ["100만원 미만", "100~200만원", "200~300만원"],
        "note": "대전청년포털 장학금 신청 메뉴에서 확인.",
        "url": "https://www.daejeonyouthportal.kr"
    },
]

user_sessions = {}

def parse_age(age_str):
    if "18~24" in age_str:
        return 21
    elif "25~29" in age_str:
        return 27
    elif "30~34" in age_str:
        return 32
    elif "35~39" in age_str:
        return 37
    return 0

@app.route('/policy', methods=['POST'])
def get_policy():
    data = request.get_json()
    utterance = data.get('userRequest', {}).get('utterance', '').strip()
    user_id = data.get('userRequest', {}).get('user', {}).get('id', 'default')

    if user_id not in user_sessions:
        user_sessions[user_id] = {}

    session = user_sessions[user_id]

    # 나이 저장
    if any(x in utterance for x in ["18~24", "25~29", "30~34", "35~39"]):
        session['age'] = utterance

    # 취업상태 저장
    if utterance in ["재학생", "취업준비생", "재직중"]:
        session['status'] = utterance

    # 거주지 저장
    if utterance in ["동구", "중구", "서구", "유성구", "대덕구"]:
        session['district'] = utterance

    # 자취 여부 저장
    if utterance in ["자취중", "가족과 거주"]:
        session['living'] = utterance

    # 월소득 저장
    if utterance in ["100만원 미만", "100~200만원", "200~300만원", "300만원 이상"]:
        session['income'] = utterance

    # 가구원 수 저장
    if utterance in ["1인", "2인", "3인 이상"]:
        session['household'] = utterance

    # 혼인 여부 저장 + 결과 반환
    if utterance in ["미혼", "기혼"]:
        session['marriage'] = utterance
        print(f"DEBUG session: {session}", flush=True)

        age = parse_age(session.get('age', ''))
        status = session.get('status', '')
        living = session.get('living', '')
        income = session.get('income', '')
        marriage = session.get('marriage', '')

        matched = []
        for p in policies:
            age_ok = p['target_age'][0] <= age <= p['target_age'][1]
            status_ok = status in p['target_status']
            living_ok = 'target_living' not in p or living in p['target_living']
            income_ok = 'target_income' not in p or income in p['target_income']
            marriage_ok = 'target_marriage' not in p or marriage in p.get('target_marriage', [marriage])

            if age_ok and status_ok and living_ok and income_ok and marriage_ok:
                matched.append(p)

        if matched:
            # 카테고리별 정렬
            category_order = {"주거": 0, "취업": 1, "자산": 2, "복지": 3}
            matched.sort(key=lambda x: category_order.get(x['category'], 9))

            result = f"✅ 총 {len(matched)}개 정책이 해당됩니다!\n\n"
            current_category = None
            for i, p in enumerate(matched, 1):
                if p['category'] != current_category:
                    current_category = p['category']
                    result += f"📌 [{current_category}]\n"
                result += f"{i}. {p['name']}\n"
                result += f"   💰 {p['support_amount']}\n"
                if p.get('note'):
                    result += f"   ℹ️ {p['note']}\n"
                result += f"   🔗 {p['url']}\n"
                result += "\n"
            result += "🔗 자세한 내용은 대전청년포털에서 확인하세요!\nhttps://www.daejeonyouthportal.kr"
        else:
            result = "현재 조건에 맞는 정책이 없습니다.\n대전청년포털에서 더 많은 정책을 확인해보세요!\nhttps://www.daejeonyouthportal.kr"

        user_sessions[user_id] = {}

        return jsonify({
            "version": "2.0",
            "template": {
                "outputs": [{"simpleText": {"text": result}}]
            }
        })

    return jsonify({
        "version": "2.0",
        "template": {
            "outputs": [{"simpleText": {"text": "조건을 선택해주세요."}
            }]
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)