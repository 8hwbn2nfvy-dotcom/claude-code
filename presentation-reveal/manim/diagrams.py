"""Анимированные схемы для слайдов 2–7 (Manim Community 0.19).

Каждая сцена рисуется на прозрачном фоне в координатах макета 600×H px
(как прежние SVG-схемы), затем build.py собирает кадры в анимированный WebP.
Запуск: python manim/render.py
"""
import numpy as np
from manim import *

FONT = "Carlito"          # метрический аналог Calibri, есть кириллица
K_FONT = 0.963            # px макета -> font_size Manim (замерено для Carlito)
U = 1 / 75                # 1 px макета в единицах Manim (600 px = 8 единиц)

PAL = {  # светлый, основной, кромка
    "rose":  ("#ffe1dc", "#f2b2a8", "#c98479"),
    "sage":  ("#e0f3e6", "#b3dcc1", "#7fae90"),
    "sky":   ("#e1edfc", "#b3cdef", "#7f9fcc"),
    "lilac": ("#ebe5fc", "#cbc0f0", "#988bc7"),
    "sand":  ("#fcefd4", "#f0d3a0", "#c6a46a"),
}
INK, INK2, GOLD = "#26322b", "#4a5a50", "#f6dca0"


class Diagram(Scene):
    VH = 480  # высота макета в px

    # ---------- координаты ----------
    def P(self, x, y):
        return np.array([(x - 300) * U, (self.VH / 2 - y) * U, 0])

    # ---------- текст ----------
    def T(self, x, y, s, size, bold=True, color=INK, anchor="middle", white=False, opacity=1):
        t = Text(s, font=FONT, font_size=size * K_FONT, weight=BOLD if bold else NORMAL, color=color)
        t.set_fill(opacity=opacity)
        if white:
            t.set_color(WHITE).set_fill(opacity=opacity)
            t.set_stroke(BLACK, width=5, opacity=0.45, background=True)
        top = self.P(0, y - 0.644 * size)[1]          # верх заглавных = базовая линия - высота заглавной
        t.shift(UP * (top - t.get_top()[1]))
        if anchor == "middle":
            t.shift(RIGHT * (self.P(x, 0)[0] - t.get_center()[0]))
        elif anchor == "start":
            t.shift(RIGHT * (self.P(x, 0)[0] - t.get_left()[0]))
        else:
            t.shift(RIGHT * (self.P(x, 0)[0] - t.get_right()[0]))
        return t

    def W(self, *a, **k):  # белый текст поверх фото
        return self.T(*a, white=True, **k)

    # ---------- мягкая плашка ----------
    def rrect(self, x, y, w, h, rx):
        r = RoundedRectangle(corner_radius=min(rx, w / 2, h / 2) * U, width=w * U, height=h * U)
        r.move_to(self.P(x + w / 2, y + h / 2))
        return r

    def card(self, x, y, w, h, name, rx=16, lift=7):
        light, base, edge = PAL[name]
        g = VGroup()
        for k, op in ((14, .07), (9, .09), (4, .12)):          # мягкая тень
            g.add(self.rrect(x - k / 2, y + 10 - k / 4, w + k, h + k, rx + k / 2).set_fill(BLACK, op).set_stroke(width=0))
        g.add(self.rrect(x, y + lift, w, h, rx).set_fill(edge, 1).set_stroke(width=0))      # кромка
        face = self.rrect(x, y, w, h, rx).set_stroke(width=0)
        face.set_fill([light, base], 1)
        face.set_sheen_direction(DOWN)
        g.add(face)
        g.add(self.rrect(x + 3, y + 3, w - 6, max(8, h * .42), max(4, rx - 3)).set_fill(WHITE, .28).set_stroke(width=0))
        return g

    def orb(self, x, y, r=16):
        return VGroup(
            Circle(radius=(r + 12) * U).set_fill(GOLD, .18).set_stroke(width=0),
            Circle(radius=(r + 5) * U).set_fill(GOLD, .28).set_stroke(width=0),
            Circle(radius=r * U).set_fill(["#fffaf0", "#d9b36a"], 1).set_sheen_direction(DR).set_stroke(width=0),
            Circle(radius=r * .35 * U).set_fill(WHITE, .8).set_stroke(width=0).shift(LEFT * r * .35 * U + UP * r * .35 * U),
        ).move_to(self.P(x, y))

    def bez(self, *pts):
        return CubicBezier(*[self.P(*p) for p in pts])

    def poly(self, pts, **kw):
        return Polygon(*[self.P(*p) for p in pts], **kw)

    def line(self, a, b, color=WHITE, width=3, opacity=1):
        return Line(self.P(*a), self.P(*b)).set_stroke(color, width, opacity)


