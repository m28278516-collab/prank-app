"""
ПРАНК-ПРИЛОЖЕНИЕ (Android) — v2.1 CHAOS FIXED
20 секунд разных ошибок, потом кнопка «прости». Не нажал — ошибки продолжаются.
"""
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.core.audio import SoundLoader
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window
from kivy.utils import platform
from kivy.animation import Animation
import random

# --- Вибрация (только Android) ---
vibrator = None
if platform == 'android':
    try:
        from jnius import autoclass, cast
        Context = autoclass('android.content.Context')
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        activity = PythonActivity.mActivity
        vibrator = cast('android.os.Vibrator',
                        activity.getSystemService(Context.VIBRATOR_SERVICE))
    except Exception as e:
        print("Vibrator init error:", e)

VIBRO_PATTERN = [0, 500, 200, 500, 200, 500, 200, 500, 200,
                 500, 200, 500, 200, 500, 200, 500]

# ---- СПИСОК ОШИБОК ----
ERRORS = [
    ("CRITICAL ERROR",     "0x80070005\nДоступ запрещён системой"),
    ("SYSTEM FAILURE",     "Ядро перегрето\n88°C / 100°C"),
    ("DATA CORRUPTION",    "Потеряно 4.7 ГБ данных\nВосстановление невозможно"),
    ("NETWORK BREACH",     "Неизвестный IP\n192.168.x.x"),
    ("BATTERY CRITICAL",   "Утечка заряда\n-18% за секунду"),
    ("MEMORY LEAK",        "Заполнено 99.7% ОЗУ\nЗамедление 40x"),
    ("SECURITY ALERT",     "Вирус-шифровальщик\nЗашифровано 1247 файлов"),
    ("KERNEL PANIC",       "STOP: 0x0000007B\nСистема перезагружается"),
    ("GPS BREACH",         "Ваше местоположение\nпередано 47 разам"),
    ("CAMERA ACCESS",      "Фронтальная камера\nактивирована удалённо"),
    ("MIC ACCESS",         "Идёт запись звука\nФайл: voice_0884.wav"),
    ("APPLICATION CRASH",  "android.app.process\nне отвечает"),
    ("STORAGE FULL",       "Диск C: заполнен\nОсталось 0 байт"),
    ("UPDATE FAILED",      "Не удалось обновить\nядро Android 14"),
    ("SIM CARD ERROR",     "SIM не обнаружена\nПопытка обхода: 12/999"),
    ("CIA BACKDOOR",       "Агент 0x7A активен\nЗагрузка данных..."),
    ("FACE RECOGNITION",   "Совпадение 87%\nЛицо не распознано"),
    ("BANKING TROJAN",     "Банковский троян\nзапущен в фоне"),
    ("ROOT ACCESS DENIED", "Попытка root\nзаблокирована"),
    ("FIREWALL DOWN",      "Брандмауэр отключён\nПортов открыто: 65535"),
    ("SYSTEM RESTORE",     "Откат системы\nДо версии 1970 года"),
    ("OVERHEAT",           "CPU: 118°C\nGPU: 121°C"),
    ("DISK FAILURE",       "SMART-тест провален\nSSD не отвечает"),
    ("CLOCK RESET",        "Системное время\nсброшено на 01.01.1970"),
]


