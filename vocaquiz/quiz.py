"""퀴즈 출제·채점·오답 추출 모듈.

사용 순서
    1. make_quiz()    : 단어장에서 문제를 랜덤으로 뽑는다
    2. check_answer() : 문제 하나의 정답 여부를 확인한다
    3. make_result()  : 문제·정답·내 답·정답 여부를 결과 하나로 묶는다
    4. get_score() / get_wrong_words() : 점수 계산, 오답만 골라내기
"""

import random

EN_TO_KO = 'en2ko'  # 영어를 보고 뜻 맞히기
KO_TO_EN = 'ko2en'  # 뜻을 보고 영어 맞히기


def make_quiz(words, n=10, mode=EN_TO_KO):
    """단어장에서 문제를 n개 랜덤으로 뽑아 [(영어, 뜻), ...]로 돌려준다.

    단어 수가 n보다 적으면 있는 단어를 모두 출제한다.
    단어장이 비어 있으면 ValueError를 일으킨다.
    """
    if not words:
        raise ValueError('단어장에 단어가 없습니다.')
    if mode not in (EN_TO_KO, KO_TO_EN):
        raise ValueError(f'알 수 없는 모드입니다: {mode}')

    count = min(n, len(words))
    return random.sample(list(words.items()), count)


def get_question(item, mode=EN_TO_KO):
    """(영어, 뜻) 한 쌍에서 화면에 보여줄 문제를 돌려준다."""
    eng, kor = item
    return eng if mode == EN_TO_KO else kor


def check_answer(item, user_answer, mode=EN_TO_KO):
    """사용자의 답이 맞으면 True, 틀리면 False를 돌려준다.

    - 앞뒤 공백과 영어 대소문자는 무시한다.
    - 뜻이 '사과, 사과나무'처럼 여러 개면 그중 하나만 맞아도 정답이다.
    """
    eng, kor = item
    answer = kor if mode == EN_TO_KO else eng
    user_answer = user_answer.strip().lower()
    if not user_answer:
        return False

    corrects = [a.strip().lower() for a in answer.split(',')]
    return user_answer in corrects


def make_result(item, user_answer, mode=EN_TO_KO):
    """문제 하나의 결과를 딕셔너리로 묶어 돌려준다."""
    eng, kor = item
    return {
        'eng': eng,
        'kor': kor,
        'user': user_answer.strip(),
        'correct': check_answer(item, user_answer, mode),
    }


def get_score(results):
    """(맞은 개수, 전체 개수)를 돌려준다."""
    correct = len(list(filter(lambda r: r['correct'], results)))
    return correct, len(results)


def get_wrong_words(results):
    """틀린 문제만 골라 {영어: 뜻} 딕셔너리로 돌려준다. (오답노트용)"""
    wrong = filter(lambda r: not r['correct'], results)
    return {r['eng']: r['kor'] for r in wrong}


if __name__ == '__main__':
    # 이 파일을 직접 실행했을 때만 동작하는 테스트 코드
    test_words = {'apple': '사과, 사과나무', 'book': '책', 'cat': '고양이'}

    # 1) 자동 테스트: 정해진 답으로 채점이 맞는지 확인
    print(check_answer(('apple', '사과, 사과나무'), ' 사과나무 '))   # True
    print(check_answer(('apple', '사과'), 'Apple', KO_TO_EN))       # True
    print(check_answer(('book', '책'), ''))                          # False

    # 2) 직접 풀어보기 (콘솔 버전 미리보기)
    print('\n=== 영어 → 뜻 퀴즈 ===')
    results = []
    for i, item in enumerate(make_quiz(test_words, n=3), start=1):
        user = input(f'Q{i}. {get_question(item)} : ')
        result = make_result(item, user)
        results.append(result)
        print('  정답!' if result['correct'] else f'  오답 (정답: {item[1]})')

    correct, total = get_score(results)
    print(f'\n점수: {correct} / {total}')
    print('오답노트:', get_wrong_words(results))