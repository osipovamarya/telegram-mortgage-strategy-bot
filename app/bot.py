import telebot
from app.utils import init_logging
# from app.telegram_user import TelegramUser
# from app.mortgage import Mortgage
from app.mortgage_registry import MortgageRegistry
from app.mortgage_count import MortgageCount
from collections import defaultdict
import logbook
import os

BOT_API_TOKEN = os.environ['MORST_BOT_API_TOKEN']
DB_PATH = os.environ['MORST_BOT_DB_PATH']

GREETING = '''
To start *MorstBot* use /default command.
This will add all parameters of mortgage and you could check if calculations is wright.

[MorstBot on GitHub](https://github.com/osipovamarya/telegram-mortgage-strategy-bot)
'''

bot = telebot.TeleBot(BOT_API_TOKEN)
mortgage_registry = MortgageRegistry()
current_count = defaultdict(str)
init_logging()


@bot.message_handler(commands=['start', 'help'])
def on_help_command(message):
    bot.send_message(message.chat.id, GREETING)


@bot.message_handler(commands=['default'])
def get_count_name(message):
    bot.send_message(message.chat.id, 'Давайте начнем расчет, следуйте инструкциям бота')
    msg = bot.send_message(message.chat.id, 'Введите название')
    bot.register_next_step_handler(msg, get_count_sum)


def get_count_sum(message):
    count_name = message.text
    bot.send_message(message.chat.id,  f'Записал название {count_name}')
    current_count['name'] = count_name
    msg = bot.send_message(message.chat.id, 'Введите остаток основного долга')
    bot.register_next_step_handler(msg, get_remain_sum)


def get_remain_sum(message):
    remain_sum = message.text
    bot.send_message(message.chat.id,  f'Записал остаток долга {remain_sum}')
    current_count['main_debt_sum'] = remain_sum
    msg = bot.send_message(message.chat.id, 'Введите процент')
    bot.register_next_step_handler(msg, get_interest)


def get_interest(message):
    interest = message.text
    bot.send_message(message.chat.id,  f'Записал процент {interest}')
    current_count['interest'] = interest
    msg = bot.send_message(message.chat.id, 'Введите дату начала ипотеки')
    bot.register_next_step_handler(msg, get_start_date)


def get_start_date(message):
    mortgage_start = message.text
    bot.send_message(message.chat.id, f'Записал дату начала {mortgage_start}')
    current_count['mortgage_start'] = mortgage_start
    msg = bot.send_message(message.chat.id, 'Введите дату первого платежа')
    bot.register_next_step_handler(msg, get_first_payment_date)


def get_first_payment_date(message):
    first_payment_date = message.text
    bot.send_message(message.chat.id, f'Записал дату первого платежа {first_payment_date}')
    current_count['first_payment_date'] = first_payment_date
    msg = bot.send_message(message.chat.id, 'Введите дату последнего платежа')
    bot.register_next_step_handler(msg, get_last_payment_date)


def get_last_payment_date(message):
    last_payment_date = message.text
    bot.send_message(message.chat.id, f'Записал дату последнего платежа {last_payment_date}')
    current_count['last_payment_date'] = last_payment_date
    count_month_payment(message)


def count_month_payment(message):
    bot.send_message(message.chat.id, f'Рассчитываю размер ежемесячного платежа')
    count_data = create_count(message.chat.id, current_count)
    bot.send_message(message.chat.id, f'Параметры вашего платежа {count_data.__dict__}')
    bot.send_message(message.chat.id, f'Размер ежемесячного платежа cоставляет {count_data.month_payment}')


@bot.message_handler(commands=['main'])
def get_count_name(message):
    bot.send_message(message.chat.id, 'Ищу параметры основного платежа')
    count_data = find_old_count(message.chat.id, 'main')
    bot.send_message(message.chat.id, f'Параметры основного платежа {count_data}')