class PrankLayout(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Красный фон — ВАЖНО: храним ссылку на Color, а не только на Rectangle
        with self.canvas.before:
            self.bg_color = Color(0.6, 0.0, 0.0, 1)
            self.bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._upd, size=self._upd)

        # Заголовок
        self.title = Label(
            text='[ СИСТЕМА ВЗЛОМАНА ]',
            font_size='28sp',
            bold=True,
            color=(1, 1, 1, 1),
            pos_hint={'center_x': 0.5, 'top': 0.97},
            size_hint=(1, 0.10),
        )
        self.add_widget(self.title)

        # Название ошибки
        self.err_title = Label(
            text='КРИТИЧЕСКАЯ ОШИБКА',
            font_size='30sp',
            bold=True,
            color=(1, 1, 0, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.72},
            size_hint=(1, 0.15),
        )
        self.add_widget(self.err_title)

        # Описание ошибки
        self.err_msg = Label(
            text='...',
            font_size='20sp',
            halign='center',
            valign='middle',
            color=(1, 1, 1, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.48},
            size_hint=(0.9, 0.30),
        )
        self.err_msg.bind(size=lambda *_: setattr(self.err_msg, 'text_size', self.err_msg.size))
        self.add_widget(self.err_msg)

        # Строка прогресса
        self.progress = Label(
            text='Взлом: 0%',
            font_size='22sp',
            color=(0, 1, 0, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.25},
            size_hint=(1, 0.08),
        )
        self.add_widget(self.progress)

        # Кнопка «прости» (скрыта до 20 сек)
        self.forgive_btn = Button(
            text='Это была шутка, прости 😄',
            font_size='18sp',
            size_hint=(0.8, 0.09),
            pos_hint={'center_x': 0.5, 'y': 0.05},
            background_color=(0, 0.6, 0, 1),
            opacity=0,
            disabled=True,
        )
        self.forgive_btn.bind(on_press=self.stop_prank)
        self.add_widget(self.forgive_btn)

        # === ЗАПУСК ===
        self.progress_val = 0

        Clock.schedule_once(self.start_sound, 0.3)
        Clock.schedule_once(self.start_vibro, 0.5)
        Clock.schedule_interval(self.next_error, 0.7)
        Clock.schedule_interval(self.tick, 0.1)
        Clock.schedule_once(self.show_forgive, 20.0)

    def _upd(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size

    def next_error(self, dt):
        """Меняем ошибку + вспышка фона"""
        title, msg = random.choice(ERRORS)
        self.err_title.text = title
        self.err_msg.text = msg
        self.err_title.color = random.choice([
            (1, 1, 0, 1), (1, 0.3, 0.3, 1), (1, 0.6, 0, 1)
        ])
        # Вспышка фона — меняем у Color, не у Rectangle
        self.bg_color.rgba = (1, 0.3, 0.3, 1)
        Animation(rgba=(0.6, 0.0, 0.0, 1), d=0.4).start(self.bg_color)

    def tick(self, dt):
        """Прогресс и мигание заголовка"""
        if self.progress_val < 100:
            self.progress_val += random.uniform(0.3, 1.5)
            if self.progress_val > 100:
                self.progress_val = 99.9
        self.progress.text = f'Взлом: {self.progress_val:.1f}%'

        # Мигание заголовка
        if random.random() < 0.15:
            self.title.color = (1, 1, 1, 1) if self.title.color[0] < 0.7 else (1, 0.5, 0.5, 1)

    def show_forgive(self, dt):
        self.forgive_btn.opacity = 1
        self.forgive_btn.disabled = False

    def start_sound(self, dt):
        self.sound = SoundLoader.load('sound.wav')
        if self.sound:
            self.sound.loop = True
            self.sound.play()

    def start_vibro(self, dt):
        if vibrator is not None:
            try:
                from jnius import autoclass
                LongArray = autoclass('[J')
                pattern = LongArray(len(VIBRO_PATTERN))
                for i, v in enumerate(VIBRO_PATTERN):
                    pattern[i] = v
                vibrator.vibrate(pattern, 0)
            except Exception as e:
                print("Vibro error:", e)

    def stop_prank(self, *args):
        if hasattr(self, 'sound') and self.sound:
            self.sound.stop()
        if vibrator is not None:
            try:
                vibrator.cancel()
            except Exception:
                pass
        App.get_running_app().stop()


class PrankApp(App):
    def build(self):
        # Для отладки на Windows — окно как телефон
        if platform == 'win':
            Window.size = (400, 800)
        else:
            Window.fullscreen = 'auto'
        return PrankLayout()


if __name__ == '__main__':
    PrankApp().run()