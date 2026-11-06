"""모서리가 둥근 카드와 버튼 (Canvas에 직접 그려서 만든다).

Tkinter의 기본 위젯은 모서리를 둥글게 만들 수 없어서,
Canvas 위에 둥근 사각형을 그리고 그 위에 글씨나 다른 위젯을 올린다.
"""

import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk

from vocaquiz.theme import (BLUE, BLUE_DARK, CREAM, FONT, GRAY, LINE, NAVY,
                            RED, RED_LIGHT, STRIPE, WHITE)

# 버튼 종류별 색: (배경, 글씨, 테두리, 마우스를 올렸을 때 배경)
BUTTON_COLORS = {
    'primary': (BLUE, WHITE, BLUE, BLUE_DARK),
    'default': (WHITE, NAVY, LINE, STRIPE),
    'danger': (WHITE, RED, LINE, RED_LIGHT),
}
DISABLED_COLORS = (LINE, GRAY, LINE)


def draw_round_rect(canvas, x1, y1, x2, y2, r, **options):
    """Canvas에 모서리가 r만큼 둥근 사각형을 그린다.

    꼭짓점마다 점을 두 번씩 찍고 smooth=True로 이으면
    모서리 부분만 부드러운 곡선이 된다.
    """
    r = max(0, min(r, (x2 - x1) / 2, (y2 - y1) / 2))
    points = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
              x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
              x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
    return canvas.create_polygon(points, smooth=True, **options)


class RoundedCard(tk.Canvas):
    """흰색 둥근 카드. 안에 넣을 위젯은 card.inner 에 넣는다."""

    def __init__(self, parent, radius=16, padding=16, color=WHITE,
                 outer=CREAM, border=None):
        super().__init__(parent, bg=outer, highlightthickness=0, bd=0)
        self.radius = radius
        self.padding = padding
        self.color = color
        self.border = border or color

        self.inner = ttk.Frame(self, style='Card.TFrame')
        self._window = self.create_window(padding, padding,
                                          window=self.inner, anchor='nw')
        self.bind('<Configure>', self._redraw)
        self.inner.bind('<Configure>', self._fit_to_inner)

    def _fit_to_inner(self, event=None):
        """안쪽 내용의 크기에 맞춰 카드가 필요한 크기를 알려준다."""
        pad = self.padding * 2
        self.config(width=self.inner.winfo_reqwidth() + pad,
                    height=self.inner.winfo_reqheight() + pad)

    def _redraw(self, event):
        """카드 크기가 바뀔 때마다 둥근 배경을 다시 그린다."""
        self.delete('bg')
        draw_round_rect(self, 1, 1, event.width - 1, event.height - 1,
                        self.radius, fill=self.color, outline=self.border,
                        tags='bg')
        self.tag_lower('bg')
        pad = self.padding * 2
        self.itemconfig(self._window, width=max(1, event.width - pad),
                        height=max(1, event.height - pad))


class RoundedButton(tk.Canvas):
    """모서리가 둥근 버튼. kind는 'primary', 'default', 'danger' 중 하나."""

    def __init__(self, parent, text, command=None, kind='default',
                 outer=WHITE, radius=10, font_size=11, padx=16, pady=7,
                 width=None):
        self.font = tkfont.Font(family=FONT, size=font_size, weight='bold')
        text_width = self.font.measure(text)
        self.btn_width = width or text_width + padx * 2
        self.btn_height = self.font.metrics('linespace') + pady * 2
        super().__init__(parent, width=self.btn_width,
                         height=self.btn_height, bg=outer,
                         highlightthickness=0, bd=0, cursor='hand2')

        self.text = text
        self.command = command
        self.kind = kind
        self.radius = radius
        self.state = 'normal'
        self.hover = False

        self.bind('<Configure>', lambda event: self._draw())
        self.bind('<Enter>', lambda event: self._set_hover(True))
        self.bind('<Leave>', lambda event: self._set_hover(False))
        self.bind('<ButtonRelease-1>', self._on_click)
        self._draw()

    def _draw(self):
        """현재 상태(보통 / 마우스 올림 / 비활성)에 맞게 버튼을 그린다."""
        self.delete('all')
        width = self.winfo_width() if self.winfo_width() > 1 \
            else self.btn_width
        height = self.winfo_height() if self.winfo_height() > 1 \
            else self.btn_height
        if self.state == 'disabled':
            fill, text_color, border = DISABLED_COLORS
        else:
            fill, text_color, border, hover_fill = BUTTON_COLORS[self.kind]
            if self.hover:
                fill = hover_fill
        draw_round_rect(self, 1, 1, width - 1, height - 1, self.radius,
                        fill=fill, outline=border)
        self.create_text(width / 2, height / 2, text=self.text,
                         fill=text_color, font=self.font)

    def _set_hover(self, value):
        self.hover = value
        self._draw()

    def _on_click(self, event):
        """버튼 안에서 마우스를 뗐을 때만 명령을 실행한다."""
        inside = (0 <= event.x <= self.winfo_width()
                  and 0 <= event.y <= self.winfo_height())
        if self.state == 'normal' and inside and self.command:
            self.command()

    def config(self, cnf=None, state=None, **kwargs):
        """state='disabled' / 'normal' 로 버튼을 끄고 켤 수 있게 한다."""
        if state is not None:
            self.state = state
            self['cursor'] = 'hand2' if state == 'normal' else 'arrow'
            self._draw()
        if cnf or kwargs:
            return super().config(cnf, **kwargs)

    configure = config