# async def on_default_command(chat: Chat, match):
#     chat_id = chat.id
#     facilitator_message_id = str(chat.message["message_id"])
#     game_name = match.group(1)
#     facilitator = TelegramUser.from_dict(chat.sender)
#
#     if game_name == "game":
#         game_name = "(no name)"
#
#     active_game = await game_registry.find_active_game(chat_id, facilitator)
#     if active_game is not None:
#         await chat.send_text(
#             text="You have active game already. Need to /game_end to start another one."
#         )
#         return
#
#     game = Mortgage(chat_id, facilitator_message_id, game_name, facilitator)
#     await create_game(chat, game)
#
#
# @bot.command("/game_end$")
# async def on_game_end_command(chat: Chat, match):
#     chat_id = chat.id
#     facilitator = TelegramUser.from_dict(chat.sender)
#
#     active_game = await game_registry.find_active_game(chat_id, facilitator)
#
#     if active_game is None:
#         await chat.send_text(
#             text="You do not have active game. Need to run /game to start game."
#         )
#         return
#
#     await end_game(chat, active_game)
#
#
# @bot.command("(?s)/poker\s+(.+)$")
# @bot.command("/(poker)$")
# async def on_poker_command(chat: Chat, match):
#     chat_id = chat.id
#     facilitator_message_id = str(chat.message["message_id"])
#     topic = match.group(1)
#     facilitator = TelegramUser.from_dict(chat.sender)
#
#     if topic == "poker":
#         topic = "(no topic)"
#
#     game = await game_registry.find_active_game(chat_id, facilitator)
#
#     game_session = MortgageCount(game, chat_id, facilitator_message_id, topic, facilitator)
#     await create_game_session(chat, game_session)
#
#
# @bot.callback(r"discussion-vote-click-(.*?)-(.*?)$")
# async def on_discussion_vote_click(chat: Chat, callback_query: CallbackQuery, match):
#     logbook.info("{}", callback_query)
#     facilitator_message_id = int(match.group(1))
#     vote = match.group(2)
#     result = "Vote `{}` accepted".format(vote)
#     game_session = await game_registry.find_active_game_session(chat.id, facilitator_message_id)
#
#     if not game_session:
#         return await callback_query.answer(text="No such game session")
#
#     if game_session.phase not in MortgageCount.PHASE_DISCUSSION:
#         return await callback_query.answer(text="Can't vote not in " + MortgageCount.PHASE_DISCUSSION + " phase")
#
#     if not game_session.game.is_active():
#         return await callback_query.answer(text="Mortgage already ended")
#
#     game_session.add_discussion_vote(callback_query.src["from"], vote)
#     await game_registry.update_game_session(game_session)
#
#     await edit_message(chat, game_session)
#
#     await callback_query.answer(text=result)
#
#
# @bot.callback(r"estimation-vote-click-(.*?)-(.*?)$")
# async def on_estimation_vote_click(chat: Chat, callback_query: CallbackQuery, match):
#     logbook.info("{}", callback_query)
#     chat_id = chat.id
#     facilitator_message_id = int(match.group(1))
#     vote = match.group(2)
#     result = "Vote `{}` accepted".format(vote)
#     game_session = await game_registry.find_active_game_session(chat_id, facilitator_message_id)
#
#     if not game_session:
#         return await callback_query.answer(text="No such game session")
#
#     if game_session.phase not in MortgageCount.PHASE_ESTIMATION:
#         return await callback_query.answer(text="Can't vote not in " + MortgageCount.PHASE_ESTIMATION + " phase")
#
#     if not game_session.game.is_active():
#         return await callback_query.answer(text="Mortgage already ended")
#
#     game_session.add_estimation_vote(callback_query.src["from"], vote)
#     await game_registry.update_game_session(game_session)
#
#     await edit_message(chat, game_session)
#
#     await callback_query.answer(text=result)
#
#
# @bot.callback(r"({})-click-(.*?)$".format("|".join(FACILITATOR_OPERATIONS)))
# async def on_facilitator_operation_click(chat: Chat, callback_query: CallbackQuery, match):
#     operation = match.group(1)
#     chat_id = chat.id
#     facilitator_message_id = int(match.group(2))
#     game_session = await game_registry.find_active_game_session(chat_id, facilitator_message_id)
#
#     if not game_session:
#         return await callback_query.answer(text="No such game session")
#
#     if callback_query.src["from"]["id"] != game_session.facilitator.id:
#         return await callback_query.answer(text="Operation `{}` is available only for facilitator".format(operation))
#
#     if not game_session.game.is_active():
#         return await callback_query.answer(text="Mortgage already ended")
#
#     if operation in MortgageCount.OPERATION_START_ESTIMATION:
#         await run_operation_start_estimation(chat, game_session)
#     elif operation in MortgageCount.OPERATION_END_ESTIMATION:
#         await run_operation_end_estimation(chat, game_session)
#     elif operation in MortgageCount.OPERATION_CLEAR_VOTES:
#         await run_operation_clear_votes(chat, game_session)
#     elif operation in MortgageCount.OPERATION_RE_ESTIMATE:
#         await run_re_estimate(chat, game_session)
#     else:
#         raise Exception("Unknown operation `{}`".format(operation))
#
#     await callback_query.answer()
#
#
# async def run_operation_start_estimation(chat: Chat, game_session: MortgageCount):
#     game_session.start_estimation()
#     await edit_message(chat, game_session)
#     await game_registry.update_game_session(game_session)
#
#
# async def run_operation_clear_votes(chat: Chat, game_session: MortgageCount):
#     game_session.clear_votes()
#     await edit_message(chat, game_session)
#     await game_registry.update_game_session(game_session)
#
#
# async def run_operation_end_estimation(chat: Chat, game_session: MortgageCount):
#     game_session.end_estimation()
#     await edit_message(chat, game_session)
#     await game_registry.update_game_session(game_session)
#
#
# async def run_re_estimate(chat: Chat, game_session: MortgageCount):
#     message = {
#         "text": game_session.render_system_message_text(),
#     }
#
#     game_session.re_estimate()
#
#     # TODO: Extract to method
#     try:
#         await bot.edit_message_text(chat.id, game_session.system_message_id, **message)
#     except BotApiError:
#         logbook.exception("Error when updating markup")
#
#     await create_game_session(chat, game_session)
#
# async def end_game(chat: Chat, game: Mortgage):
#     game.end()
#     await game_registry.update_game(game)
#     game_statistics = await game_registry.get_game_statistics(game)
#     await chat.send_text(**game.render_results_system_message(game_statistics))


def create_count(chat_id: int, current_count: dict) :
    mortgage_count = MortgageCount(chat_id, **current_count)
    logbook.info(f'mortgage_count.__dict_ = {mortgage_count.__dict__}')
    mortgage_registry.create_count(mortgage_count)
    mortgage_count = mortgage_registry.find_count(mortgage_count)
    return mortgage_count


def find_old_count(chat_id: int, count_name: str):
    return mortgage_registry.find_old_count(chat_id, count_name)

#
# async def edit_message(chat: Chat, game_session: MortgageCount):
#     try:
#         await bot.edit_message_text(chat.id, game_session.system_message_id, **game_session.render_system_message())
#     except BotApiError:
#         logbook.exception("Error when updating markup")
#


# def test_fun(message):
#     logbook.info('проверяем что коллбек отрабатывает каждый раз')
#     bot.send_message(message.chat.id, f'коллбек отработал после текста {message.text}')


def main():
    mortgage_registry.init_db(DB_PATH)
    bot.polling(none_stop=True)


if __name__ == "__main__":
    main()
