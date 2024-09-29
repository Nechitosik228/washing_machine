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


dp = Dispatcher()
bot= Bot(token=getenv("BOT_TOKEN"))



async def washing_machine(message,clothes,washing_time,squeezing_turnovers,temperature):
    if int(temperature)>90:
        await message.answer("You have burnt your clothes,because the temperature is too high")
    else:
        await message.answer(f"Starting to wash:{clothes}")
        await asyncio.sleep(int(washing_time))
        await message.answer("Done washing\nStarting to squeeze")
        if int(squeezing_turnovers)>500:
            await asyncio.sleep(10)
            await message.answer(f"Your clothes:{clothes} are washed and are dry")
        else:
            await asyncio.sleep(5)
            await message.answer(f"Your clothes:{clothes} are washed and are half-dry")
        
            



@dp.message(Command("start"))
async def washing_clothes(message:Message):
    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Start the process", callback_data="start")]
        ])
    await message.answer("Welcome to washing machine simulator\nTry the simulator out!",reply_markup=kb)


@dp.callback_query(F.data.startswith("start"))
async def open_door(query:CallbackQuery):
    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Open the door", callback_data="open")]
        ])
    await query.message.answer("Open the door:",reply_markup=kb)


@dp.callback_query(F.data.startswith("open"))
async def open_door(query:CallbackQuery,state:FSMContext):
    await query.message.answer("Now put the clothes in:\n(write them down)")
    await state.set_state(Washing.clothes)


@dp.message(Washing.clothes)
async def clothes(message:Message,state:FSMContext):
    clothes = message.text
    await state.update_data(clothes=clothes)
    await message.answer("Now set the temperature:")
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
    turnovers = message.text
    data = await state.update_data(squeezing_turnovers=turnovers)
    temperature = data.get("temperature")
    time = data.get("washing_time")
    clothes = data.get("clothes")
    return await washing_machine(clothes=clothes,washing_time=time,squeezing_turnovers=turnovers,temperature=temperature,message=message)









async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())




