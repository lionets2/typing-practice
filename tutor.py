import json
import time
import sys
import os
import random
from difflib import SequenceMatcher
from datetime import datetime

DRILLS_FILE = 'drills.json'
HISTORY_FILE = 'history.json'

# ==========================================
# 1. Drill Bank (내장 문제 데이터)
# ==========================================
DRILL_BANK = {
    "basic_ko": [
        {"text": "안녕하세요 반갑습니.", "guide": "기본 인사말입니다."},
        {"text": "타이핑 연습을 시작합니다.", "guide": "어깨 힘을 빼세요."},
        {"text": "천천히 정확하게 치는 것이 중요합니다.", "guide": "속도보다는 정확도!"},
        {"text": "무한한 가능성을 믿으세요.", "guide": "긍정적인 마인드"},
        {"text": "오늘 점심은 무엇을 먹을까요?", "guide": "일상 대화 연습"},
        {"text": "가는 말이 고와야 오는 말이 곱습니다.", "guide": "속담 연습 1"},
        {"text": "티끌 모아 태산이 됩니다.", "guide": "속담 연습 2"},
        {"text": "늦었다고 생각할 때가 가장 빠릅니다.", "guide": "동기 부여"},
        {"text": "독수리 타법 탈출을 축하합니다.", "guide": "성장 마인드셋"},
        {"text": "개발자의 기본은 체력입니다.", "guide": "진리"}
    ],
    "basic_eng": [
        {"text": "hello world", "guide": "프로그래밍의 시작"},
        {"text": "typing is fun", "guide": "간단한 문장"},
        {"text": "good morning everyone", "guide": "아침 인사"},
        {"text": "stay hungry stay foolish", "guide": "스티브 잡스 명언"},
        {"text": "python is powerful", "guide": "파이썬 찬양"},
        {"text": "practice makes perfect", "guide": "연습이 완벽을 만듭니다"},
        {"text": "time is gold", "guide": "시간은 금이다"},
        {"text": "keep it simple stupid", "guide": "KISS 원칙"},
        {"text": "clean code is art", "guide": "클린 코드는 예술이다"},
        {"text": "just do it", "guide": "나이키 명언"}
    ],
    "shift_mix": [
        {"text": "Hello World", "guide": "대문자 H, W 주의"},
        {"text": "Docker & Kubernetes", "guide": "대문자와 기호"},
        {"text": "iPhone, iPad, MacBook", "guide": "애플 제품명 연습"},
        {"text": "The Quick Brown Fox", "guide": "전통적인 연습 문장"},
        {"text": "JavaScript and TypeScript", "guide": "카멜 케이스 연습"},
        {"text": "I love New York and Seoul.", "guide": "도시 이름 대문자"},
        {"text": "Elon Musk -> SpaceX & Tesla", "guide": "특수문자와 대문자 혼합"},
        {"text": "HTML, CSS, And JS!", "guide": "약어 대문자 연습"},
        {"text": "Daft Punk - Get Lucky", "guide": "노래 제목 연습"},
        {"text": "PyTorch vs TensorFlow", "guide": "딥러닝 프레임워크"}
    ],
    "symbol_code": [
        {"text": "print('Hello')", "guide": "함수 호출 괄호"},
        {"text": "if (score > 90) { return 'A'; }", "guide": "조건문과 블록"},
        {"text": "const arr = [1, 2, 3];", "guide": "대괄호와 세미콜론"},
        {"text": "def __init__(self):", "guide": "파이썬 언더스코어"},
        {"text": "<div class=\"container\">", "guide": "HTML 태그 연습"},
        {"text": "SELECT * FROM users WHERE id=1;", "guide": "SQL 쿼리 연습"},
        {"text": "git commit -m \"fix: bug\"", "guide": "Git 명령어 연습"},
        {"text": "for i in range(10): pass", "guide": "파이썬 반복문"},
        {"text": "npm install react-dom", "guide": "터미널 명령어"},
        {"text": "h1 { color: #ff0000; }", "guide": "CSS 문법 연습"}
    ],
    "long_sentence": [
        {"text": "성공이란 열정을 잃지 않고 실패에서 실패로 걸어가는 능력이다.", "guide": "윈스턴 처칠"},
        {"text": "The only way to do great work is to love what you do.", "guide": "스티브 잡스"},
        {"text": "삶이 있는 한 희망은 있다.", "guide": "키케로"},
        {"text": "In the middle of difficulty lies opportunity.", "guide": "알버트 아인슈타인"},
        {"text": "Pain is temporary. Quitting lasts forever.", "guide": "고통은 일시적이지만 포기는 영원하다"},
        {"text": "Talk is cheap. Show me the code.", "guide": "리누스 토발즈"},
        {"text": "우리가 헛되이 보낸 오늘은 어제 죽은 이가 그토록 멸망하던 내일이다.", "guide": "하루의 소중함"},
        {"text": "Life is what happens when you are busy making other plans.", "guide": "존 레논"}
    ]
}

