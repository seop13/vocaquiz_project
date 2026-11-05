"""단어장 파일을 읽고 쓰는 모듈.

단어장은 딕셔너리로 다룬다.
    {'apple': '사과', 'epoch': '에포크'}

파일(words.txt)에는 한 줄에 "영어,뜻" 형식으로 저장한다.
    apple,사과
    epoch,에포크
"""

import os

# 이 파일(file_io.py)이 어디에 있든 항상 data 폴더를 찾을 수 있도록
# 프로젝트 폴더(vocaquiz_project)의 위치를 계산해 둔다.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
WORDS_PATH = os.path.join(DATA_DIR, 'words.txt')


def load_words(path=WORDS_PATH):
    """단어장 파일을 읽어 딕셔너리로 돌려준다.

    파일이 없으면 빈 딕셔너리를 돌려주고,
    형식이 잘못된 줄은 건너뛴다.
    """
    words = {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for line_no, line in enumerate(f, start=1):
                line = line.strip()
                if not line:  # 빈 줄은 건너뛴다
                    continue
                try:
                    eng, kor = line.split(',', 1)
                except ValueError:
                    print(f'[경고] {line_no}번째 줄 형식 오류: {line}')
                    continue
                words[eng.strip()] = kor.strip()
    except FileNotFoundError:
        print(f'[알림] 단어장 파일이 없어 새로 시작합니다: {path}')
    return words


def save_words(words, path=WORDS_PATH):
    """딕셔너리의 단어들을 파일에 저장한다. (기존 내용은 덮어쓴다)"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        for eng, kor in words.items():
            f.write(f'{eng},{kor}\n')


if __name__ == '__main__':
    # 이 파일을 직접 실행했을 때만 동작하는 테스트 코드
    test_words = load_words()
    print('불러온 단어 수:', len(test_words))
    print(test_words)

    test_words['banana'] = '바나나'
    save_words(test_words)
    print('저장 후 다시 불러오기:', load_words())

    del test_words['banana']
    save_words(test_words)  # 테스트로 넣은 단어는 다시 지운다