# ======================= слайд 2 =======================
class S2(Diagram):
    VH = 470

    def construct(self):
        title = self.W(300, 40, "Одна жизнь или две?", 32)
        c1 = VGroup(self.card(40, 180, 210, 165, "rose", 22), self.T(145, 238, "1825", 48), self.T(145, 278, "Таганрог", 26),
                    self.T(145, 306, "смерть", 19, False, INK2), self.T(145, 329, "Александра I", 19, False, INK2))
        c2 = VGroup(self.card(350, 180, 210, 165, "sage", 22), self.T(455, 238, "1837", 48), self.T(455, 278, "Томск", 26),
                    self.T(455, 306, "появление", 19, False, INK2), self.T(455, 329, "старца", 19, False, INK2))
        arc = self.bez((150, 168), (205, 60), (400, 60), (452, 160))
        glow = arc.copy().set_stroke(WHITE, 12, .25)
        dash = DashedVMobject(arc.copy().set_stroke(WHITE, 3), num_dashes=26, dashed_ratio=.35)
        head = VMobject().set_points_as_corners([self.P(441, 152), self.P(453, 170), self.P(464, 150)]).set_stroke(WHITE, 3.5)
        orb = self.orb(150, 168)
        pill = VGroup(self.card(165, 398, 270, 50, "lilac", 25, 5), self.T(300, 430, "12 лет между событиями", 21))

        self.play(Write(title), run_time=.5)
        self.play(LaggedStart(FadeIn(c1, shift=UP * .25, scale=.9), FadeIn(c2, shift=UP * .25, scale=.9), lag_ratio=.35), run_time=.7)
        self.add(glow)
        self.play(Create(glow), Create(dash), MoveAlongPath(orb, arc), run_time=.8, rate_func=smooth)
        self.play(orb.animate.move_to(self.P(302, 83)), Create(head), run_time=.3)
        self.play(GrowFromCenter(pill), run_time=.4)
        self.wait(.1)


# ======================= слайд 3 =======================
class S3(Diagram):
    VH = 490

    def construct(self):
        cols = ["lilac", "sky", "sage", "sand", "rose"]
        ev = [("1777", ["Рождение"]), ("1801", ["Становится императором"]), ("1812", ["Война с Наполеоном"]),
              ("1814", ["Въезд в Париж во главе", "союзных войск"]), ("1825", ["Смерть в Таганроге, 47 лет"])]
        title = self.W(300, 36, "Жизнь Александра I", 30)
        axis = self.line((66, 96), (66, 452), WHITE, 3, .45)
        rows = []
        for i, ((yr, lines), c) in enumerate(zip(ev, cols)):
            y = 70 + i * 82
            pill = VGroup(self.card(14, y, 104, 54, c, 27, 5), self.T(66, y + 36, yr, 27))
            box = self.rrect(138, y, 448, 54, 14).set_fill(WHITE, .12).set_stroke(WHITE, 1.5, .35)
            if len(lines) == 1:
                txt = VGroup(self.W(158, y + 35, lines[0], 22, bold=True, anchor="start"))
            else:
                txt = VGroup(self.W(158, y + 24, lines[0], 19, anchor="start"), self.W(158, y + 46, lines[1], 19, anchor="start"))
            rows.append((pill, box, txt))
        self.play(Write(title), Create(axis), run_time=.5)
        self.play(LaggedStart(*[AnimationGroup(GrowFromCenter(p), FadeIn(b, shift=RIGHT * .3), lag_ratio=.3) for p, b, _ in rows], lag_ratio=.18), run_time=1.1)
        self.play(LaggedStart(*[Write(t) for _, _, t in rows], lag_ratio=.12), run_time=.8)
        self.wait(.1)


