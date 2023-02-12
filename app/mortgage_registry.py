from app.mortgage import Mortgage
from app.mortgage_count import MortgageCount
from app.telegram_user import TelegramUser
import sqlite3
import json


class MortgageRegistry:
    def __init__(self):
        self.db_connection = None

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
                    percent REAL,
                    mortgage_start DATE,
                    first_payment_date DATE,
                    last_payment_date DATE,
                    month_payment REAL,
                    perсent_sum_left REAL
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
                    chat_id
                ) VALUES (
                    :name,
                    :chat_id
                )
            """,
            {
                "name": mortgage_count.name,
                "chat_id": mortgage_count.chat_id
                # "main_debt_sum": mortgage_count.main_debt_sum,
                # "percent": mortgage_count.percent,
                # "mortgage_start": mortgage_count.mortgage_start,
                # "first_payment_date": mortgage_count.first_payment_date,
                # "last_payment_date": mortgage_count.last_payment_date
            }
        )
        self.db_connection.commit()

    # async def update_game(self, game: Mortgage):
    #     await self.db_connection.execute(
    #         """
    #             UPDATE game
    #             SET status = :game_status
    #             WHERE id = :game_id
    #         """,
    #         {
    #             "game_id": game.id,
    #             "game_status": game.status,
    #         }
    #     )
    #     await self.db_connection.commit()

    # async def find_active_game(self, chat_id: int, facilitator: TelegramUser) -> Mortgage:
    #     query = """
    #         SELECT
    #             id AS game_id,
    #             facilitator_message_id AS game_facilitator_message_id,
    #             system_message_id AS game_system_message_id,
    #             status AS game_status,
    #             name AS game_name,
    #             json_data AS game_json_data
    #         FROM game
    #         WHERE chat_id = :chat_id
    #         AND facilitator_id = :game_facilitator_id
    #         AND status = :active_game_status
    #         ORDER BY system_message_id DESC
    #         LIMIT 1
    #     """
    #     parameters = {
    #         "chat_id": chat_id,
    #         "game_facilitator_id": facilitator.id,
    #         "active_game_status": Mortgage.STATUS_STARTED,
    #     }
    #     async with self.db_connection.execute(query, parameters) as cursor:
    #         row = await cursor.fetchone()
    #
    #         if not row:
    #             return None
    #
    #         game_json_data = json.loads(row["game_json_data"])
    #         game_facilitator = TelegramUser.from_dict(game_json_data["facilitator"])
    #
    #         game = Mortgage.from_dict(
    #             chat_id,
    #             row["game_facilitator_message_id"],
    #             row["game_name"],
    #             game_facilitator,
    #         )
    #         game.id = row["game_id"]
    #         game.system_message_id = row["game_system_message_id"]
    #         game.status = row["game_status"]
    #
    #         return game
    #
    # async def find_active_game_session(self, chat_id: int, game_session_facilitator_message_id: int) -> MortgageCount:
    #     query = """
    #         SELECT
    #             g.id AS game_id,
    #             g.facilitator_message_id AS game_facilitator_message_id,
    #             g.system_message_id AS game_system_message_id,
    #             g.status AS game_status,
    #             g.name AS game_name,
    #             g.json_data AS game_json_data,
    #             gs.facilitator_message_id AS game_session_facilitator_message_id,
    #             gs.system_message_id AS game_session_system_message_id,
    #             gs.phase AS game_session_phase,
    #             gs.topic AS game_session_topic,
    #             gs.json_data AS game_session_json_data
    #         FROM game_session AS gs
    #         LEFT JOIN game AS g
    #         ON gs.game_id = g.id
    #         WHERE gs.chat_id = :chat_id
    #         AND gs.facilitator_message_id = :game_session_facilitator_message_id
    #         ORDER BY gs.system_message_id DESC
    #         LIMIT 1
    #     """
    #     parameters = {
    #         "chat_id": chat_id,
    #         "game_session_facilitator_message_id": game_session_facilitator_message_id,
    #     }
    #     async with self.db_connection.execute(query, parameters) as cursor:
    #         row = await cursor.fetchone()
    #
    #         if not row:
    #             return None
    #
    #         if row["game_id"] is None:
    #             game = None
    #         else:
    #             game_json_data = json.loads(row["game_json_data"])
    #             game_facilitator = TelegramUser.from_dict(game_json_data["facilitator"])
    #
    #             game = Mortgage.from_dict(
    #                 chat_id,
    #                 row["game_facilitator_message_id"],
    #                 row["game_name"],
    #                 game_facilitator,
    #             )
    #             game.id = row["game_id"]
    #             game.system_message_id = row["game_system_message_id"]
    #             game.status = row["game_status"]
    #
    #         game_session_json_data = json.loads(row["game_session_json_data"])
    #         game_session_facilitator = TelegramUser.from_dict(game_session_json_data["facilitator"])
    #
    #         game_session = MortgageCount.from_dict(
    #             game,
    #             chat_id,
    #             row["game_session_facilitator_message_id"],
    #             row["game_session_topic"],
    #             game_session_facilitator,
    #             game_session_json_data,
    #         )
    #         game_session.system_message_id = row["game_session_system_message_id"]
    #         game_session.phase = row["game_session_phase"]
    #
    #         return game_session
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
