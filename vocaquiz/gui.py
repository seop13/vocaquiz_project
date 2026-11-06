"""VocaQuiz GUI 버전 (Tkinter).

탭 3개로 구성한다.
    [단어장]   단어장(카테고리) 선택·만들기·삭제, 단어 추가·삭제·검색
    [퀴즈]     단어장별 / 전체 퀴즈, 오답노트 퀴즈
    [학습 기록] 날짜별 점수

실행은 프로젝트 폴더에서  python main.py
"""

import time
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

from vocaquiz import file_io, quiz, validator, word_manager

FONT = '맑은 고딕'
MODE_NAMES = {quiz.EN_TO_KO: '영어→뜻', quiz.KO_TO_EN: '뜻→영어'}
ALL_CATEGORY = '전체'

# 색상 (발표 PPT와 같은 색 조합)
NAVY = '#1F2A44'        # 진한 남색: 제목, 머리글
CREAM = '#F7F5EF'       # 연한 크림색: 창 배경
WHITE = '#FFFFFF'       # 카드 배경
STRIPE = '#F3F0E8'      # 표 줄무늬
LINE = '#E2DED3'        # 테두리
GRAY = '#6A7179'        # 보조 글씨
BLUE = '#2F5FBF'        # 주요 버튼, 정답
BLUE_DARK = '#244C99'
ORANGE = '#F2A65A'      # 강조
ORANGE_DARK = '#B85A16'
RED = '#C0392B'         # 오답, 삭제


