from app.telegram_user import TelegramUser
# from app.mortgage import Mortgage
import collections
from dataclasses import dataclass
from datetime import datetime, timedelta
from dateutil import relativedelta
from dateutil.rrule import rrule, MONTHLY
import json
import logbook


@dataclass
class MortgageCount:
    chat_id: int
    name: str
    main_debt_sum: float
    interest: float
    mortgage_start: datetime
    first_payment_date: datetime
    last_payment_date: datetime
    month_payment: float
    id: int = None
    interest_sum_left: float = None

    @property
    def mortgage_start(self):
        return self.__mortgage_start

    @mortgage_start.setter
    def mortgage_start(self, value):
        self.__mortgage_start = datetime.strptime(value, '%d.%m.%Y')

    @property
    def first_payment_date(self):
        return self.__first_payment_date

    @first_payment_date.setter
    def first_payment_date(self, value):
        self.__first_payment_date = datetime.strptime(value, '%d.%m.%Y')

    @property
    def last_payment_date(self):
        return self.__last_payment_date

    @last_payment_date.setter
    def last_payment_date(self, value):
        self.__last_payment_date = datetime.strptime(value, '%d.%m.%Y')

    @property
    def month_payment(self):
        return self.__month_payment

    @month_payment.setter
    def month_payment(self, value=None):
        period_interest = float(self.interest) / (100 * 12)
        payment = float(self.main_debt_sum) * (period_interest / (1 - (1 + period_interest) ** -self.__payment_period_num()))
        self.__month_payment = round(payment, 2)

    def __payment_period_num(self):
        if self.__mortgage_start.day < self.__first_payment_date.day:
            previous_payment_date = datetime(self.__mortgage_start.year,
                                             self.__mortgage_start.month - 1,
                                             self.__first_payment_date.day)
        else:
            previous_payment_date = datetime(self.__mortgage_start.year,
                                             self.__mortgage_start.month,
                                             self.__first_payment_date.day)
        all_mortgage_time = self.__last_payment_date - previous_payment_date
        period_num = round((all_mortgage_time.days / 365) * 12)
        logbook.info(f'period_num = {period_num}')
        s1, e1 = previous_payment_date, self.__last_payment_date + timedelta(days=1)
        s360 = (s1.year * 12 + s1.month) * 30 + s1.day
        e360 = (e1.year * 12 + e1.month) * 30 + e1.day
        dates_360 = divmod(e360 - s360, 30)[0]
        logbook.info(f'dates_360 = {dates_360}')
        rd = relativedelta.relativedelta(self.__last_payment_date, previous_payment_date)
        rd_period = rd.months + (12*rd.years)
        logbook.info(f'rd_period = {rd_period}')
        # dates = [dt for dt in rrule(MONTHLY, bymonthday=2, dtstart=self.__first_payment_date, until=self.__last_payment_date)]
        # logbook.info(f'dates = {dates}')
        # dates_2 = [dt for dt in rrule(MONTHLY, bymonthday=2, dtstart=self.__first_payment_date.replace(day=1), until=self.__last_payment_date.replace(day=1))]
        # logbook.info(f'dates_2 = {dates_2}')
        return period_num


    #
    # def start_estimation(self):
    #     self.phase = self.PHASE_ESTIMATION
    #
    # def end_estimation(self):
    #     self.phase = self.PHASE_RESOLUTION
    #
    # def clear_votes(self):
    #     self.estimation_votes.clear()
    #     self.phase = self.PHASE_ESTIMATION
    #
    # def re_estimate(self):
    #     self.estimation_votes.clear()
    #     self.phase = self.PHASE_ESTIMATION
    #
    # def add_discussion_vote(self, player, vote):
    #     self.discussion_votes[self.player_to_string(player)].set(vote)
    #
    # def add_estimation_vote(self, player, vote):
    #     self.estimation_votes[self.player_to_string(player)].set(vote)
    #
    # def render_system_message(self):
    #     return {
    #         "text": self.render_system_message_text(),
    #         "reply_markup": json.dumps(self.render_system_message_buttons()),
    #     }
    #
    # def render_system_message_text(self):
    #     result = ""
    #
    #     result += self.render_game_text()
    #     result += "\n"
    #     result += self.render_facilitator_text()
    #     result += "\n"
    #     result += self.render_topic_text()
    #     result += "\n"
    #     result += "\n"
    #     result += self.render_votes_text()
    #
    #     return result
    #
    # def render_game_text(self):
    #     if self.game is None:
    #         return ""
    #     else:
    #         return "Mortgage: {}".format(self.game.name)
    #
    # def render_facilitator_text(self):
    #     return "Facilitator: {}".format(self.facilitator.to_string())
    #
    # def render_topic_text(self):
    #     result = ""
    #
    #     if self.phase in self.PHASE_DISCUSSION:
    #         result += "Discussion for: "
    #     elif self.phase in self.PHASE_ESTIMATION:
    #         result += "Estimation for: "
    #     elif self.phase in self.PHASE_RESOLUTION:
    #         result += "Resolution for: "
    #
    #     result += self.topic
    #
    #     return result
    #
    # def render_votes_text(self):
    #     if self.phase in self.PHASE_DISCUSSION:
    #         return self.render_discussion_votes_text()
    #     elif self.phase in self.PHASE_ESTIMATION:
    #         return self.render_estimation_votes_text()
    #     elif self.phase in self.PHASE_RESOLUTION:
    #         return self.render_estimation_votes_text()
    #
    # def render_discussion_votes_text(self):
    #     result = ""
    #
    #     votes_count = len(self.discussion_votes)
    #
    #     if votes_count > 0:
    #         result += "Votes ({}):".format(votes_count)
    #         result += "\n"
    #         result += "\n".join(
    #             "{} {}".format(
    #                 discussion_vote.icon,
    #                 user_id,
    #             )
    #             for user_id, discussion_vote in sorted(self.discussion_votes.items())
    #         )
    #
    #     return result
    #
    # def render_estimation_votes_text(self):
    #     result = ""
    #
    #     votes_count = len(self.estimation_votes)
    #
    #     if votes_count > 0:
    #         result += "Votes ({}):".format(votes_count)
    #         result += "\n"
    #         result += "\n".join(
    #             "{} {}".format(
    #                 estimation_vote.vote if self.phase == self.PHASE_RESOLUTION else estimation_vote.masked,
    #                 user_id,
    #             )
    #             for user_id, estimation_vote in sorted(self.estimation_votes.items())
    #         )
    #
    #     return result
    #
    # def render_system_message_buttons(self):
    #     layout_rows = []
    #
    #     if self.phase in self.PHASE_DISCUSSION:
    #         layout_rows.append(
    #             [
    #                 self.render_discussion_vote_button(
    #                     DiscussionVote.VOTE_TO_ESTIMATE,
    #                     "👍 To estimate",
    #                 ),
    #                 self.render_discussion_vote_button(
    #                     DiscussionVote.VOTE_NEED_DISCUSS,
    #                     "⁉️ Discuss",
    #                 ),
    #             ]
    #         )
    #         layout_rows.append(
    #             [
    #                 self.render_discussion_vote_button(
    #                     DiscussionVote.VOTE_SPLIT_TASK,
    #                     "✂️ Split",
    #                 ),
    #                 self.render_discussion_vote_button(
    #                     DiscussionVote.VOTE_CANCEL_TASK,
    #                     "☠️️ Cancel",
    #                 ),
    #             ]
    #         )
    #         layout_rows.append(
    #             [
    #                 self.render_discussion_vote_button(
    #                     DiscussionVote.VOTE_ESTIMATION_IMPOSSIBLE,
    #                     "♾️ Impossible",
    #                 ),
    #                 self.render_discussion_vote_button(
    #                     DiscussionVote.VOTE_TAKE_A_BREAK,
    #                     "☕️ Take a break",
    #                 ),
    #             ]
    #         )
    #         layout_rows.append(
    #             [
    #                 self.render_operation_button(self.OPERATION_START_ESTIMATION, "Start estimation"),
    #             ]
    #         )
    #     elif self.phase in self.PHASE_ESTIMATION:
    #         for votes_layout_row in self.CARD_DECK_LAYOUT:
    #             vote_buttons_row = []
    #             for vote in votes_layout_row:
    #                 vote_buttons_row.append(self.render_estimation_vote_button(vote))
    #             layout_rows.append(vote_buttons_row)
    #
    #         layout_rows.append(
    #             [
    #                 self.render_operation_button(self.OPERATION_CLEAR_VOTES, "Clear votes"),
    #                 self.render_operation_button(self.OPERATION_END_ESTIMATION, "End estimation"),
    #             ]
    #         )
    #     elif self.phase in self.PHASE_RESOLUTION:
    #         layout_rows.append(
    #             [
    #                 self.render_operation_button(self.OPERATION_RE_ESTIMATE, "Re-estimate"),
    #             ]
    #         )
    #
    #     return {
    #         "type": "InlineKeyboardMarkup",
    #         "inline_keyboard": layout_rows,
    #     }
    #
    # def render_discussion_vote_button(self, vote: str, text: str):
    #     return {
    #         "type": "InlineKeyboardButton",
    #         "text": text,
    #         "callback_data": "discussion-vote-click-{}-{}".format(self.facilitator_message_id, vote),
    #     }
    #
    # def render_estimation_vote_button(self, vote: str):
    #     return {
    #         "type": "InlineKeyboardButton",
    #         "text": vote,
    #         "callback_data": "estimation-vote-click-{}-{}".format(self.facilitator_message_id, vote),
    #     }
    #
    # def render_operation_button(self, operation: str, text: str):
    #     return {
    #         "type": "InlineKeyboardButton",
    #         "text": text,
    #         "callback_data": "{}-click-{}".format(operation, self.facilitator_message_id),
    #     }
    #
    # @staticmethod
    # def player_to_string(player: dict) -> str:
    #     return "@{} ({})".format(
    #         player.get("username") or player.get("id"),
    #         "{} {}".format(player.get("first_name"), player.get("last_name") or "").strip()
    #     )
    #
    # @staticmethod
    # def votes_to_json(votes):
    #     return {
    #         user_id: vote.to_dict() for user_id, vote in votes.items()
    #     }
    #
    # def to_dict(self):
    #     return {
    #         "facilitator": self.facilitator.to_dict(),
    #         "discussion_votes": self.votes_to_json(self.discussion_votes),
    #         "estimation_votes": self.votes_to_json(self.estimation_votes),
    #     }
    #
    # @classmethod
    # def from_dict(cls, game: Mortgage, chat_id: int, facilitator_message_id: int, topic: str, facilitator: TelegramUser, dict):
    #     result = cls(
    #         game,
    #         chat_id,
    #         facilitator_message_id,
    #         topic,
    #         facilitator,
    #     )
    #
    #     for user_id, discussion_vote in dict["discussion_votes"].items():
    #         result.discussion_votes[user_id] = DiscussionVote.from_dict(discussion_vote)
    #
    #     for user_id, estimation_vote in dict["estimation_votes"].items():
    #         result.estimation_votes[user_id] = EstimationVote.from_dict(estimation_vote)
    #
    #     return result
