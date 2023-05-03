import os, re, configparser, pafy
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.utils import executor
from aiogram.utils.helper import Helper, HelperMode, ListItem
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, \
    InlineKeyboardButton
from keyboard import menu, back, make_keyboards

config = configparser.ConfigParser()
config.read("settings.ini")
TOKEN = config["tgbot"]["token"]

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


def get_title(url):
    yVideo = pafy.new(url)
    title = yVideo.title
    return title


def get_author(url):
    yVideo = pafy.new(url)
    author = yVideo.author
    return author


def get_url(call):
    url = call.split('|')
    video_url = url[1]
    return video_url


def get_download_url_with_audio(url_video):
    yVideo = pafy.new(url_video)
    video = yVideo.getbest()
    return video.url_https


def get_download_url_best_video(url_video):
    yVideo = pafy.new(url_video)
    video = yVideo.getbestvideo()
    return video.url_https


def get_download_url_best_audio(url_video):
    yVideo = pafy.new(url_video)
    video = yVideo.getbestaudio()
    return video.url_https


class Info(StatesGroup):
    video = State()


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await bot.send_message(chat_id=message.chat.id, text=' Привет, я помогу тебе скачать видео с YouTube.',
                           reply_markup=menu())


@dp.message_handler(text="Скачать")
async def save_video(message: types.Message):
    await bot.send_message(chat_id=message.chat.id, text=' Введи ссылку на видео: ', reply_markup=back())
    await Info.video.set()


@dp.message_handler(state=Info.video, content_types=types.ContentTypes.TEXT)
async def edit_name(message: types.Message, state: FSMContext):
    if message.text.lower() == 'отмена':
        await bot.send_message(chat_id=message.chat.id, text='Ты вернулся в главное меню.', reply_markup=menu())
        await state.finish()
    else:
        if message.text.startswith('https://www.youtube.com/watch?v='):
            try:
                video_url = message.text
                await bot.send_message(chat_id=message.chat.id,
                                       text=f'Название видео: {get_title(video_url)}\nАвтор: {get_author(video_url)}\n\nВыберите качество загрузки:',
                                       reply_markup=make_keyboards(video_url))
                await state.finish()
            except OSError:
                await bot.send_message(chat_id=message.chat.id,
                                       text=f'Ссылка неверная, либо видео не найдено. Введи ссылку в формате: ```https://www.youtube.com/watch?v=...```',
                                       reply_markup=back(), parse_mode="Markdown")
            except ValueError:
                await bot.send_message(chat_id=message.chat.id,
                                       text=f'Ссылка неверная, либо видео не найдено. Введи ссылку в формате: ```https://www.youtube.com/watch?v=...```',
                                       reply_markup=back(), parse_mode="Markdown")
        else:
            await bot.send_message(chat_id=message.chat.id,
                                   text=f'Введи ссылку в формате: ```https://www.youtube.com/watch?v=...```',
                                   reply_markup=back(), parse_mode="Markdown")


@dp.callback_query_handler()
async def handler_call(call: types.CallbackQuery, state: FSMContext):
    chat_id = call.from_user.id
    if call.data.startswith('best_with_audio'):
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        video_url = get_url(call.data)
        download_link = get_download_url_with_audio(video_url)
        await bot.send_message(chat_id=chat_id, text=f' Вот ваша ссылка на скачивание видео: {download_link}',
                               reply_markup=menu())
    elif call.data.startswith('best_video'):
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        video_url = get_url(call.data)
        download_link = get_download_url_best_video(video_url)
        await bot.send_message(chat_id=chat_id, text=f' Вот ваша ссылка на скачивание видео: {download_link}',
                               reply_markup=menu())
    elif call.data.startswith('best_audio'):
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        video_url = get_url(call.data)
        download_link = get_download_url_best_audio(video_url)
        await bot.send_message(chat_id=chat_id, text=f' Вот ваша ссылка на скачивание аудио: {download_link}',
                               reply_markup=menu())
    elif call.data == 'cancel':
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        await bot.send_message(chat_id=chat_id, text='Ты вернулся в главное меню.', reply_markup=menu())


if __name__ == "__main__":
    # Запускаем бота
    executor.start_polling(dp, skip_updates=True)
