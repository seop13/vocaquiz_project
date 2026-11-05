"""VocaQuiz 실행 파일.

    python main.py            → GUI 버전 (Tkinter, v2.0)
    python main.py --console  → 콘솔 버전 (v1.0)
"""

import sys
import time

from vocaquiz import file_io, quiz, validator, word_manager

MENU = """
========== VocaQuiz ==========
 1. 단어 목록 보기
 2. 단어 추가
 3. 단어 삭제
 4. 단어 검색
 5. 퀴즈 풀기
 6. 오답노트 다시 풀기
 7. 학습 기록 보기
 0. 종료
=============================="""

MODE_NAMES = {quiz.EN_TO_KO: '영어→뜻', quiz.KO_TO_EN: '뜻→영어'}


# ---------- 단어장 관리 ----------

def show_words(words):
    """단어 목록을 알파벳순으로 보여준다."""
    if not words:
        print('단어장이 비어 있습니다.')
        return
    print(f'\n[단어 {len(words)}개]')
    for i, (eng, kor) in enumerate(word_manager.get_sorted_words(words), 1):
        print(f'{i:3}. {eng} : {kor}')


def add_menu(words):
    """단어를 입력받아 검사한 뒤 추가하고 파일에 저장한다."""
    eng = input('영어 단어: ')
    kor = input('뜻 (여러 개면 쉼표로 구분): ')

    ok, message = validator.check_word_input(eng, kor)
    if not ok:
        print(message)
        return

    if word_manager.add_word(words, eng, kor):
        file_io.save_words(words)
        print(f"'{eng.strip()}' 단어를 추가했습니다.")
    else:
        print('이미 있는 단어입니다.')


def delete_menu(words):
    """단어를 입력받아 삭제하고 파일에 저장한다."""
    eng = input('삭제할 영어 단어: ')
    if word_manager.delete_word(words, eng):
        file_io.save_words(words)
        print(f"'{eng.strip()}' 단어를 삭제했습니다.")
    else:
        print('없는 단어입니다.')


def search_menu(words):
    """단어를 입력받아 뜻을 보여준다."""
    eng = input('검색할 영어 단어: ')
    meaning = word_manager.search_word(words, eng)
    if meaning is None:
        print('없는 단어입니다.')
    else:
        print(f'{eng.strip()} : {meaning}')


# ---------- 퀴즈 ----------

def choose_mode():
    """퀴즈 모드를 고른다."""
    choice = input('모드 선택 (1: 영어→뜻, 2: 뜻→영어) [기본 1]: ').strip()
    return quiz.KO_TO_EN if choice == '2' else quiz.EN_TO_KO


def choose_count(max_count):
    """문제 수를 입력받는다. 잘못 입력하면 10문제(또는 전체)로 한다."""
    text = input(f'문제 수 (1~99, 단어 {max_count}개) [기본 10]: ')
    if validator.is_valid_count(text):
        return int(text)
    if text.strip():
        print('1~99 사이 숫자가 아니라서 기본값으로 진행합니다.')
    return 10


def run_quiz(words, mode, n):
    """퀴즈를 진행하고 결과 리스트를 돌려준다."""
    try:
        items = quiz.make_quiz(words, n, mode)
    except ValueError as e:
        print(e)
        return []

    print(f'\n=== {MODE_NAMES[mode]} 퀴즈 ({len(items)}문제) ===')
    results = []
    for i, item in enumerate(items, 1):
        user = input(f'Q{i}. {quiz.get_question(item, mode)} : ')
        result = quiz.make_result(item, user, mode)
        results.append(result)

        if result['correct']:
            print('  ⭕ 정답!')
        else:
            answer = item[1] if mode == quiz.EN_TO_KO else item[0]
            print(f'  ❌ 오답 (정답: {answer})')
    return results


def finish_quiz(results, mode):
    """점수를 보여주고 학습 기록 파일에 저장한다."""
    correct, total = quiz.get_score(results)
    print(f'\n점수: {correct} / {total}')
    date = time.strftime('%Y-%m-%d %H:%M')
    file_io.append_record(date, MODE_NAMES[mode], correct, total)


def quiz_menu(words):
    """일반 퀴즈: 틀린 단어는 오답노트에 추가한다."""
    if not words:
        print('단어장에 단어를 먼저 추가하세요.')
        return
    mode = choose_mode()
    n = choose_count(len(words))
    results = run_quiz(words, mode, n)
    if not results:
        return

    finish_quiz(results, mode)
    new_wrong = quiz.get_wrong_words(results)
    if new_wrong:
        wrong = file_io.load_words(file_io.WRONG_PATH, notify=False)
        wrong.update(new_wrong)
        file_io.save_words(wrong, file_io.WRONG_PATH)
        print(f'틀린 단어 {len(new_wrong)}개를 오답노트에 저장했습니다.')


def wrong_menu():
    """오답노트 퀴즈: 맞힌 단어는 오답노트에서 지운다."""
    wrong = file_io.load_words(file_io.WRONG_PATH, notify=False)
    if not wrong:
        print('오답노트가 비어 있습니다. 👍')
        return
    print(f'오답노트 단어 {len(wrong)}개를 모두 출제합니다.')
    mode = choose_mode()
    results = run_quiz(wrong, mode, len(wrong))
    if not results:
        return

    finish_quiz(results, mode)
    file_io.save_words(quiz.get_wrong_words(results), file_io.WRONG_PATH)
    print(f'남은 오답: {len(quiz.get_wrong_words(results))}개')


def record_menu():
    """최근 학습 기록 10개를 보여준다."""
    records = file_io.load_records()
    if not records:
        print('아직 학습 기록이 없습니다.')
        return
    print('\n[최근 학습 기록]')
    for date, mode, correct, total in records[-10:]:
        rate = correct / total * 100 if total else 0
        print(f'{date}  {mode}  {correct}/{total}  ({rate:.0f}%)')


# ---------- 실행 ----------

def main():
    """메뉴를 반복해서 보여주고 선택한 기능을 실행한다."""
    words = file_io.load_words()
    print(f'단어 {len(words)}개를 불러왔습니다.')

    while True:
        print(MENU)
        choice = input('메뉴 선택: ').strip()

        if choice == '1':
            show_words(words)
        elif choice == '2':
            add_menu(words)
        elif choice == '3':
            delete_menu(words)
        elif choice == '4':
            search_menu(words)
        elif choice == '5':
            quiz_menu(words)
        elif choice == '6':
            wrong_menu()
        elif choice == '7':
            record_menu()
        elif choice == '0':
            print('프로그램을 종료합니다. 수고하셨습니다!')
            break
        else:
            print('0~7 사이 번호를 입력하세요.')


if __name__ == '__main__':
    if '--console' in sys.argv:
        try:
            main()
        except (KeyboardInterrupt, EOFError):
            print('\n프로그램을 종료합니다.')
    else:
        from vocaquiz import gui
        gui.run()