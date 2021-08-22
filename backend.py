import sqlite3


def row_column(row_column_list):
    return row_column_list[0][0], row_column_list[0][1], row_column_list[1][0], row_column_list[1][1]


class DiscordDatabase:

    def __init__(self):
        self.connection = sqlite3.connect(
            r"C:\Users\Charles\Documents\Python Scripts\Discord 3.0\data\discordOasisData.db")
        self.cursor = self.connection.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS members ("
                            "memberID INTEGER PRIMARY KEY UNIQUE,"
                            "memberUsername TEXT NOT NULL,"
                            "memberName TEXT NOT NULL,"
                            "timestampJoined REAL NOT NULL DEFAULT 0,"
                            "timestampLastMessage REAL NOT NULL DEFAULT 0,"
                            "rulesReaction INTEGER NOT NULL DEFAULT 0,"
                            "numViolations INTEGER NOT NULL DEFAULT 0,"
                            "timestampLastViolation REAL NOT NULL DEFAULT 0,"
                            "lastMessage TEXT NOT NULL DEFAULT ''"
                            ")")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS leveling ("
                            "memberID INTEGER PRIMARY KEY UNIQUE,"
                            "memberUsername TEXT NOT NULL,"
                            "level INTEGER NOT NULL DEFAULT 0,"
                            "experience REAL NOT NULL DEFAULT 0,"
                            "previousExeprience REAL NOT NULL DEFAULT 0,"
                            "timestampLastUpdate REAL NOT NULL DEFAULT 0,"
                            "timestampLastVoice REAL NOT NULL DEFAULT 0"
                            ")")
        # memberID, memberUsername, memberName, timestampJoined,
        # timestampLastMessage, rulesReaction, numViolations, timestampLastViolation,
        # lastMessage
        # timestamps are real/float because they are in ms

    def insert(self, memberID, memberUsername, memberName, timestampJoined, timestampLastMessage, rulesReaction,
               numViolations, timestampLastViolation, lastMessage, dbTable="members"):
        self.cursor.execute(f"INSERT INTO {dbTable} VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)",
                            (memberID, memberUsername, memberName, timestampJoined, timestampLastMessage, rulesReaction,
                             numViolations, timestampLastViolation, lastMessage))
        self.connection.commit()

    def get(self, row_column_list, dbTable="members"):
        rowIdentifier, rowValue, columnIdentifier, columnValue = row_column(row_column_list)
        if not (rowIdentifier and rowValue):
            self.cursor.execute(f"SELECT {columnIdentifier} FROM {dbTable}")
        else:
            self.cursor.execute(f"SELECT {columnIdentifier} FROM {dbTable} WHERE {rowIdentifier}=?",
                                (rowValue,))
        return self.cursor.fetchall()

    def get_rank(self):
        self.cursor.execute(f"SELECT ROW_NUMBER() OVER ("
                            f"ORDER BY experience DESC) "
                            f"RowNum, memberID, experience "
                            f"FROM leveling")
        return self.cursor.fetchall()

    def delete(self, memberID, dbTable="members"):
        self.cursor.execute(f"DELETE FROM {dbTable} WHERE 'memberID'=?", (memberID,))
        self.connection.commit()

    def update(self, row_column_list, dbTable="members"):
        rowIdentifier, rowValue, columnIdentifier, columnValue = row_column(row_column_list)
        self.cursor.execute(f"UPDATE {dbTable} SET {columnIdentifier}=? WHERE {rowIdentifier}=?",
                            (columnValue, rowValue))
        self.connection.commit()



    def __del__(self):
        self.connection.close()
