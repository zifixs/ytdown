import io
import random
from datetime import datetime
from textwrap import fill

from hikkatl.types import Message
from .. import loader, utils
from PIL import Image, ImageDraw, ImageFont

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

        # Парсим аргументы
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
        # Создаем изображение
        img = Image.new("RGB", (400, 300), (32, 44, 61))
        draw = ImageDraw.Draw(img)
        
        # Используем встроенный шрифт (если системные не работают)
        try:
            font = ImageFont.truetype("arial.ttf", 14)
        except:
            font = ImageFont.load_default()
        
        # Аватарка (простой круг)
        avatar_size = 30
        draw.ellipse((20, 20, 20+avatar_size, 20+avatar_size), fill=(70, 130, 200))
        
        # Имя и время
        draw.text((60, 20), user_name, font=font, fill=(255, 255, 255))
        draw.text((200, 22), datetime.now().strftime("%H:%M"), font=font, fill=(150, 150, 150))
        
        # Ответ (если есть)
        y_offset = 50
        if reply_text:
            draw.rectangle((60, y_offset, 360, y_offset + 40), fill=(70, 70, 70))
            draw.text((65, y_offset + 5), fill(reply_text, width=40), font=font)
            y_offset += 50
        
        # Текст сообщения
        for line in fill(text, width=40).split("\n"):
            draw.text((60, y_offset), line, font=font, fill=(255, 255, 255))
            y_offset += 20
        
        return img