# ======================= слайд 4 =======================
class S4(Diagram):
    VH = 455

    def construct(self):
        title = self.W(300, 36, "Путь легенды", 30)
        shadow = self.rrect(40, 104, 520, 300, 26).set_fill("#9fb594", 1).set_stroke(width=0)
        land = self.rrect(40, 96, 520, 300, 26).set_stroke(width=0)
        land.set_fill(["#e3efd9", "#c9dfc0", "#e6d8b6"], 1).set_sheen_direction(DR)
        soft = VGroup(*[self.rrect(40 - k / 2, 106 - k / 4, 520 + k, 300 + k, 26 + k / 2).set_fill(BLACK, op).set_stroke(width=0)
                        for k, op in ((14, .07), (8, .1))])
        contours = VGroup(*[self.bez(*c).set_stroke(WHITE, 2, .6) for c in (
            ((70, 190), (150, 170), (210, 210), (270, 186)), ((70, 300), (160, 272), (230, 320), (320, 292)),
            ((350, 130), (410, 160), (470, 126), (540, 146)), ((350, 340), (410, 308), (470, 340), (540, 316)))])
        mts = VGroup()
        for cx, by in [(300, 170), (290, 214), (303, 258), (292, 302), (304, 346)]:
            mts.add(VGroup(self.poly([(cx - 24, by), (cx, by - 44), (cx, by)]).set_fill("#c9b892", 1).set_stroke(width=0),
                           self.poly([(cx, by - 44), (cx + 24, by), (cx, by)]).set_fill("#a8946c", 1).set_stroke(width=0)))
        ural = self.T(334, 366, "Урал", 18, True, "#6d5a35", "start")
        route = self.bez((150, 318), (230, 252), (340, 214), (450, 170))
        rglow = route.copy().set_stroke("#e8a598", 12, .45)
        rdash = DashedVMobject(route.copy().set_stroke("#c4655a", 3), num_dashes=22, dashed_ratio=.55)

        def pin(x, y, col, dark):
            head = Circle(radius=15 * U).set_fill(col, 1).set_stroke(dark, 1.5).move_to(self.P(x, y - 32))
            tip = self.poly([(x - 11, y - 22), (x + 11, y - 22), (x, y)]).set_fill(col, 1).set_stroke(dark, 1.5)
            return VGroup(Ellipse(width=20 * U, height=7 * U).set_fill(BLACK, .35).set_stroke(width=0).move_to(self.P(x, y + 2)),
                          tip, head, Circle(radius=5.5 * U).set_fill(WHITE, 1).set_stroke(width=0).move_to(self.P(x, y - 32)))
        p1 = VGroup(pin(150, 168, "#b3cdef", "#7f9fcc"), self.T(174, 160, "Петербург", 19, True, INK, "start"))
        p2 = VGroup(pin(150, 328, "#f2b2a8", "#c98479"), self.T(174, 322, "Таганрог", 21, True, INK, "start"),
                    self.T(174, 345, "1825, смерть царя", 16, False, INK2, "start"))
        p3 = VGroup(pin(466, 176, "#f0d3a0", "#c6a46a"), self.T(444, 128, "Томск", 21, True, INK, "end"),
                    self.T(444, 149, "март 1837", 16, False, INK2, "end"))
        note = self.W(300, 440, "Схема без масштаба", 16, bold=False, opacity=.8)

        self.play(Write(title), FadeIn(VGroup(soft, shadow, land), scale=.92), run_time=.6)
        self.play(Create(contours), LaggedStart(*[GrowFromEdge(m, DOWN) for m in mts], lag_ratio=.15), FadeIn(ural), run_time=.6)
        self.play(FadeIn(p2, shift=DOWN * .3), FadeIn(p1, shift=DOWN * .3), run_time=.35)
        self.add(rglow)
        self.play(Create(rglow), Create(rdash), run_time=.7)
        self.play(FadeIn(p3, shift=DOWN * .3), FadeIn(note), run_time=.35)
        self.wait(.1)


# ======================= слайд 5 =======================
class S5(Diagram):
    VH = 470

    def construct(self):
        title = self.W(300, 36, "Возраст в 1864 году", 30)
        base = self.rrect(34, 394, 532, 5, 2.5).set_fill(WHITE, .55).set_stroke(width=0)
        data = [(80, "Старец", "одни источники", "sand"), (88, "Старец", "другие источники", "rose"), (86, "Александр I", "род. в 1777 г.", "lilac")]
        bars, nums, labels = [], [], []
        for i, (val, n1, n2, c) in enumerate(data):
            x = 66 + i * 176; w = 116; h = val * 2.95; y = 390 - h
            bars.append(self.card(x, y, w, h, c, 18, 6))
            tracker = ValueTracker(0)
            ref = self.T(x + w / 2, y + 46, str(val), 36)
            num = always_redraw(lambda tr=tracker, r=ref: Text(str(int(round(tr.get_value()))), font=FONT, font_size=36 * K_FONT,
                                                               weight=BOLD, color=INK).move_to(r.get_center()))
            nums.append((tracker, val, num, ref))
            labels.append(VGroup(self.W(x + w / 2, 434, n1, 21), self.W(x + w / 2, 458, n2, 16, bold=False, opacity=.85)))
        self.play(Write(title), GrowFromEdge(base, LEFT), run_time=.5)
        self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=.25), run_time=1.0, rate_func=rate_functions.ease_out_back)
        for tr, val, num, ref in nums:
            self.add(num)
        self.play(*[tr.animate.set_value(val) for tr, val, _, _ in nums], LaggedStart(*[FadeIn(l, shift=UP * .2) for l in labels], lag_ratio=.2), run_time=.8)
        for tr, val, num, ref in nums:   # финальные числа — тем же шрифтом, что подписи
            num.clear_updaters(); self.remove(num); self.add(ref)
        self.wait(.1)


