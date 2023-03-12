import logbook

from app.mortgage import Mortgage
from app.mortgage_count import MortgageCount
from app.telegram_user import TelegramUser
import sqlite3
import json
from collections import defaultdict


class MortgageRegistry:
    def __init__(self):
        self.db_connection = None
        self.cursor = None

    def init_db(self, db_path: str):
        db_connection = sqlite3.connect(db_path, check_same_thread=False)
        self.db_connection = db_connection
        self.db_connection.row_factory = sqlite3.Row
        self.run_migrations()

    def run_migrations(self):
        self.db_connection.execute(
            """
                CREATE TABLE IF NOT EXISTS mortgage_count (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    main_debt_sum REAL,
                    interest REAL,
                    mortgage_start DATE,
                    first_payment_date DATE,
                    last_payment_date DATE,
                    month_payment REAL,
                    interest_sum_left REAL
                )
            """
        )

        self.db_connection.execute(
            """
                CREATE TABLE IF NOT EXISTS partial_repayment (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    mortgage_count_id INTEGER NOT NULL,
                    date DATE NOT NULL,
                    repayment_sum REAL NOT NULL
                )
            """
        )
        self.db_connection.execute(
            """
                CREATE UNIQUE INDEX IF NOT EXISTS mortgage_count_id_partial_repayment_id_idx 
                ON partial_repayment (id, mortgage_count_id);
            """
        )

    def create_count(self, mortgage_count: MortgageCount):
        self.db_connection.execute(
            """
                INSERT INTO mortgage_count
                (
                    name,
                    chat_id,
                    main_debt_sum,
                    interest,
                    mortgage_start,
                    first_payment_date,
                    last_payment_date,
                    month_payment
                ) VALUES (
                    :name,
                    :chat_id,
                    :main_debt_sum,
                    :interest,
                    :mortgage_start,
                    :first_payment_date,
                    :last_payment_date,
                    :month_payment
                )
            """,
            {
                "name": mortgage_count.name,
                "chat_id": mortgage_count.chat_id,
                "main_debt_sum": mortgage_count.main_debt_sum,
                "interest": mortgage_count.interest,
                "mortgage_start": mortgage_count.mortgage_start,
                "first_payment_date": mortgage_count.first_payment_date,
                "last_payment_date": mortgage_count.last_payment_date,
                "month_payment": mortgage_count.month_payment
            }
        )
        self.db_connection.commit()

    def update_count(self, mortgage_count: MortgageCount):
        self.db_connection.execute(
            """
                UPDATE mortgage_count
                SET main_debt_sum = :main_debt_sum,
                    interest = :interest
                WHERE id = :count_id
            """,
            {
                "count_id": mortgage_count.id,
                "main_debt_sum": mortgage_count.main_debt_sum,
                "interest": mortgage_count.interest
            }
        )
        self.db_connection.commit()

    def find_count(self, count: MortgageCount) -> MortgageCount:
        cursor = self.db_connection.execute(
            """
                SELECT
                    id,
                    chat_id,
                    name,
                    interest_sum_left
                FROM mortgage_count
                WHERE chat_id = :chat_id
                AND name = :name
                ORDER BY id DESC
                LIMIT 1
            """,
            {
                "chat_id": count.chat_id,
                "name": count.name
            }
        )
        row = cursor.fetchone()
        count.id = row["id"]
        count.interest_sum_left = row["interest_sum_left"]
        return count

    def find_old_count(self, chat_id: int, count_name: str) -> MortgageCount:
        cursor = self.db_connection.execute(
            """
                SELECT *
                FROM mortgage_count
                WHERE chat_id = :chat_id
                AND name = :name
                ORDER BY id DESC
                LIMIT 1
            """,
            {
                "chat_id": chat_id,
                "name": count_name,
            }
        )
        row = cursor.fetchone()
        if not row:
            return None
        fields = [column[0] for column in cursor.description]
        my_dict = {key: value for key, value in zip(fields, row)}
        return my_dict

    #
    #
    # async def update_game_session(self, game_session: MortgageCount):
    #     await self.db_connection.execute(
    #         """
    #             UPDATE game_session
    #             SET phase = :phase,
    #                 json_data = :json_data,
    #                 updated_at = datetime('now')
    #             WHERE chat_id = :chat_id
    #             AND system_message_id = :system_message_id
    #         """,
    #         {
    #             "phase": game_session.phase,
    #             "json_data": json.dumps(game_session.to_dict()),
    #             "chat_id": game_session.chat_id,
    #             "system_message_id": game_session.system_message_id,
    #         }
    #     )
    #     await self.db_connection.commit()
    #
    # async def get_game_statistics(self, game: Mortgage):
    #     query = """
    #         SELECT
    #             COUNT(DISTINCT facilitator_message_id) AS estimated_game_sessions_count
    #         FROM game_session
    #         WHERE game_id = :game_id
    #         AND phase = :game_session_phase
    #     """
    #     parameters = {
    #         "game_id": game.id,
    #         "game_session_phase": MortgageCount.PHASE_RESOLUTION,
    #     }
    #     async with self.db_connection.execute(query, parameters) as cursor:
    #         row = await cursor.fetchone()
    #
    #         if not row:
    #             return None
    #
    #         return {
    #             "estimated_game_sessions_count": row["estimated_game_sessions_count"],
    #         }
