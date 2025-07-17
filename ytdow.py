import io
import random
from datetime import datetime
from textwrap import fill

from hikkatl.types import Message
from .. import loader, utils
from PIL import Image, ImageDraw, ImageFont

# Стиль оформления скриншота (цвета, шрифты)
FONT_PATH = "arial.ttf"  # Укажи путь к шрифту (или оставь стандартный)
BG_COLOR = (32, 44, 61)  # Цвет фона (как в Telegram)
TEXT_COLOR = (255, 255, 255)  # Цвет текста
TIME_COLOR = (150, 150, 150)  # Цвет времени
REPLY_COLOR = (70, 70, 70)  # Цвет плашки "ответа"

@loader.tds
class FakeScreenshotsMod(loader.Module):
    """Создает фейковые скриншоты переписки"""
    
    strings = {
        "name": "FakeScreenshots",
        "args_err": "❌ Укажите текст! Пример: <code>.fakess Привет, как дела?</code>",
        "generating": "🖼 Генерирую скриншот...",
    }

    async def fakesscmd(self, message: Message):
        """<текст> [--reply=ответ] [--user=имя] — создать фейковый скриншот"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings["args_err"])
            return

        # Парсим аргументы (--reply, --user)
        reply_text = None
        user_name = "Изгой"
        if "--reply=" in args:
            args, reply_text = args.split("--reply=", 1)
            reply_text = reply_text.split("--user=")[0].strip()
        if "--user=" in args:
            args, user_name = args.split("--user=", 1)
            user_name = user_name.strip()
        
        await utils.answer(message, self.strings["generating"])

        # Генерируем скриншот
        img = await self.generate_screenshot(
            text=args.strip(),
            reply_text=reply_text,
            user_name=user_name,
        )
        
        # Отправляем результат
        output = io.BytesIO()
        img.save(output, format="PNG")
        output.seek(0)
        await message.client.send_file(
            message.peer_id,
            file=output,
            caption="📸 Вот твой фейковый скриншот!",
        )

    async def generate_screenshot(
        self,
        text: str,
        user_name: str = "Изгой",
        reply_text: str = None,
    ) -> Image.Image:
        """Генерация изображения"""
        # Создаем "телеграммовский" фон
        img = Image.new("RGB", (400, 300), BG_COLOR)
        draw = ImageDraw.Draw(img)
        
        # Шрифты
        font = ImageFont.truetype(FONT_PATH, 14)
        small_font = ImageFont.truetype(FONT_PATH, 11)
        bold_font = ImageFont.truetype(FONT_PATH, 14)  # Для имени
        
        # Аватарка (круглая миниатюра)
        avatar_size = 30
        avatar = Image.new("RGB", (avatar_size, avatar_size), (50, 150, 220))
        draw_avatar = ImageDraw.Draw(avatar)
        draw_avatar.ellipse((0, 0, avatar_size, avatar_size), fill=(70, 130, 200))
        
        # Вставляем аватар
        img.paste(avatar, (20, 20))
        
        # Имя пользователя и время
        draw.text((60, 20), user_name, font=bold_font, fill=TEXT_COLOR)
        time_str = datetime.now().strftime("%H:%M")
        draw.text((60 + bold_font.getlength(user_name) + 10, 22), 
                 time_str, font=small_font, fill=TIME_COLOR)
        
        # Плашка "ответа" (если есть)
        y_offset = 50
        if reply_text:
            reply_width = 300
            reply_height = 40
            draw.rounded_rectangle(
                (60, y_offset, 60 + reply_width, y_offset + reply_height),
                radius=5,
                fill=REPLY_COLOR,
            )
            draw.text(
                (65, y_offset + 5),
                fill(reply_text, width=40),
                font=small_font,
                fill=TEXT_COLOR,
            )
            y_offset += reply_height + 10
        
        # Основной текст сообщения
        text_lines = fill(text, width=40).split("\n")
        for line in text_lines:
            draw.text((60, y_offset), line, font=font, fill=TEXT_COLOR)
            y_offset += 20
        
        return img
