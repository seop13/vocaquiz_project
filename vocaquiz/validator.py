"""정규표현식으로 사용자 입력을 검사하는 모듈.

단어를 추가하거나 문제 수를 입력받기 전에 형식이 맞는지 확인한다.
"""

import re

# 영어 단어: 알파벳으로 시작·끝, 중간에 공백 또는 하이픈 하나 허용
#   OK  : apple, neural network, check-in
#   NO  : 123, apple!, -apple, apple  (공백 두 개)
ENG_PATTERN = re.compile(r'^[a-zA-Z]+([ -][a-zA-Z]+)*$')

# 뜻: 한글·영어·숫자·공백·쉼표·괄호·가운뎃점·물결·하이픈만 허용
MEANING_PATTERN = re.compile(r'^[가-힣a-zA-Z0-9 ,()·~\-]+$')

# 뜻에 한글이 최소 한 글자는 있어야 한다
HANGUL_PATTERN = re.compile(r'[가-힣]')

# 문제 수: 1 ~ 99 (0으로 시작하면 안 됨)
COUNT_PATTERN = re.compile(r'^[1-9][0-9]?$')


def is_valid_english(eng):
    """영어 단어 형식이 맞으면 True를 돌려준다."""
    return ENG_PATTERN.match(eng.strip()) is not None


def is_valid_meaning(kor):
    """뜻 형식이 맞고 한글이 들어 있으면 True를 돌려준다."""
    kor = kor.strip()
    if MEANING_PATTERN.match(kor) is None:
        return False
    return HANGUL_PATTERN.search(kor) is not None


def is_valid_count(text):
    """문제 수 입력이 1~99 사이 숫자면 True를 돌려준다."""
    return COUNT_PATTERN.match(text.strip()) is not None


def check_word_input(eng, kor):
    """단어 추가 입력을 검사해 (통과 여부, 안내 메시지)를 돌려준다.

    GUI나 콘솔에서 메시지를 그대로 보여주기 위해 사용한다.
    """
    if not eng.strip() or not kor.strip():
        return False, '영어 단어와 뜻을 모두 입력하세요.'
    if not is_valid_english(eng):
        return False, '영어 단어는 알파벳으로만 입력하세요. (예: apple)'
    if not is_valid_meaning(kor):
        return False, '뜻은 한글로 입력하세요. (예: 사과, 사과나무)'
    return True, '올바른 입력입니다.'


if __name__ == '__main__':
    # 이 파일을 직접 실행했을 때만 동작하는 테스트 코드
    print('--- 영어 단어 ---')
    for word in ['apple', 'neural network', 'check-in', '123', 'apple!', '']:
        print(f'{word!r:18} {is_valid_english(word)}')

    print('--- 뜻 ---')
    for meaning in ['사과', '사과, 사과나무', '신경망(AI)', 'apple', '사과!']:
        print(f'{meaning!r:18} {is_valid_meaning(meaning)}')

    print('--- 문제 수 ---')
    for count in ['10', '5', '0', '100', 'ten', '07']:
        print(f'{count!r:18} {is_valid_count(count)}')

    print('--- 단어 추가 검사 ---')
    print(check_word_input('apple', '사과'))
    print(check_word_input('사과', 'apple'))
    print(check_word_input('apple', ''))