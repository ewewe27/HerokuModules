# meta developer: @Modules_iwwushka
# meta author: @iwwushka
# meta version: 1.0.0

from hikkatl.types import Message
from .. import loader, utils
import io
import requests

@loader.tds
class UploaderMod(loader.Module): 
    """Module for uploading files to envs.sh"""

    strings = {
        'name': 'Uploader',
        'uploading': 'Uploader for envs.sh',
        'reply_to_file': 'Reply to a file to upload it',
        'uploaded': 'File uploaded to envs.sh\n\n URL: <code>{}</code>',
        'error': 'Error: <code>{}</code>',
    }

    async def _get_file(self, message: Message):
        """Getting a file from a message"""
        reply = await message.get_reply_message()
        if not reply:
            await utils.answer(message, self.strings("reply_to_file"))
            return None
        
        if reply.media:
            
            file_bytes = await self.client.download_media(reply.media, bytes)
            file = io.BytesIO(file_bytes)

            if hasattr(reply.media, 'document') and reply.media.document:
                for attr in reply.media.document.attributes:
                    if hasattr(attr, 'file_name'):
                        file.name = attr.file_name
                        break
                else:
                    file.name = f"photo_{reply.id}"
            else:
                file.name = f"photo_{reply.id}.jpg"
        else:
            file = io.BytesIO(bytes(reply.text, 'utf-8'))
            file.name = "text.txt"

        file.seek(0)
        return file
    
    async def envscmd(self, message: Message):
        """Upload file to envs.sh"""
        await utils.answer(message, self.strings("uploading"))
        file = await self._get_file(message)
        if not file:
            return
        
        try:
            files = {"file": (file.name, file)}

            response = requests.post("https://envs.sh", files=files)

            if response.status_code == 200:
                url = response.text.strip()
                await utils.answer(message, self.strings("uploaded").format(url))
            else:
                await utils.answer(message, self.strings("error").format(f"HTTP {response.status_code}"))
        except Exception as e:
            await utils.answer(message, self.strings("error").format(str(e)))