# ==========================================
# 2. Smart Coach (분석 및 추천 로직)
# ==========================================
class SmartCoach:
    def __init__(self):
        self.history = self.load_history()

    def load_history(self):
        if not os.path.exists(HISTORY_FILE):
            return []
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []

    def analyze_weakness(self):
        """최근 기록을 분석하여 약점 카테고리와 조언 반환"""
        if not self.history:
            return "basic_ko", "기초부터 차근차근 시작해봅시다."

        recent = self.history[-10:] # 최근 10개만 분석
        
        # 1. 정확도 분석
        low_accuracy_drills = [h for h in recent if h['accuracy'] < 95]
        if len(low_accuracy_drills) > 3:
            # 오타가 많음 -> 정확도 위주 코칭
            return "basic_ko", "정확도가 다소 불안정합니다. 천천히 다시 기본기를 다져봅시다."

        # 2. Shift 키 / 특수문자 약점 확인
        shift_mistakes = 0
        code_mistakes = 0
        for h in recent:
            for mistake in h.get('mistakes', []):
                if any(c.isupper() for c in mistake): shift_mistakes += 1
                if any(not c.isalnum() and c != ' ' for c in mistake): code_mistakes += 1
        
        if shift_mistakes > 2:
            return "shift_mix", "Shift 키 입력(대문자)에서 실수가 감지되었습니다. 집중 훈련이 필요합니다."
        
        if code_mistakes > 2:
            return "symbol_code", "특수기호 입력이 아직 낯섭니다. 코드 연습을 통해 익숙해져 봅시다."

        # 3. 속도 분석 (WPM)
        avg_wpm = sum(h['wpm'] for h in recent) / len(recent)
        if avg_wpm > 40:
            return "long_sentence", f"평균 속도 {avg_wpm:.1f} WPM! 아주 훌륭합니다. 긴 문장으로 지구력을 길러봅시다."
        
        # 4. 기본 (순환)
        categories = list(DRILL_BANK.keys())
        next_cat = random.choice(categories)
        return next_cat, "다양한 문장을 고루 연습하며 감각을 유지합시다."

    def generate_curriculum(self):
        """약점 분석 기반으로 다음 연습 세트(5문제) 생성"""
        category, advice = self.analyze_weakness()
        
        # 메인 카테고리에서 3문제
        candidates = DRILL_BANK.get(category, DRILL_BANK['basic_ko'])
        selected = random.sample(candidates, k=min(3, len(candidates)))
        
        # 랜덤(환기용) 2문제
        other_cats = list(DRILL_BANK.keys())
        if category in other_cats: other_cats.remove(category)
        
        for _ in range(2):
            rnd_cat = random.choice(other_cats)
            rnd_drill = random.choice(DRILL_BANK[rnd_cat])
            selected.append(rnd_drill)
            
        random.shuffle(selected)
        
        # ID 부여 및 포맷팅
        curriculum = []
        for idx, item in enumerate(selected):
            curriculum.append({
                "id": f"auto_{int(time.time())}_{idx}",
                "category": category,
                "text": item['text'],
                "guide": item['guide']
            })
            
        # drills.json 업데이트
        with open(DRILLS_FILE, 'w', encoding='utf-8') as f:
            json.dump(curriculum, f, indent=2, ensure_ascii=False)
            
        return curriculum, advice

# ==========================================
# 3. Core Engine (실행 및 측정)
# ==========================================
def calculate_wpm(start_time, end_time, text_len):
    duration_min = (end_time - start_time) / 60
    if duration_min == 0: return 0
    return int((text_len / 5) / duration_min)

