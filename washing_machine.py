import asyncio
from os import getenv
from dotenv import load_dotenv
from aiogram import Dispatcher,types,F,Bot
from aiogram.types import Message,CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup



load_dotenv()



class Washing(StatesGroup):
    washing_time=State()
    temperature=State()
    clothes=State()
    squeezing_turnovers=State()



gifs={"temperature_too_high":"https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExMHd5ZmVzczhoYmdyOGs5bDgycTJnaWcyaDF1YWhzb3NicnRicGxsbyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/eZ2fk4Z0bKWQ0/giphy.mp4",
      "machine_1":"https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExaHN6NjhscmVlaWlleGFzbWJpM3doZGN4bXB6czZyaW9lNW52MzN5ZiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/l2QZUkF4YilI5fO6I/giphy.mp4",
      "machine_2":"https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExZHV1Z3JtY3h1Ync3amprYmllN3Z0cWY1NGp6OGJyNm44bWFreXVheCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/31UNKTJhlCatTPSfeh/giphy.mp4",
      "temperature_too_low":"https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExemY4Z3d4YWt2ZHV4ZDlidnd2dmtmNWJicTc4bHk5NGFxOWNscjhmaiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/s4Bi420mMDRBK/giphy.mp4"}



dp = Dispatcher()
bot= Bot(token=getenv("BOT_TOKEN"))



async def washing_machine(query:CallbackQuery,clothes,washing_time,squeezing_turnovers,temperature,state):
    half_time=int(washing_time) / 2
    if int(temperature)>90:
        await query.message.answer("The temperature is too high\nmax:90")
        await query.message.answer_animation(gifs.get("temperature_too_high"))
        await state.clear()

    elif int(temperature)<30:
        await query.message.answer("The temperature is too low\nmin:30")
        await query.message.answer_animation(gifs.get("temperature_too_low"))
        await state.clear()

    else:
        await query.message.answer(f"Starting to wash:{clothes}")
        await query.message.answer_animation(gifs.get("machine_1"))
        await asyncio.sleep(half_time)
        await query.message.answer("Half way through")
        await asyncio.sleep(half_time)
        await query.message.answer("Done washing\nStarting to squeeze")
        await query.message.answer_animation(gifs.get("machine_2"))

        if int(squeezing_turnovers)>500:
            await asyncio.sleep(10)
            await query.message.answer(f"Done squeezing\nYour clothes:{clothes} are washed and are dry")
            await state.clear()

        else:
            await asyncio.sleep(5)
            await query.message.answer(f"Done squeezing\nYour clothes:{clothes} are washed and are half-dry")
            await state.clear()
        
            

@dp.message(Command("start"))
async def washing_clothes(message:Message):
    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Try it out", callback_data="try")]
        ])
    await message.answer("Welcome to washing machine simulator\nTry the simulator out!",reply_markup=kb)



@dp.callback_query(F.data.startswith("try"))
async def open_door(query:CallbackQuery):
    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Open the door", callback_data="open")]
        ])
    await query.message.answer("Open the door:",reply_markup=kb)



@dp.callback_query(F.data.startswith("open"))
async def putting_in(query:CallbackQuery,state:FSMContext):
    await query.message.answer("Now put the clothes in:\n(write them down)")
    await state.set_state(Washing.clothes)



@dp.message(Washing.clothes)
async def clothes(message:Message,state:FSMContext):
    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Close the door", callback_data="close")]
        ])
    clothes = message.text
    await state.update_data(clothes=clothes)
    await message.answer("Now close the door:",reply_markup=kb)



@dp.callback_query(F.data.startswith("close"))
async def close_door(query:CallbackQuery,state:FSMContext):
    await query.message.answer("Now set the temperature:\nmin:30 - max:90")
    await state.set_state(Washing.temperature)



@dp.message(Washing.temperature)
async def temperature(message:Message,state:FSMContext):
    temperature = message.text
    await state.update_data(temperature=temperature)
    await message.answer("Now set the time to wash:")
    await state.set_state(Washing.washing_time)



@dp.message(Washing.washing_time)
async def washing_time(message:Message,state:FSMContext):
    time = message.text
    await state.update_data(washing_time=time)
    await message.answer("Now set the number of turnovers to squeeze:")
    await state.set_state(Washing.squeezing_turnovers)



@dp.message(Washing.squeezing_turnovers)
async def squeezing_turnovers(message:Message,state:FSMContext):
    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Start Washing", callback_data="start")]
        ])
    turnovers = message.text
    await state.update_data(squeezing_turnovers=turnovers)
    await message.answer("Now press start:",reply_markup=kb)



@dp.callback_query(F.data.startswith("start"))
async def start(query:CallbackQuery,state:FSMContext):
    data = await state.get_data()
    turnovers = data.get("squeezing_turnovers")
    temperature = data.get("temperature")
    time = data.get("washing_time")
    clothes = data.get("clothes")
    return await washing_machine(clothes=clothes,washing_time=time,squeezing_turnovers=turnovers,temperature=temperature,query=query,state=state)
    


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())