# ======================= слайд 6 =======================
class S6(Diagram):
    VH = 486

    def construct(self):
        metal = ["#c9d1da", "#ffffff", "#aeb8c4"]
        title = self.W(300, 36, "Чаша весов", 30)
        foot = self.rrect(214, 402, 172, 24, 12).set_fill(metal, 1).set_sheen_direction(RIGHT).set_stroke(width=0)
        pole = self.rrect(290, 112, 20, 296, 10).set_fill(metal, 1).set_sheen_direction(RIGHT).set_stroke(width=0)
        beam_parts = VGroup(self.rrect(86, 100, 428, 12, 6).set_fill(["#f6f8fb", "#8994a3"], 1).set_sheen_direction(DOWN).set_stroke(width=0))
        pans = VGroup()
        for cx, n in ((134, "sage"), (466, "rose")):
            l, b, d = PAL[n]
            strings = VGroup(self.line((cx, 110), (cx - 58, 232), WHITE, 2, .8), self.line((cx, 110), (cx + 58, 232), WHITE, 2, .8))
            bowl = VMobject().set_points_smoothly([self.P(cx - 66, 232), self.P(cx - 50, 274), self.P(cx, 288), self.P(cx + 50, 274), self.P(cx + 66, 232)])
            bowl.add_line_to(self.P(cx - 66, 232)).set_fill([l, b], 1).set_sheen_direction(DOWN).set_stroke(d, 1.5)
            rim = Ellipse(width=132 * U, height=22 * U).set_fill(l, 1).set_stroke(d, 1.5).move_to(self.P(cx, 232))
            pans.add(VGroup(strings, bowl, rim))
        hub = self.orb(300, 106, 15)
        beam = VGroup(beam_parts, pans)
        cubes_for = VGroup(self.card(104, 200, 28, 26, "sky", 7, 3), self.card(136, 200, 28, 26, "sand", 7, 3), self.card(120, 172, 28, 26, "lilac", 7, 3))
        cube_against = self.card(452, 200, 28, 26, "rose", 7, 3)
        lab = VGroup(self.W(134, 326, "ЗА", 27), self.W(134, 352, "3 мнения,", 18, bold=False), self.W(134, 374, "косвенные признаки", 18, bold=False),
                     self.W(466, 326, "ПРОТИВ", 27), self.W(466, 352, "нет документов", 18, bold=False), self.W(466, 374, "о подмене", 18, bold=False))
        verdict = self.W(300, 470, "Спор не закончен", 24)

        self.play(Write(title), GrowFromEdge(foot, DOWN), run_time=.4)
        self.play(GrowFromEdge(pole, DOWN), run_time=.35)
        for m in (beam, cubes_for, cube_against):            # всё на коромысле наклонено вместе
            m.rotate(-.22, about_point=self.P(300, 106))
        self.play(FadeIn(beam), FadeIn(hub), run_time=.3)
        self.play(LaggedStart(*[FadeIn(c, shift=DOWN * .6) for c in cubes_for], lag_ratio=.25), FadeIn(cube_against, shift=DOWN * .6),
                  run_time=.6)
        # чаша качается и приходит в равновесие: спор не решён
        self.play(Rotate(VGroup(beam, cubes_for, cube_against), .30, about_point=self.P(300, 106)), run_time=.35)
        self.play(Rotate(VGroup(beam, cubes_for, cube_against), -.08, about_point=self.P(300, 106)), run_time=.3, rate_func=smooth)
        self.play(FadeIn(lab, shift=UP * .15), Write(verdict), run_time=.5)
        self.wait(.1)


# ======================= слайд 7 =======================
class S7(Diagram):
    VH = 520

    def construct(self):
        cols = ["lilac", "sky", "sage", "sand"]
        steps = [("Характер царя", "усталость, вина, вера"), ("Легенда о Сибири", "внезапная смерть, старец"),
                 ("Нет документов", "только косвенные признаки"), ("Спор продолжается", "тайна не разгадана")]
        anims = []
        for i, ((h1, h2), c) in enumerate(zip(steps, cols)):
            y = 24 + i * 126
            card = VGroup(self.card(80, y, 440, 82, c, 22, 6), self.T(300, y + 38, h1, 26), self.T(300, y + 64, h2, 18, False, INK2))
            anims.append(FadeIn(card, shift=DOWN * .35, scale=.95))
            if i < 3:
                ay = y + 96
                arrow = VMobject().set_points_as_corners([self.P(286, ay), self.P(300, ay + 16), self.P(314, ay)]).set_stroke(WHITE, 4)
                anims.append(Create(arrow))
        self.play(LaggedStart(*anims, lag_ratio=.32), run_time=2.0)
        self.wait(.1)


SCENES = {2: (S2, 470), 3: (S3, 490), 4: (S4, 455), 5: (S5, 470), 6: (S6, 486), 7: (S7, 520)}
