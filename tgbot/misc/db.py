import asyncio
from typing import Tuple

import pyodbc

from tgbot.config import load_config

config = load_config(".env")

connection_string = f"""
    DRIVER={{ODBC Driver 17 for SQL Server}};
    SERVER={config.db.host};
    DATABASE={config.db.database};
    UID={config.db.user};
    PWD={config.db.password};
    """

conn = pyodbc.connect(connection_string)


def is_admin(user_id: int):
    cursor = conn.cursor()

    query = """
            SELECT Role
            FROM dbo.RegisteredUsers
            WHERE ChatId = ?
            """

    cursor.execute(query, (user_id,))
    user_role = cursor.fetchone()
    cursor.close()

    if user_role and user_role[0] == 10:
        return True
    else:
        return False


async def run_procedure(procedure: str) -> Tuple[bool, str]:
    """
    Execute a stored procedure asynchronously with proper error handling.

    Args:
        procedure (str): Name of the procedure to execute

    Returns:
        Tuple[bool, str]: (success, message)
    """

    def _execute_procedure():
        """Execute procedure in a separate thread"""
        cursor = None
        try:
            cursor = conn.cursor()

            # Execute the procedure
            cursor.execute(f"EXEC {procedure}")

            # Commit the transaction
            conn.commit()

            # Get affected rows count if available
            rowcount = cursor.rowcount if hasattr(cursor, 'rowcount') else 0

            return True, f"Процедура {procedure} выполнена успешно. Обработано записей: {rowcount}"

        except pyodbc.Error as e:
            # Rollback transaction on error
            try:
                conn.rollback()
            except:
                pass

            error_msg = str(e)
            if hasattr(e, 'args') and len(e.args) > 1:
                error_msg = e.args[1] if e.args[1] else str(e)

            return False, f"Ошибка выполнения процедуры {procedure}: {error_msg}"

        except Exception as e:
            # Rollback transaction on any other error
            try:
                conn.rollback()
            except:
                pass

            return False, f"Неожиданная ошибка при выполнении процедуры {procedure}: {str(e)}"

        finally:
            if cursor:
                try:
                    cursor.close()
                except:
                    pass

    # Run the procedure in a thread pool to avoid blocking the event loop
    loop = asyncio.get_event_loop()
    try:
        success, message = await loop.run_in_executor(None, _execute_procedure)
        return success, message
    except Exception as e:
        return False, f"Ошибка выполнения в потоке: {str(e)}"


def get_connection_status() -> Tuple[bool, str]:
    """
    Check if database connection is working.

    Returns:
        Tuple[bool, str]: (is_connected, message)
    """
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        return True, "Соединение с базой данных активно"
    except Exception as e:
        return False, f"Ошибка соединения с БД: {str(e)}"
