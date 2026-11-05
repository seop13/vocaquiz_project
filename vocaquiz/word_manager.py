"""단어장 딕셔너리를 관리하는 모듈 (추가·삭제·검색).

모든 함수는 file_io.load_words()가 돌려준 딕셔너리를 그대로 받아서 쓴다.
    {'apple': '사과', 'epoch': '에포크'}
영어 단어는 앞뒤 공백을 없애고 소문자로 바꿔서 다룬다. (Apple == apple)
"""


def _clean(eng):
    """영어 단어의 앞뒤 공백을 없애고 소문자로 바꾼다."""
    return eng.strip().lower()


def add_word(words, eng, kor):
    """단어를 추가한다.

    새로 추가하면 True, 이미 있는 단어면 False를 돌려준다.
    """
    eng = _clean(eng)
    if eng in words:
        return False
    words[eng] = kor.strip()
    return True


def delete_word(words, eng):
    """단어를 삭제한다.

    삭제하면 True, 없는 단어면 False를 돌려준다.
    """
    eng = _clean(eng)
    if eng not in words:
        return False
    del words[eng]
    return True


def search_word(words, eng):
    """단어의 뜻을 돌려준다. 없는 단어면 None을 돌려준다."""
    return words.get(_clean(eng))


def get_sorted_words(words):
    """단어 목록을 알파벳순으로 정렬해 [(영어, 뜻), ...] 형태로 돌려준다."""
    return sorted(words.items(), key=lambda item: item[0])


if __name__ == '__main__':
    # 이 파일을 직접 실행했을 때만 동작하는 테스트 코드
    test = {'apple': '사과', 'book': '책'}

    print(add_word(test, 'cat', '고양이'))   # True
    print(add_word(test, 'Apple', '사과'))   # False (이미 있음, 대소문자 무시)
    print(search_word(test, 'cat'))          # 고양이
    print(search_word(test, 'dog'))          # None
    print(delete_word(test, 'book'))         # True
    print(delete_word(test, 'book'))         # False (이미 지움)
    print(get_sorted_words(test))  # [('apple', '사과'), ('cat', '고양이')]