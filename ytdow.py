from hikkatl.types import Message  
from .. import loader, utils  
import yt_dlp  
import re  

@loader.tds  
class YTDownloaderMod(loader.Module):  
    """Скачать видео/аудио с YouTube"""  

    strings = {  
        "name": "YTDownloader",  
        "args_err": "❌ Укажите ссылку на YouTube! Пример: <code>.yt https://youtu.be/...</code>",  
        "downloading": "⬇️ Скачиваю...",  
        "error": "❌ Ошибка при скачивании. Проверь ссылку или попробуй позже.",  
    }  

    async def ytcmd(self, message: Message):  
        """<ссылка> [качество] — скачать видео (или аудио)"""  
        args = utils.get_args_raw(message)  
        if not args:  
            await utils.answer(message, self.strings["args_err"])  
            return  

        # Проверяем, что это ссылка на YouTube  
        if not re.match(r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+", args):  
            await utils.answer(message, "❌ Это не ссылка на YouTube!")  
            return  

        await utils.answer(message, self.strings["downloading"])  

        try:  
            ydl_opts = {  
                "format": "best",  # Лучшее качество (можно изменить на 'bestaudio' для аудио)  
                "outtmpl": "downloads/%(title)s.%(ext)s",  
                "quiet": True,  
            }  

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:  
                info = ydl.extract_info(args, download=True)  
                filename = ydl.prepare_filename(info)  

            await message.client.send_file(  
                message.peer_id,  
                file=filename,  
                caption=f"🎬 {info['title']}",  
            )  

        except Exception as e:  
            await utils.answer(message, f"{self.strings['error']}\nОшибка: {str(e)}")   