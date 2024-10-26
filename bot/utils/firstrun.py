from bot.config import settings
import aiofiles


def load_session_names():
    with open(settings.IN_USE_SESSIONS_PATH, 'a') as file:
        pass

    # Open file for both reading and writing, create if it doesn't exist
    with open(settings.IN_USE_SESSIONS_PATH, 'r') as file:
        lines_list = file.readlines()

    return [line.strip() for line in lines_list]

async def append_line_to_file(line):
    async with aiofiles.open(settings.IN_USE_SESSIONS_PATH, 'a') as file:
        await file.write(line + '\n')
