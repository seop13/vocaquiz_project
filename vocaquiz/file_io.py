"""단어장 파일을 읽고 쓰는 모듈.

단어장은 카테고리(과일, 동물 …)마다 파일 하나로 저장한다.
    data/wordbooks/과일.txt
    data/wordbooks/동물.txt

파일 안에는 한 줄에 "영어,뜻" 형식으로 적는다.
    apple,사과
    banana,바나나

프로그램 안에서는 단어장 하나를 딕셔너리로 다룬다.
    {'apple': '사과', 'banana': '바나나'}
"""

import os

# 이 파일(file_io.py)이 어디에 있든 항상 data 폴더를 찾을 수 있도록
# 프로젝트 폴더(vocaquiz_project)의 위치를 계산해 둔다.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
WORDBOOK_DIR = os.path.join(DATA_DIR, 'wordbooks')    # 단어장 폴더
OLD_WORDS_PATH = os.path.join(DATA_DIR, 'words.txt')  # 예전 단일 단어장
WRONG_PATH = os.path.join(DATA_DIR, 'wrong.txt')      # 오답노트
RECORD_PATH = os.path.join(DATA_DIR, 'records.txt')   # 학습 기록

DEFAULT_CATEGORY = '기본'


# ---------- 단어 파일 하나 읽기/쓰기 ----------

def load_words(path, notify=True):
    """단어 파일을 읽어 딕셔너리로 돌려준다.

    파일이 없으면 빈 딕셔너리를 돌려주고(notify=False면 알림 없이),
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
        if notify:
            print(f'[알림] 파일이 없어 새로 시작합니다: {path}')
    return words


def save_words(words, path):
    """딕셔너리의 단어들을 파일에 저장한다. (기존 내용은 덮어쓴다)"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        for eng, kor in words.items():
            f.write(f'{eng},{kor}\n')


# ---------- 카테고리(단어장) 관리 ----------

def category_path(name):
    """카테고리 이름으로 단어장 파일 경로를 만든다."""
    return os.path.join(WORDBOOK_DIR, f'{name}.txt')


def prepare_wordbooks():
    """단어장 폴더를 준비한다.

    - 예전 data/words.txt가 있으면 '기본' 단어장으로 옮긴다. (한 번만)
    - 단어장이 하나도 없으면 빈 '기본' 단어장을 만든다.
    """
    os.makedirs(WORDBOOK_DIR, exist_ok=True)
    default_path = category_path(DEFAULT_CATEGORY)
    if os.path.exists(OLD_WORDS_PATH) and not os.path.exists(default_path):
        os.replace(OLD_WORDS_PATH, default_path)
    if not list_categories():
        save_words({}, default_path)


def list_categories():
    """단어장 이름 목록을 가나다순으로 돌려준다."""
    if not os.path.isdir(WORDBOOK_DIR):
        return []
    names = [os.path.splitext(file)[0] for file in os.listdir(WORDBOOK_DIR)
             if file.endswith('.txt')]
    return sorted(names)


def load_category(name):
    """카테고리 하나의 단어를 딕셔너리로 돌려준다."""
    return load_words(category_path(name), notify=False)


def save_category(name, words):
    """카테고리 하나의 단어를 파일에 저장한다."""
    save_words(words, category_path(name))


def load_all_categories():
    """모든 단어장의 단어를 하나의 딕셔너리로 합쳐 돌려준다. (전체 퀴즈용)"""
    all_words = {}
    for name in list_categories():
        all_words.update(load_category(name))
    return all_words


def create_category(name):
    """빈 단어장을 새로 만든다. 이미 있으면 False를 돌려준다."""
    if name in list_categories():
        return False
    save_category(name, {})
    return True


def delete_category(name):
    """단어장 파일을 삭제한다. 없으면 False를 돌려준다."""
    try:
        os.remove(category_path(name))
    except FileNotFoundError:
        return False
    return True


# ---------- 학습 기록 ----------

def append_record(date, mode, correct, total, path=RECORD_PATH):
    """퀴즈 결과 한 줄을 학습 기록 파일 끝에 추가한다. ('a' 모드)"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'a', encoding='utf-8') as f:
        f.write(f'{date},{mode},{correct},{total}\n')


def load_records(path=RECORD_PATH):
    """학습 기록을 [(날짜, 종류, 맞은 수, 전체 수), ...]로 돌려준다."""
    records = []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split(',')
                if len(parts) != 4:
                    continue
                try:
                    date, mode = parts[0], parts[1]
                    correct, total = int(parts[2]), int(parts[3])
                except ValueError:
                    continue
                records.append((date, mode, correct, total))
    except FileNotFoundError:
        pass  # 아직 기록이 없으면 빈 리스트
    return records


if __name__ == '__main__':
    # 이 파일을 직접 실행했을 때만 동작하는 테스트 코드
    prepare_wordbooks()
    print('단어장 목록:', list_categories())
    for category in list_categories():
        print(f'  {category}: {len(load_category(category))}개')
    print('전체 단어 수:', len(load_all_categories()))