class VocaApp(tk.Tk):
    """VocaQuiz 메인 창."""

    def __init__(self):
        super().__init__()
        self.title('VocaQuiz - 영어 단어장 퀴즈')
        # 화면 배율(100%, 125%, 150% …)에 맞춰 창 크기를 키운다.
        # 글씨는 배율에 맞춰 커지지만 픽셀로 정한 크기는 그대로라서,
        # 직접 곱해 주지 않으면 창이 작아져 아래쪽이 잘린다.
        self.scale = max(1.0, self.winfo_fpixels('1i') / 96)
        width = min(self.px(780), self.winfo_screenwidth() - 40)
        height = min(self.px(660), self.winfo_screenheight() - 80)
        self.geometry(f'{width}x{height}')
        self.minsize(min(self.px(720), width), min(self.px(600), height))
        self.configure(bg=CREAM)
        self.option_add('*Font', (FONT, 11))
        self._setup_style()

        file_io.prepare_wordbooks()
        self.category = file_io.list_categories()[0]   # 지금 보고 있는 단어장
        self.words = file_io.load_category(self.category)
        self.quiz_title = ''     # 기록에 남길 퀴즈 이름 (예: 과일)

        # 퀴즈 진행 상태
        self.items = []          # 출제된 문제 [(영어, 뜻), ...]
        self.results = []        # 채점 결과
        self.index = 0           # 지금 몇 번째 문제인지
        self.mode = quiz.EN_TO_KO
        self.is_wrong_quiz = False

        self._build_header()

        notebook = ttk.Notebook(self)
        notebook.pack(fill='both', expand=True, padx=16, pady=(12, 16))
        self.word_tab = ttk.Frame(notebook, padding=16)
        self.quiz_tab = ttk.Frame(notebook, padding=16)
        self.record_tab = ttk.Frame(notebook, padding=16)
        notebook.add(self.word_tab, text='단어장')
        notebook.add(self.quiz_tab, text='퀴즈')
        notebook.add(self.record_tab, text='학습 기록')

        self._build_word_tab()
        self._build_quiz_tab()
        self._build_record_tab()

        self.refresh_categories()
        self.refresh_word_list()
        self.refresh_records()

    # ================= 디자인 =================

    def px(self, size):
        """100% 배율 기준 픽셀 크기를 현재 화면 배율에 맞게 바꾼다."""
        return int(size * self.scale)

    def _setup_style(self):
        """ttk 위젯들의 색과 글꼴을 한 곳에서 정한다."""
        style = ttk.Style(self)
        style.theme_use('clam')

        style.configure('.', background=CREAM, foreground=NAVY,
                        font=(FONT, 11), bordercolor=LINE)
        style.configure('TFrame', background=CREAM)
        style.configure('Card.TFrame', background=WHITE)
        style.configure('TLabel', background=CREAM, foreground=NAVY)
        style.configure('Card.TLabel', background=WHITE)
        style.configure('Sub.TLabel', foreground=GRAY, font=(FONT, 10))
        style.configure('CardSub.TLabel', background=WHITE, foreground=GRAY,
                        font=(FONT, 10))
        style.configure('Title.TLabel', font=(FONT, 13, 'bold'))
        style.configure('CardTitle.TLabel', background=WHITE,
                        font=(FONT, 12, 'bold'))
        style.configure('Card.TRadiobutton', background=WHITE)
        style.map('Card.TRadiobutton', background=[('active', WHITE)])

        # 탭
        style.configure('TNotebook', background=CREAM, borderwidth=0)
        style.configure('TNotebook.Tab', font=(FONT, 11, 'bold'),
                        padding=(22, 8), background=LINE, foreground=GRAY,
                        borderwidth=0)
        style.map('TNotebook.Tab',
                  background=[('selected', WHITE)],
                  foreground=[('selected', NAVY)])

        # 버튼: 기본 / 강조(파랑) / 위험(빨강)
        style.configure('TButton', padding=(14, 6), background=WHITE,
                        foreground=NAVY, borderwidth=1, focusthickness=0)
        style.map('TButton', background=[('active', STRIPE)])
        style.configure('Accent.TButton', background=BLUE, foreground=WHITE,
                        bordercolor=BLUE, font=(FONT, 11, 'bold'))
        style.map('Accent.TButton',
                  background=[('disabled', LINE), ('active', BLUE_DARK)],
                  foreground=[('disabled', GRAY)])
        style.configure('Danger.TButton', foreground=RED)

        # 입력칸
        style.configure('TEntry', padding=6, fieldbackground=WHITE)
        style.configure('TCombobox', padding=4, fieldbackground=WHITE)
        style.map('TCombobox', fieldbackground=[('readonly', WHITE)])
        style.configure('TSpinbox', padding=4, fieldbackground=WHITE)

        # 표
        style.configure('Treeview', rowheight=self.px(30), background=WHITE,
                        fieldbackground=WHITE, borderwidth=0,
                        font=(FONT, 11))
        style.configure('Treeview.Heading', background=NAVY,
                        foreground=WHITE, font=(FONT, 11, 'bold'),
                        padding=6, borderwidth=0)
        style.map('Treeview.Heading', background=[('active', NAVY)])
        style.map('Treeview', background=[('selected', ORANGE)],
                  foreground=[('selected', NAVY)])

        # 진행 막대
        style.configure('Quiz.Horizontal.TProgressbar', troughcolor=STRIPE,
                        background=ORANGE, bordercolor=STRIPE, thickness=10)

    def _build_header(self):
        """창 맨 위의 남색 제목 띠를 만든다."""
        header = tk.Frame(self, bg=NAVY, height=self.px(64))
        header.pack(fill='x')
        tk.Label(header, text='VocaQuiz', bg=NAVY, fg=WHITE,
                 font=(FONT, 20, 'bold')).pack(side='left', padx=(20, 8),
                                               pady=12)
        tk.Label(header, text='영어 단어장 퀴즈', bg=NAVY, fg=ORANGE,
                 font=(FONT, 11, 'bold')).pack(side='left', pady=(10, 0))
        self.header_stats = tk.Label(header, text='', bg=NAVY, fg='#BFC8D8',
                                     font=(FONT, 10))
        self.header_stats.pack(side='right', padx=20)

    def refresh_header(self):
        """제목 띠 오른쪽의 요약 정보를 갱신한다."""
        categories = file_io.list_categories()
        total = len(file_io.load_all_categories())
        wrong = len(file_io.load_words(file_io.WRONG_PATH, notify=False))
        self.header_stats.config(
            text=f'단어장 {len(categories)}개  ·  단어 {total}개  ·  '
                 f'오답 {wrong}개')

    @staticmethod
    def _card(parent, padding=16):
        """흰색 카드 모양의 틀을 만든다."""
        return ttk.Frame(parent, style='Card.TFrame', padding=padding)

    # ================= 단어장 탭 =================

    def _build_word_tab(self):
        """단어 목록(표)과 입력칸, 버튼을 만든다."""
        tab = self.word_tab

        top = ttk.Frame(tab)
        top.pack(fill='x', pady=(0, 10))
        ttk.Label(top, text='단어장', style='Title.TLabel').pack(side='left')
        self.category_var = tk.StringVar(value=self.category)
        self.category_box = ttk.Combobox(top, textvariable=self.category_var,
                                         state='readonly', width=14,
                                         font=(FONT, 11))
        self.category_box.pack(side='left', padx=8)
        self.category_box.bind('<<ComboboxSelected>>',
                               lambda event: self.change_category())
        ttk.Button(top, text='+ 새 단어장',
                   command=self.new_category).pack(side='left')
        ttk.Button(top, text='단어장 삭제', style='Danger.TButton',
                   command=self.remove_category).pack(side='left', padx=6)
        self.count_label = ttk.Label(top, text='', style='Sub.TLabel')
        self.count_label.pack(side='right')

        # 입력 카드를 먼저 아래쪽에 고정해서, 창이 작아도 항상 보이게 한다
        form = self._card(tab, padding=14)
        form.pack(side='bottom', fill='x', pady=(12, 0))

        table_frame = ttk.Frame(tab)
        table_frame.pack(fill='both', expand=True)
        self.tree = ttk.Treeview(table_frame, columns=('eng', 'kor'),
                                 show='headings', height=6)
        self.tree.heading('eng', text='영어', anchor='w')
        self.tree.heading('kor', text='뜻', anchor='w')
        self.tree.column('eng', width=240, anchor='w')
        self.tree.column('kor', width=380, anchor='w')
        self.tree.tag_configure('odd', background=STRIPE)
        scroll = ttk.Scrollbar(table_frame, orient='vertical',
                               command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side='left', fill='both', expand=True)
        scroll.pack(side='right', fill='y')
        self.tree.bind('<<TreeviewSelect>>', self.on_select_word)

        ttk.Label(form, text='영어', style='CardSub.TLabel').grid(
            row=0, column=0, sticky='w')
        ttk.Label(form, text='뜻 (여러 개면 쉼표로 구분)',
                  style='CardSub.TLabel').grid(row=0, column=1, sticky='w',
                                               padx=(10, 0))
        self.eng_entry = ttk.Entry(form, width=22, font=(FONT, 11))
        self.kor_entry = ttk.Entry(form, width=32, font=(FONT, 11))
        self.eng_entry.grid(row=1, column=0, sticky='we', pady=(4, 10))
        self.kor_entry.grid(row=1, column=1, sticky='we', padx=(10, 0),
                            pady=(4, 10))
        self.kor_entry.bind('<Return>', lambda event: self.add_word())
        form.columnconfigure(1, weight=1)

        buttons = ttk.Frame(form, style='Card.TFrame')
        buttons.grid(row=2, column=0, columnspan=2, sticky='we')
        ttk.Button(buttons, text='추가', style='Accent.TButton',
                   command=self.add_word).pack(side='left')
        ttk.Button(buttons, text='검색',
                   command=self.search_word).pack(side='left', padx=6)
        ttk.Button(buttons, text='삭제', style='Danger.TButton',
                   command=self.delete_word).pack(side='left')
        ttk.Button(buttons, text='입력칸 비우기',
                   command=self.clear_entries).pack(side='right')

    def refresh_categories(self):
        """단어장 목록을 단어장 탭과 퀴즈 탭의 선택 상자에 다시 채운다."""
        names = file_io.list_categories()
        self.category_box['values'] = names
        self.category_var.set(self.category)
        self.scope_box['values'] = [ALL_CATEGORY] + names
        if self.scope_var.get() not in self.scope_box['values']:
            self.scope_var.set(self.category)

    def change_category(self):
        """선택 상자에서 고른 단어장을 불러온다."""
        self.category = self.category_var.get()
        self.words = file_io.load_category(self.category)
        self.scope_var.set(self.category)
        self.clear_entries()
        self.refresh_word_list()

    def new_category(self):
        """새 단어장 이름을 입력받아 만든다."""
        name = simpledialog.askstring('새 단어장', '단어장 이름 (예: 과일, 동물)',
                                      parent=self)
        if name is None:
            return
        name = name.strip()
        if name == ALL_CATEGORY or not validator.is_valid_category(name):
            messagebox.showwarning('입력 확인',
                                   '단어장 이름은 한글·영어·숫자로 1~20자까지 가능합니다.')
            return
        if not file_io.create_category(name):
            messagebox.showinfo('알림', '이미 있는 단어장입니다.')
            return
        self.category = name
        self.words = {}
        self.refresh_categories()
        self.scope_var.set(name)
        self.refresh_word_list()

    def remove_category(self):
        """지금 보고 있는 단어장을 삭제한다."""
        message = (f"'{self.category}' 단어장과 단어 {len(self.words)}개를 "
                   '삭제할까요?')
        if not messagebox.askyesno('단어장 삭제', message):
            return
        file_io.delete_category(self.category)
        file_io.prepare_wordbooks()  # 하나도 없으면 '기본'을 다시 만든다
        self.category = file_io.list_categories()[0]
        self.words = file_io.load_category(self.category)
        self.refresh_categories()
        self.scope_var.set(self.category)
        self.refresh_word_list()

    def refresh_word_list(self):
        """표의 내용을 현재 단어장으로 다시 채운다. (줄무늬 포함)"""
        self.tree.delete(*self.tree.get_children())
        sorted_words = word_manager.get_sorted_words(self.words)
        for i, (eng, kor) in enumerate(sorted_words):
            tag = 'odd' if i % 2 else 'even'
            self.tree.insert('', 'end', iid=eng, values=(eng, kor),
                             tags=(tag,))
        self.count_label.config(text=f'단어 {len(self.words)}개')
        self.refresh_header()

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
        self.eng_entry.focus()

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
        file_io.save_category(self.category, self.words)
        self.refresh_word_list()
        self.clear_entries()
        self.tree.selection_set(eng.strip().lower())
        self.tree.see(eng.strip().lower())

    def delete_word(self):
        """입력칸(또는 표에서 선택한) 단어를 삭제하고 저장한다."""
        eng = self.eng_entry.get().strip()
        if not eng:
            messagebox.showwarning('입력 확인', '삭제할 단어를 입력하거나 선택하세요.')
            return
        if not messagebox.askyesno('삭제 확인', f"'{eng}' 단어를 삭제할까요?"):
            return
        if word_manager.delete_word(self.words, eng):
            file_io.save_category(self.category, self.words)
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

    # ================= 퀴즈 탭 =================

    def _build_quiz_tab(self):
        """퀴즈 설정 카드와 문제 카드를 만든다."""
        tab = self.quiz_tab

        setting = self._card(tab, padding=14)
        setting.pack(fill='x')
        ttk.Label(setting, text='출제 단어장', style='CardSub.TLabel').grid(
            row=0, column=0, sticky='w')
        ttk.Label(setting, text='모드', style='CardSub.TLabel').grid(
            row=0, column=1, sticky='w', padx=(16, 0))
        ttk.Label(setting, text='문제 수', style='CardSub.TLabel').grid(
            row=0, column=3, sticky='w', padx=(16, 0))

        self.scope_var = tk.StringVar(value=self.category)
        self.scope_box = ttk.Combobox(setting, textvariable=self.scope_var,
                                      state='readonly', width=12,
                                      font=(FONT, 11))
        self.scope_box.grid(row=1, column=0, sticky='w', pady=(4, 0))

        self.mode_var = tk.StringVar(value=quiz.EN_TO_KO)
        ttk.Radiobutton(setting, text='영어 → 뜻', value=quiz.EN_TO_KO,
                        variable=self.mode_var,
                        style='Card.TRadiobutton').grid(
            row=1, column=1, padx=(16, 0), pady=(4, 0))
        ttk.Radiobutton(setting, text='뜻 → 영어', value=quiz.KO_TO_EN,
                        variable=self.mode_var,
                        style='Card.TRadiobutton').grid(
            row=1, column=2, padx=(8, 0), pady=(4, 0))
        self.count_var = tk.StringVar(value='10')
        ttk.Spinbox(setting, from_=1, to=99, width=4, font=(FONT, 11),
                    textvariable=self.count_var).grid(
            row=1, column=3, sticky='w', padx=(16, 0), pady=(4, 0))

        buttons = ttk.Frame(setting, style='Card.TFrame')
        buttons.grid(row=0, column=4, rowspan=2, sticky='e', padx=(16, 0))
        setting.columnconfigure(4, weight=1)
        self.start_button = ttk.Button(buttons, text='퀴즈 시작',
                                       style='Accent.TButton',
                                       command=self.start_quiz)
        self.start_button.pack(fill='x')
        self.wrong_button = ttk.Button(buttons, text='오답노트 풀기',
                                       command=self.start_wrong_quiz)
        self.wrong_button.pack(fill='x', pady=(6, 0))

        board = self._card(tab, padding=18)
        board.pack(fill='both', expand=True, pady=(14, 0))

        self.progress_label = ttk.Label(board, text='퀴즈를 시작하세요',
                                        style='CardSub.TLabel')
        self.progress_label.pack()
        self.progress = ttk.Progressbar(board, length=self.px(420), maximum=1,
                                        style='Quiz.Horizontal.TProgressbar')
        self.progress.pack(pady=(8, 0))

        self.question_label = tk.Label(board, text='VocaQuiz', bg=WHITE,
                                       fg=NAVY, font=(FONT, 34, 'bold'))
        self.question_label.pack(pady=(14, 12))

        answer_row = ttk.Frame(board, style='Card.TFrame')
        answer_row.pack()
        self.answer_entry = ttk.Entry(answer_row, width=26, font=(FONT, 15),
                                      justify='center', state='disabled')
        self.answer_entry.pack(side='left', ipady=4)
        self.answer_entry.bind('<Return>', lambda event: self.submit_answer())
        self.submit_button = ttk.Button(answer_row, text='제출',
                                        style='Accent.TButton',
                                        command=self.submit_answer,
                                        state='disabled')
        self.submit_button.pack(side='left', padx=(8, 0), ipady=3)

        self.feedback_label = tk.Label(board, text='', bg=WHITE,
                                       font=(FONT, 13, 'bold'))
        self.feedback_label.pack(pady=(14, 0))
        self.score_label = ttk.Label(board, text='Enter 키로도 제출할 수 있어요',
                                     style='CardSub.TLabel')
        self.score_label.pack(pady=(4, 0))

    def start_quiz(self):
        """고른 단어장(또는 전체)으로 퀴즈를 시작한다."""
        if not validator.is_valid_count(self.count_var.get()):
            messagebox.showwarning('입력 확인', '문제 수는 1~99 사이 숫자로 입력하세요.')
            return
        scope = self.scope_var.get()
        if scope == ALL_CATEGORY:
            words = file_io.load_all_categories()
        else:
            words = file_io.load_category(scope)
        self.quiz_title = scope
        self._begin(words, int(self.count_var.get()), is_wrong=False)

    def start_wrong_quiz(self):
        """오답노트의 단어를 모두 출제한다."""
        wrong = file_io.load_words(file_io.WRONG_PATH, notify=False)
        if not wrong:
            messagebox.showinfo('오답노트', '오답노트가 비어 있습니다. 👍')
            return
        self.quiz_title = '오답노트'
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
        self.progress.config(maximum=len(self.items), value=0)
        self.feedback_label.config(text='')
        self.question_label.config(fg=NAVY)
        self.show_question()

    def show_question(self):
        """현재 문제를 화면에 보여준다."""
        item = self.items[self.index]
        kind = f'{self.quiz_title} · {MODE_NAMES[self.mode]}'
        self.progress_label.config(
            text=f'{kind}   Q. {self.index + 1} / {len(self.items)}')
        self.progress.config(value=self.index)
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
            self.feedback_label.config(text=f'⭕  {question}  정답!', fg=BLUE)
        else:
            answer = item[1] if self.mode == quiz.EN_TO_KO else item[0]
            self.feedback_label.config(
                text=f'❌  {question}  오답   정답: {answer}', fg=RED)

        self.index += 1
        if self.index < len(self.items):
            self.show_question()
        else:
            self.finish_quiz()

    def finish_quiz(self):
        """점수를 기록하고 오답노트를 갱신한다."""
        correct, total = quiz.get_score(self.results)
        date = time.strftime('%Y-%m-%d %H:%M')
        kind = f'{self.quiz_title} · {MODE_NAMES[self.mode]}'
        file_io.append_record(date, kind, correct, total)

        new_wrong = quiz.get_wrong_words(self.results)
        if self.is_wrong_quiz:
            # 오답노트 퀴즈: 맞힌 단어는 빼고 틀린 단어만 남긴다
            file_io.save_words(new_wrong, file_io.WRONG_PATH)
            extra = f'남은 오답 {len(new_wrong)}개'
        else:
            # 일반 퀴즈: 틀린 단어를 오답노트에 추가한다
            wrong = file_io.load_words(file_io.WRONG_PATH, notify=False)
            wrong.update(new_wrong)
            file_io.save_words(wrong, file_io.WRONG_PATH)
            extra = f'오답노트에 {len(new_wrong)}개 저장'

        rate = correct / total * 100
        self.progress.config(value=total)
        self.progress_label.config(text=f'{kind}   퀴즈 종료')
        self.question_label.config(text=f'{correct} / {total}',
                                   fg=BLUE if rate >= 70 else ORANGE_DARK)
        self.score_label.config(text=f'정답률 {rate:.0f}%  ·  {extra}')
        self.answer_entry.delete(0, 'end')
        self.answer_entry.config(state='disabled')
        self.submit_button.config(state='disabled')
        self.start_button.config(state='normal')
        self.wrong_button.config(state='normal')
        self.refresh_records()
        self.refresh_header()

    # ================= 학습 기록 탭 =================

    def _build_record_tab(self):
        """요약 카드와 학습 기록 표를 만든다."""
        tab = self.record_tab

        summary = self._card(tab, padding=14)
        summary.pack(fill='x', pady=(0, 12))
        self.summary_labels = []
        for title in ('푼 횟수', '평균 정답률', '최고 점수'):
            box = ttk.Frame(summary, style='Card.TFrame')
            box.pack(side='left', expand=True)
            ttk.Label(box, text=title, style='CardSub.TLabel').pack()
            value = tk.Label(box, text='-', bg=WHITE, fg=NAVY,
                             font=(FONT, 18, 'bold'))
            value.pack()
            self.summary_labels.append(value)

        table_frame = ttk.Frame(tab)
        table_frame.pack(fill='both', expand=True)
        columns = ('date', 'kind', 'score', 'rate')
        self.record_tree = ttk.Treeview(table_frame, columns=columns,
                                        show='headings', height=10)
        for col, text, width in [('date', '날짜', 150), ('kind', '퀴즈', 260),
                                 ('score', '점수', 90), ('rate', '정답률', 90)]:
            self.record_tree.heading(col, text=text)
            self.record_tree.column(col, width=width, anchor='center')
        self.record_tree.tag_configure('odd', background=STRIPE)
        scroll = ttk.Scrollbar(table_frame, orient='vertical',
                               command=self.record_tree.yview)
        self.record_tree.configure(yscrollcommand=scroll.set)
        self.record_tree.pack(side='left', fill='both', expand=True)
        scroll.pack(side='right', fill='y')

    def refresh_records(self):
        """기록 파일을 다시 읽어 요약 카드와 표를 채운다. (최신순)"""
        self.record_tree.delete(*self.record_tree.get_children())
        records = file_io.load_records()
        if not records:
            for label in self.summary_labels:
                label.config(text='-')
            return

        rates = [c / t * 100 for _, _, c, t in records if t]
        best = max(records, key=lambda r: r[2] / r[3] if r[3] else 0)
        self.summary_labels[0].config(text=f'{len(records)}회')
        self.summary_labels[1].config(text=f'{sum(rates) / len(rates):.0f}%')
        self.summary_labels[2].config(text=f'{best[2]} / {best[3]}')

        for i, (date, kind, correct, total) in enumerate(reversed(records)):
            rate = correct / total * 100 if total else 0
            tag = 'odd' if i % 2 else 'even'
            self.record_tree.insert(
                '', 'end', tags=(tag,),
                values=(date, kind, f'{correct} / {total}', f'{rate:.0f}%'))


def run():
    """GUI 프로그램을 실행한다."""
    try:
        # 윈도우 화면 배율(125%, 150% 등)에서 글씨가 흐려지지 않게 한다
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except (ImportError, AttributeError, OSError):
        pass  # 윈도우가 아니거나 지원하지 않으면 그냥 넘어간다
    app = VocaApp()
    app.mainloop()