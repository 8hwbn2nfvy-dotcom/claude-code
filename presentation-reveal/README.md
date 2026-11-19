# «Император и старец» — версия на reveal.js + GSAP + three.js + Manim

Та же презентация, что и `../presentation/index.html` (8 слайдов, фото яблони, падающее яблоко, камера, текст вылетает из яблока), пересобранная на четырёх библиотеках. Результат — **один HTML-файл**, работает офлайн и с флешки.

Готовый файл: `dist/Prezentaciya_Aleksandr_I.html` (≈ 8,3 МБ). Архив для флешки с инструкцией собирается рядом: `dist/Prezentaciya_Aleksandr_I.zip`.

## Кто за что отвечает

| Библиотека | Версия | Роль |
|---|---|---|
| [reveal.js](https://github.com/hakimel/reveal.js) | 5.1.0 | Слайды, клавиатура, пульт (PageUp/PageDown), свайпы, клавиша F (полный экран), B (чёрный экран). Свою раскладку reveal.js не считает (`disableLayout`), переходы — короткое затухание. |
| [GSAP](https://github.com/greensock/GSAP) | 3.12.5 | Таймлайн падения яблока (раскачивание, рывок, свободное падение `power2.in`, сплющивание, два отскока), вылет текста из яблока, общий тикер кадра. |
| [three.js](https://github.com/mrdoob/three.js) | r160 | Объёмное яблоко: `LatheGeometry`, `MeshPhysicalMaterial` с лаком, кожура из настоящего фото, черенок, лист, мягкая тень, шлейф. Если WebGL недоступен, показывается фото яблока. |
| [Manim Community](https://github.com/ManimCommunity/manim) | 0.19.0 | Схемы слайдов 2–7: плашки вырастают, линии прорисовываются, числа отсчитываются. Рендерятся заранее в анимированный WebP с прозрачностью и проигрываются, когда схема вылетает из яблока. |

## Структура

```
presentation-reveal/
├── package.json          # reveal.js, gsap, three
├── build.py              # сборка одного файла + zip
├── KAK_OTKRYT.txt        # инструкция для флешки (попадает в zip)
├── manim/
│   ├── diagrams.py       # сцены S2–S7
│   └── render.py         # рендер -> src/diagrams/sN.webp и sN_final.webp
├── tools/apple_skin.py   # текстура кожуры из фото яблока
├── src/
│   ├── template.html     # каркас страницы
│   ├── slides.html       # 8 секций reveal.js
│   ├── style.css
│   ├── app.js            # камера, яблоко (three.js), анимации (GSAP), связь с reveal.js
│   ├── assets/           # tree.webp, apple.webp, apple_skin.webp, apple_photo_source.jpg
│   └── diagrams/         # готовые анимации Manim
└── dist/                 # результат сборки
```

## Сборка

```bash
npm install
python3 -m venv .venv && .venv/bin/pip install manim==0.19.0   # нужен libpango1.0-dev и ffmpeg
.venv/bin/python manim/render.py      # ~2–3 минуты на схему; номера схем можно передать аргументами
python3 tools/apple_skin.py           # только если меняли фото яблока
python3 build.py
```

## Проверено

- Chromium 1600×900 и эмуляция iPad, страница внутри `iframe sandbox` (как в предпросмотре): нет ошибок, нет наложений и обрезанного текста, яблоко не заходит на слайд.
- Открытие из папки `ФЛЕШКА E/Мои документы` через `file://` при полностью заблокированной сети: все картинки загружены, внешних запросов 0.
- Три быстрых PageDown подряд дают ровно +3 слайда.
- С выключенным WebGL: фото-яблоко вместо 3D, ошибок нет.

## Лицензии

Фото: Wikimedia Commons, «Tree with red apples in Barkedal 2» и «Red apple with leaf», CC0. reveal.js, three.js, Manim — MIT. GSAP — стандартная бесплатная лицензия GreenSock. Тексты лицензий reveal.js, GSAP и three.js сохранены в заголовках встроенных файлов.
