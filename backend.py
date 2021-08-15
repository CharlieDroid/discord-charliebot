import sqlite3


def row_column(row_column_list):
    return row_column_list[0][0], row_column_list[0][1], row_column_list[1][0], row_column_list[1][1]


class DiscordDatabase:

    def __init__(self):
        self.connection = sqlite3.connect(r"C:\Users\Charles\Documents\Python Scripts\Discord 3.0\data\discordOasisData.db")
        self.cursor = self.connection.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS members ("
                            "memberID INTEGER PRIMARY KEY UNIQUE,"
                            "memberUsername TEXT NOT NULL,"
                            "memberName TEXT,"
                            "timestampJoined REAL NOT NULL,"
                            "timestampLastMessage REAL NOT NULL,"
                            "rulesReaction INTEGER NOT NULL,"
                            "numViolations INTEGER NOT NULL,"
                            "timestampLastViolation REAL NOT NULL"
                            ")")
        # memberID, memberUsername, memberName, timestampJoined,
        # timestampLastMessage, rulesReaction, numViolations, timestampLastViolation
        # timestamps are real/float because they are in ms

    def insert(self, memberID, memberUsername, memberName, timestampJoined, timestampLastMessage, rulesReaction,
               numViolations, timestampLastViolation):
        self.cursor.execute("INSERT INTO members VALUES(?, ?, ?, ?, ?, ?, ?, ?)",
                            (memberID, memberUsername, memberName, timestampJoined, timestampLastMessage, rulesReaction,
                             numViolations, timestampLastViolation))
        self.connection.commit()

    def get(self, row_column_list):
        rowIdentifier, rowValue, columnIdentifier, columnValue = row_column(row_column_list)
        if not (rowIdentifier and rowValue):
            self.cursor.execute(f"SELECT {columnIdentifier} FROM members")
        else:
            self.cursor.execute(f"SELECT {columnIdentifier} FROM members WHERE {rowIdentifier}=?",
                                (rowValue,))
        return self.cursor.fetchall()

    def delete(self, memberID):
        self.cursor.execute("DELETE FROM members WHERE memberID=?", (memberID,))
        self.connection.commit()

    def update(self, row_column_list):
        rowIdentifier, rowValue, columnIdentifier, columnValue = row_column(row_column_list)
        self.cursor.execute(f"UPDATE members SET {columnIdentifier}=? WHERE {rowIdentifier}=?",
                            (columnValue, rowValue))
        self.connection.commit()

    def __del__(self):
        self.connection.close()