def highlight_diff(expected, actual):
    matcher = SequenceMatcher(None, expected, actual)
    result = []
    mistakes = []
    
    for opcode, a0, a1, b0, b1 in matcher.get_opcodes():
        if opcode == 'equal':
            result.append(expected[a0:a1])
        elif opcode == 'insert':
            mistakes.append(f"Inserted: '{actual[b0:b1]}'")
            result.append(f"\033[91m{actual[b0:b1]}(+)\033[0m") 
        elif opcode == 'delete':
            mistakes.append(f"Missed: '{expected[a0:a1]}'")
            result.append(f"\033[93m{expected[a0:a1]}(-)\033[0m")
        elif opcode == 'replace':
            mistakes.append(f"Typo: '{expected[a0:a1]}' -> '{actual[b0:b1]}'")
            result.append(f"\033[91m{actual[b0:b1]}\033[0m")
            
    return "".join(result), mistakes

def run_tutor():
    # ANSI Color Check for Windows
    os.system('color') 
    
    coach = SmartCoach()
    
    print("\n" + "="*60)
    print("   🤖 AI 터미널 타이핑 코치 (AI Terminal Typing Coach)")
    print("   사용자의 패턴을 분석하여 최적의 커리큘럼을 제공합니다.")
    print("   'Ctrl + C'를 눌러 언제든지 종료할 수 있습니다.")
    print("="*60 + "\n")

    round_count = 1
    
    while True:
        try:
            # 커리큘럼 생성 단계
            if round_count == 1:
                # 첫 실행 시에는 기존 drills.json이 있으면 쓰고, 없으면 코치가 생성
                if os.path.exists(DRILLS_FILE):
                    with open(DRILLS_FILE, 'r', encoding='utf-8') as f:
                        curriculum = json.load(f)
                    advice = "기존 커리큘럼으로 시작합니다."
                else:
                    curriculum, advice = coach.generate_curriculum()
            else:
                print(f"\n[분석 중...] 연습 결과를 분석하고 있습니다...")
                time.sleep(1) # 분석하는 척(UX)
                coach = SmartCoach() # Reload history
                curriculum, advice = coach.generate_curriculum()
                
            print(f"\n📢 [ROUND {round_count} 코치 조언]")
            print(f"👉 {advice}")
            print(f"총 {len(curriculum)}개의 훈련 문장이 준비되었습니다.\n")
            
            input("엔터(Enter)를 누르면 시작합니다...")
            
            # 연습 시작
            for idx, drill in enumerate(curriculum):
                print(f"\n[문제 {idx+1}/{len(curriculum)}] {drill.get('guide', '')}")
                print(f"따라 치세요:\n\033[1m{drill['text']}\033[0m")
                
                start_time = time.time()
                user_input = input("\n입력: ")
                end_time = time.time()
                
                # Analyze
                matcher = SequenceMatcher(None, drill['text'], user_input)
                accuracy = matcher.ratio() * 100
                wpm = calculate_wpm(start_time, end_time, len(user_input))
                diff_text, mistakes = highlight_diff(drill['text'], user_input)
                
                print("-" * 30)
                if accuracy == 100:
                    print(f"\033[92m완벽합니다! (Perfect) 🎉\033[0m")
                else:
                    print(f"결과: {diff_text}")
                    
                print(f"속도: {wpm} WPM | 정확도: {accuracy:.1f}%")
                
                # Log Save
                log_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "drill_id": drill['id'],
                    "category": drill['category'],
                    "expected": drill['text'],
                    "actual": user_input,
                    "wpm": wpm,
                    "accuracy": accuracy,
                    "mistakes": mistakes
                }
                
                # Append to history immediately
                history = coach.load_history()
                history.append(log_entry)
                with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
                    json.dump(history, f, ensure_ascii=False, indent=2)
                
            print(f"\n✅ ROUND {round_count} 연습 완료!")
            choice = input("계속해서 맞춤 훈련을 진행하시겠습니까? (Y/n): ")
            if choice.lower() == 'n':
                print("\n오늘도 수고하셨습니다! 👋")
                break
                
            round_count += 1
            
        except KeyboardInterrupt:
            print("\n\n연습을 종료합니다. 수고하셨습니다!")
            break

if __name__ == "__main__":
    run_tutor()
