from flask import Flask, request, jsonify
import os

app = Flask(__name__)

policies = [
    {
        "name": "대전 청년 월세 지원",
        "description": "월 최대 20만원 월세 지원",
        "target_age": [19, 39],
        "target_status": ["재학생", "취업준비생"],
        "target_living": ["자취중"],
        "target_income": ["100만원 미만", "100~200만원", "200~300만원"],
        "url": "https://www.daejeonyouthportal.kr"
    },
    {
        "name": "청년 주택임차보증금 이자 지원",
        "description": "연 2% 이자 지원",
        "target_age": [19, 39],
        "target_status": ["재학생", "취업준비생", "재직중"],
        "target_living": ["자취중"],
        "target_income": ["100만원 미만", "100~200만원", "200~300만원"],
        "url": "https://www.daejeonyouthportal.kr"
    },
    {
        "name": "대전 청년 취업 컨설팅",
        "description": "1:1 맞춤 취업 상담 무료 제공",
        "target_age": [18, 34],
        "target_status": ["취업준비생"],
        "target_living": ["자취중", "가족과 거주"],
        "target_income": ["100만원 미만", "100~200만원", "200~300만원", "300만원 이상"],
        "url": "https://www.djbea.or.kr"
    },
    {
        "name": "청년 도전 지원사업",
        "description": "구직단념청년 대상 맞춤형 프로그램",
        "target_age": [18, 34],
        "target_status": ["취업준비생"],
        "target_living": ["자취중", "가족과 거주"],
        "target_income": ["100만원 미만", "100~200만원"],
        "url": "https://www.djbea.or.kr"
    },
    {
        "name": "대전 청년 인턴 사업",
        "description": "지역기업 인턴 연계 및 수당 지원",
        "target_age": [18, 34],
        "target_status": ["취업준비생", "재학생"],
        "target_living": ["자취중", "가족과 거주"],
        "target_income": ["100만원 미만", "100~200만원", "200~300만원"],
        "url": "https://www.daejeonyouthportal.kr"
    },
    {
        "name": "대전 청년수당 (청년내일희망카드)",
        "description": "미취업 청년 월 50만원 최대 6개월 지원",
        "target_age": [18, 34],
        "target_status": ["취업준비생"],
        "target_living": ["자취중", "가족과 거주"],
        "target_income": ["100만원 미만", "100~200만원", "200~300만원"],
        "target_marriage": ["미혼", "기혼"],
        "url": "https://www.daejeonyouthportal.kr"
    }
]

user_sessions = {}

def parse_age(age_str):
    if "18~24" in age_str:
        return 21
    elif "25~29" in age_str:
        return 27
    elif "30~34" in age_str:
        return 32
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
    if any(x in utterance for x in ["18~24", "25~29", "30~34"]):
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
            marriage_ok = 'target_marriage' not in p or marriage in p['target_marriage']

            if age_ok and status_ok and living_ok and income_ok and marriage_ok:
                matched.append(p)

        if matched:
            result = "✅ 해당되는 정책 목록입니다:\n\n"
            for i, p in enumerate(matched, 1):
                result += f"{i}. {p['name']}\n"
                result += f"   {p['description']}\n\n"
            result += "자세한 내용은 대전청년포털에서 확인하세요!"
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
            "outputs": [{"simpleText": {"text": "조건을 선택해주세요."}}]
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)