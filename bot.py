
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from datetime import datetime

API_TOKEN = '7861693671:AAEyzNuFC72PWJLqHFycNTJyODYHG70VMq8'
YOUR_ADMIN_ID = 302435472

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

users = {}
shifts = {}
plans = {}
results = {}

main_kb = ReplyKeyboardMarkup(resize_keyboard=True)
main_kb.add(KeyboardButton("🕒 Начать смену"))
main_kb.add(KeyboardButton("✅ Закончить смену"))
main_kb.add(KeyboardButton("📊 Отчёт"))
main_kb.add(KeyboardButton("📌 План на день"))
main_kb.add(KeyboardButton("📈 Отчитаться"))

admin_kb = ReplyKeyboardMarkup(resize_keyboard=True)
admin_kb.add(KeyboardButton("📌 Обновить план"))
admin_kb.add(KeyboardButton("📋 Все отчёты"))
admin_kb.add(KeyboardButton("📅 Все смены"))
admin_kb.add(KeyboardButton("⬅ Назад"))

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    user_id = message.from_user.id
    users[user_id] = message.from_user.full_name
    if user_id == YOUR_ADMIN_ID:
        await message.reply("Добро пожаловать в админ-панель.", reply_markup=admin_kb)
    else:
        await message.reply(f"Привет, {message.from_user.full_name}! Я бот для учёта смен и заданий. Используй кнопки ниже:", reply_markup=main_kb)

@dp.message_handler(lambda msg: msg.text == "🕒 Начать смену")
async def start_shift(message: types.Message):
    user_id = message.from_user.id
    if user_id not in shifts or shifts[user_id]['end'] is not None:
        shifts[user_id] = {'start': datetime.now(), 'end': None}
        await message.reply("Смена началась ✅")
    else:
        await message.reply("У тебя уже есть активная смена!")

@dp.message_handler(lambda msg: msg.text == "✅ Закончить смену")
async def end_shift(message: types.Message):
    user_id = message.from_user.id
    if user_id in shifts and shifts[user_id]['end'] is None:
        shifts[user_id]['end'] = datetime.now()
        duration = shifts[user_id]['end'] - shifts[user_id]['start']
        await message.reply(f"Смена завершена. Продолжительность: {duration}")
    else:
        await message.reply("Нет активной смены, которую можно завершить.")

@dp.message_handler(lambda msg: msg.text == "📊 Отчёт")
async def report(message: types.Message):
    user_id = message.from_user.id
    if user_id in shifts:
        shift = shifts[user_id]
        start = shift['start'].strftime('%Y-%m-%d %H:%M') if shift['start'] else '—'
        end = shift['end'].strftime('%Y-%m-%d %H:%M') if shift['end'] else '—'
        result = results.get(user_id, 'Не отчитался')
        plan = plans.get(user_id, 'Нет плана')
        await message.reply(f"Текущая смена:\nНачало: {start}\nКонец: {end}\nПлан: {plan}\nОтчёт: {result}")
    else:
        await message.reply("Данных о сменах нет.")

@dp.message_handler(lambda msg: msg.text == "📌 План на день")
async def set_plan(message: types.Message):
    if message.from_user.id == YOUR_ADMIN_ID:
        await message.reply("Для изменения плана используй '📌 Обновить план' из админ-панели.")
    else:
        plan = plans.get(message.from_user.id, 'Нет плана на день.')
        await message.reply(f"Твой план на сегодня:\n{plan}")

@dp.message_handler(lambda msg: msg.text == "📈 Отчитаться")
async def get_report(message: types.Message):
    await message.reply("Напиши, что и сколько ты выполнил за смену")
    @dp.message_handler()
    async def save_report(msg: types.Message):
        results[msg.from_user.id] = msg.text
        await msg.reply("Отчёт принят. Спасибо!")

@dp.message_handler(lambda msg: msg.text == "📌 Обновить план")
async def admin_plan_update(message: types.Message):
    if message.from_user.id == YOUR_ADMIN_ID:
        await message.reply("Напиши новый план для всех сотрудников:")
        @dp.message_handler()
        async def save_plan(msg: types.Message):
            for uid in users:
                plans[uid] = msg.text
            await msg.reply("План обновлён для всех сотрудников.")

@dp.message_handler(lambda msg: msg.text == "📋 Все отчёты")
async def all_reports(message: types.Message):
    if message.from_user.id == YOUR_ADMIN_ID:
        text = "📝 Отчёты сотрудников:\n"
        for uid, report in results.items():
            name = users.get(uid, 'Без имени')
            text += f"\n{name}: {report}"
        await message.reply(text or "Отчётов нет.")

@dp.message_handler(lambda msg: msg.text == "📅 Все смены")
async def all_shifts(message: types.Message):
    if message.from_user.id == YOUR_ADMIN_ID:
        text = "📅 Смены сотрудников:\n"
        for uid, shift in shifts.items():
            name = users.get(uid, 'Без имени')
            start = shift['start'].strftime('%Y-%m-%d %H:%M') if shift['start'] else '—'
            end = shift['end'].strftime('%Y-%m-%d %H:%M') if shift['end'] else '—'
            text += f"\n{name}: {start} — {end}"
        await message.reply(text or "Смен нет.")

@dp.message_handler(lambda msg: msg.text == "⬅ Назад")
async def back_to_main(message: types.Message):
    if message.from_user.id == YOUR_ADMIN_ID:
        await message.reply("Возврат к главному меню.", reply_markup=main_kb)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp, skip_updates=True)
