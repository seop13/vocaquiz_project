"""VocaQuiz GUI 버전 (Tkinter).

탭 3개로 구성한다.
    [단어장]   단어 목록 보기, 추가·삭제·검색
    [퀴즈]     일반 퀴즈 / 오답노트 퀴즈
    [학습 기록] 날짜별 점수

실행은 프로젝트 폴더에서  python main.py
"""

import time
import tkinter as tk
from tkinter import messagebox, ttk

from vocaquiz import file_io, quiz, validator, word_manager

FONT = '맑은 고딕'
MODE_NAMES = {quiz.EN_TO_KO: '영어→뜻', quiz.KO_TO_EN: '뜻→영어'}


class VocaApp(tk.Tk):
    """VocaQuiz 메인 창."""

    def __init__(self):
        super().__init__()
        self.title('VocaQuiz - 영어 단어장 퀴즈')
        self.geometry('680x560')
        self.minsize(600, 500)
        self.option_add('*Font', (FONT, 11))

        self.words = file_io.load_words()

        # 퀴즈 진행 상태
        self.items = []          # 출제된 문제 [(영어, 뜻), ...]
        self.results = []        # 채점 결과
        self.index = 0           # 지금 몇 번째 문제인지
        self.mode = quiz.EN_TO_KO
        self.is_wrong_quiz = False

        notebook = ttk.Notebook(self)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)

        self.word_tab = ttk.Frame(notebook, padding=12)
        self.quiz_tab = ttk.Frame(notebook, padding=12)
        self.record_tab = ttk.Frame(notebook, padding=12)
        notebook.add(self.word_tab, text='  단어장  ')
        notebook.add(self.quiz_tab, text='  퀴즈  ')
        notebook.add(self.record_tab, text='  학습 기록  ')

        self._build_word_tab()
        self._build_quiz_tab()
        self._build_record_tab()

        self.refresh_word_list()
        self.refresh_records()

    # ================= 단어장 탭 =================

    def _build_word_tab(self):
        """단어 목록(표)과 입력칸, 버튼을 만든다."""
        tab = self.word_tab

        self.count_label = ttk.Label(tab, text='')
        self.count_label.pack(anchor='w')

        table_frame = ttk.Frame(tab)
        table_frame.pack(fill='both', expand=True, pady=(4, 10))
        self.tree = ttk.Treeview(table_frame, columns=('eng', 'kor'),
                                 show='headings', height=12)
        self.tree.heading('eng', text='영어')
        self.tree.heading('kor', text='뜻')
        self.tree.column('eng', width=220)
        self.tree.column('kor', width=360)
        scroll = ttk.Scrollbar(table_frame, orient='vertical',
                               command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side='left', fill='both', expand=True)
        scroll.pack(side='right', fill='y')
        self.tree.bind('<<TreeviewSelect>>', self.on_select_word)

        form = ttk.Frame(tab)
        form.pack(fill='x')
        ttk.Label(form, text='영어').grid(row=0, column=0, sticky='w')
        ttk.Label(form, text='뜻 (여러 개면 쉼표)').grid(
            row=0, column=1, sticky='w', padx=(10, 0))
        self.eng_entry = ttk.Entry(form, width=22)
        self.kor_entry = ttk.Entry(form, width=32)
        self.eng_entry.grid(row=1, column=0, sticky='we')
        self.kor_entry.grid(row=1, column=1, sticky='we', padx=(10, 0))
        form.columnconfigure(1, weight=1)

        buttons = ttk.Frame(tab)
        buttons.pack(fill='x', pady=(10, 0))
        ttk.Button(buttons, text='추가', command=self.add_word).pack(
            side='left')
        ttk.Button(buttons, text='삭제', command=self.delete_word).pack(
            side='left', padx=6)
        ttk.Button(buttons, text='검색', command=self.search_word).pack(
            side='left')
        ttk.Button(buttons, text='입력칸 비우기',
                   command=self.clear_entries).pack(side='right')

    def refresh_word_list(self):
        """표의 내용을 현재 단어장으로 다시 채운다."""
        self.tree.delete(*self.tree.get_children())
        for eng, kor in word_manager.get_sorted_words(self.words):
            self.tree.insert('', 'end', iid=eng, values=(eng, kor))
        self.count_label.config(text=f'단어 {len(self.words)}개')

    def on_select_word(self, event=None):
        """표에서 단어를 클릭하면 입력칸에 채워 준다."""
        selected = self.tree.selection()
        if not selected:
            return
        eng, kor = self.tree.item(selected[0], 'values')
        self.clear_entries()
        self.eng_entry.insert(0, eng)
        self.kor_entry.insert(0, kor)

    def clear_entries(self):
        """영어·뜻 입력칸을 비운다."""
        self.eng_entry.delete(0, 'end')
        self.kor_entry.delete(0, 'end')

    def add_word(self):
        """입력칸의 단어를 검사한 뒤 추가하고 저장한다."""
        eng = self.eng_entry.get()
        kor = self.kor_entry.get()
        ok, message = validator.check_word_input(eng, kor)
        if not ok:
            messagebox.showwarning('입력 확인', message)
            return
        if not word_manager.add_word(self.words, eng, kor):
            messagebox.showinfo('알림', '이미 있는 단어입니다.')
            return
        file_io.save_words(self.words)
        self.refresh_word_list()
        self.clear_entries()
        messagebox.showinfo('완료', f"'{eng.strip()}' 단어를 추가했습니다.")

    def delete_word(self):
        """입력칸(또는 표에서 선택한) 단어를 삭제하고 저장한다."""
        eng = self.eng_entry.get().strip()
        if not eng:
            messagebox.showwarning('입력 확인', '삭제할 단어를 입력하거나 선택하세요.')
            return
        if not messagebox.askyesno('삭제 확인', f"'{eng}' 단어를 삭제할까요?"):
            return
        if word_manager.delete_word(self.words, eng):
            file_io.save_words(self.words)
            self.refresh_word_list()
            self.clear_entries()
        else:
            messagebox.showinfo('알림', '없는 단어입니다.')

    def search_word(self):
        """입력한 영어 단어를 찾아 표에서 선택해 보여준다."""
        eng = self.eng_entry.get().strip().lower()
        if not eng:
            messagebox.showwarning('입력 확인', '검색할 영어 단어를 입력하세요.')
            return
        meaning = word_manager.search_word(self.words, eng)
        if meaning is None:
            messagebox.showinfo('검색 결과', '없는 단어입니다.')
            return
        self.tree.selection_set(eng)
        self.tree.see(eng)
        messagebox.showinfo('검색 결과', f'{eng} : {meaning}')

    # ================= 퀴즈 탭 =================

    def _build_quiz_tab(self):
        """퀴즈 설정, 문제, 답 입력 화면을 만든다."""
        tab = self.quiz_tab

        setting = ttk.LabelFrame(tab, text='퀴즈 설정', padding=10)
        setting.pack(fill='x')
        self.mode_var = tk.StringVar(value=quiz.EN_TO_KO)
        ttk.Radiobutton(setting, text='영어 → 뜻', value=quiz.EN_TO_KO,
                        variable=self.mode_var).grid(row=0, column=0)
        ttk.Radiobutton(setting, text='뜻 → 영어', value=quiz.KO_TO_EN,
                        variable=self.mode_var).grid(row=0, column=1,
                                                     padx=10)
        ttk.Label(setting, text='문제 수').grid(row=0, column=2, padx=(20, 4))
        self.count_var = tk.StringVar(value='10')
        ttk.Spinbox(setting, from_=1, to=99, width=5,
                    textvariable=self.count_var).grid(row=0, column=3)

        self.start_button = ttk.Button(setting, text='퀴즈 시작',
                                       command=self.start_quiz)
        self.start_button.grid(row=1, column=0, columnspan=2, sticky='we',
                               pady=(10, 0))
        self.wrong_button = ttk.Button(setting, text='오답노트 풀기',
                                       command=self.start_wrong_quiz)
        self.wrong_button.grid(row=1, column=2, columnspan=2, sticky='we',
                               pady=(10, 0), padx=(20, 0))

        self.progress_label = ttk.Label(tab, text='퀴즈를 시작하세요',
                                        foreground='#B85A16')
        self.progress_label.pack(pady=(24, 0))
        self.question_label = ttk.Label(tab, text='VocaQuiz',
                                        font=(FONT, 30, 'bold'))
        self.question_label.pack(pady=10)

        answer_row = ttk.Frame(tab)
        answer_row.pack()
        self.answer_entry = ttk.Entry(answer_row, width=30,
                                      font=(FONT, 14), state='disabled')
        self.answer_entry.pack(side='left')
        self.answer_entry.bind('<Return>', lambda event: self.submit_answer())
        self.submit_button = ttk.Button(answer_row, text='제출',
                                        command=self.submit_answer,
                                        state='disabled')
        self.submit_button.pack(side='left', padx=6)

        self.feedback_label = ttk.Label(tab, text='', font=(FONT, 13))
        self.feedback_label.pack(pady=(16, 0))
        self.score_label = ttk.Label(tab, text='')
        self.score_label.pack(pady=(6, 0))

    def start_quiz(self):
        """일반 퀴즈를 시작한다."""
        if not validator.is_valid_count(self.count_var.get()):
            messagebox.showwarning('입력 확인', '문제 수는 1~99 사이 숫자로 입력하세요.')
            return
        self._begin(self.words, int(self.count_var.get()), is_wrong=False)

    def start_wrong_quiz(self):
        """오답노트의 단어를 모두 출제한다."""
        wrong = file_io.load_words(file_io.WRONG_PATH, notify=False)
        if not wrong:
            messagebox.showinfo('오답노트', '오답노트가 비어 있습니다. 👍')
            return
        self._begin(wrong, len(wrong), is_wrong=True)

    def _begin(self, words, n, is_wrong):
        """퀴즈 상태를 초기화하고 첫 문제를 보여준다."""
        self.mode = self.mode_var.get()
        try:
            self.items = quiz.make_quiz(words, n, self.mode)
        except ValueError as e:
            messagebox.showwarning('퀴즈', f'{e}\n단어장에 단어를 먼저 추가하세요.')
            return
        self.results = []
        self.index = 0
        self.is_wrong_quiz = is_wrong

        self.start_button.config(state='disabled')
        self.wrong_button.config(state='disabled')
        self.answer_entry.config(state='normal')
        self.submit_button.config(state='normal')
        self.feedback_label.config(text='')
        self.show_question()

    def show_question(self):
        """현재 문제를 화면에 보여준다."""
        item = self.items[self.index]
        kind = '오답노트' if self.is_wrong_quiz else MODE_NAMES[self.mode]
        self.progress_label.config(
            text=f'{kind}  Q. {self.index + 1} / {len(self.items)}')
        self.question_label.config(text=quiz.get_question(item, self.mode))
        self.answer_entry.delete(0, 'end')
        self.answer_entry.focus()
        correct, _ = quiz.get_score(self.results)
        self.score_label.config(text=f'현재 점수 {correct} / {self.index}')

    def submit_answer(self):
        """답을 채점하고 다음 문제로 넘어간다."""
        if not self.items or self.index >= len(self.items):
            return
        item = self.items[self.index]
        result = quiz.make_result(item, self.answer_entry.get(), self.mode)
        self.results.append(result)

        question = quiz.get_question(item, self.mode)
        if result['correct']:
            self.feedback_label.config(text=f'⭕ {question} 정답!',
                                       foreground='#2F5FBF')
        else:
            answer = item[1] if self.mode == quiz.EN_TO_KO else item[0]
            self.feedback_label.config(
                text=f'❌ {question} 오답  (정답: {answer})',
                foreground='#C0392B')

        self.index += 1
        if self.index < len(self.items):
            self.show_question()
        else:
            self.finish_quiz()

    def finish_quiz(self):
        """점수를 기록하고 오답노트를 갱신한다."""
        correct, total = quiz.get_score(self.results)
        date = time.strftime('%Y-%m-%d %H:%M')
        file_io.append_record(date, MODE_NAMES[self.mode], correct, total)

        new_wrong = quiz.get_wrong_words(self.results)
        if self.is_wrong_quiz:
            # 오답노트 퀴즈: 맞힌 단어는 빼고 틀린 단어만 남긴다
            file_io.save_words(new_wrong, file_io.WRONG_PATH)
            extra = f'남은 오답: {len(new_wrong)}개'
        else:
            # 일반 퀴즈: 틀린 단어를 오답노트에 추가한다
            wrong = file_io.load_words(file_io.WRONG_PATH, notify=False)
            wrong.update(new_wrong)
            file_io.save_words(wrong, file_io.WRONG_PATH)
            extra = f'오답노트에 {len(new_wrong)}개 저장'

        self.progress_label.config(text='퀴즈 종료')
        self.question_label.config(text=f'{correct} / {total}')
        self.score_label.config(text=extra)
        self.answer_entry.delete(0, 'end')
        self.answer_entry.config(state='disabled')
        self.submit_button.config(state='disabled')
        self.start_button.config(state='normal')
        self.wrong_button.config(state='normal')
        self.refresh_records()
        messagebox.showinfo('퀴즈 결과', f'점수: {correct} / {total}\n{extra}')

    # ================= 학습 기록 탭 =================

    def _build_record_tab(self):
        """학습 기록 목록을 만든다."""
        tab = self.record_tab
        ttk.Label(tab, text='최근 학습 기록 (최신순)').pack(anchor='w')
        self.record_list = tk.Listbox(tab, height=18,
                                      font=('Consolas', 11))
        self.record_list.pack(fill='both', expand=True, pady=(4, 10))
        ttk.Button(tab, text='새로고침',
                   command=self.refresh_records).pack(anchor='e')

    def refresh_records(self):
        """기록 파일을 다시 읽어 목록을 채운다."""
        self.record_list.delete(0, 'end')
        records = file_io.load_records()
        if not records:
            self.record_list.insert('end', '아직 학습 기록이 없습니다.')
            return
        for date, mode, correct, total in reversed(records):
            rate = correct / total * 100 if total else 0
            self.record_list.insert(
                'end', f'{date}   {mode}   {correct:>2}/{total:<2}  '
                       f'({rate:.0f}%)')


def run():
    """GUI 프로그램을 실행한다."""
    app = VocaApp()
    app.mainloop()