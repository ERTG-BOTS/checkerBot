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
