import sqlite3


def row_column(row_column_list):
    return row_column_list[0][0], row_column_list[0][1], row_column_list[1][0], row_column_list[1][1]


class DiscordDatabase:

    def __init__(self):
        self.connection = sqlite3.connect(r"../data/discordOasisData.db")
        self.cursor = self.connection.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS members ("
                            "memberID INTEGER PRIMARY KEY UNIQUE,"
                            "memberUsername TEXT NOT NULL DEFAULT '',"
                            "memberName TEXT NOT NULL DEFAULT '',"
                            "timestampJoined REAL NOT NULL DEFAULT 0,"
                            "timestampLastMessage REAL NOT NULL DEFAULT 0,"
                            "rulesReaction INTEGER NOT NULL DEFAULT 0,"
                            "numViolations INTEGER NOT NULL DEFAULT 0,"
                            "timestampLastViolation REAL NOT NULL DEFAULT 0,"
                            "lastMessage TEXT NOT NULL DEFAULT '',"
                            "counter INTEGER NOT NULL DEFAULT 0,"
                            "inServer BOOLEAN NOT NULL DEFAULT True"
                            ")")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS leveling ("
                            "memberID INTEGER PRIMARY KEY UNIQUE,"
                            "memberUsername TEXT NOT NULL DEFAULT '',"
                            "level INTEGER NOT NULL DEFAULT 0,"
                            "experience REAL NOT NULL DEFAULT 0,"
                            "previousExperience REAL NOT NULL DEFAULT 0,"
                            "timestampLastUpdate REAL NOT NULL DEFAULT 0,"
                            "timestampLastVoice REAL NOT NULL DEFAULT 0,"
                            "addXPVoice BOOLEAN NOT NULL DEFAULT FALSE,"
                            "messages INTEGER NOT NULL DEFAULT 0,"
                            "voiceMinutes REAL NOT NULL DEFAULT 0,"
                            "passiveHours REAL NOT NULL DEFAULT 0"
                            ")")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS memory ("
                            "guildID INTEGER PRIMARY KEY UNIQUE,"
                            "guildName TEXT NOT NULL DEFAULT '',"
                            "leaderboardMessageID INTEGER NOT NULL DEFAULT 0"
                            ")")
        # memberID, memberUsername, memberName, timestampJoined,
        # timestampLastMessage, rulesReaction, numViolations, timestampLastViolation,
        # lastMessage
        # timestamps are real/float because they are in ms

    def insert(self, memberID, memberUsername, memberName, timestampJoined, timestampLastMessage, rulesReaction,
               numViolations, timestampLastViolation, lastMessage, counter, inServer, dbTable="members"):
        self.cursor.execute(f"INSERT INTO {dbTable} VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                            (memberID, memberUsername, memberName, timestampJoined, timestampLastMessage, rulesReaction,
                             numViolations, timestampLastViolation, lastMessage, counter, inServer))
        self.cursor.execute(f"INSERT INTO leveling(memberID, memberUsername) VALUES(?, ?)",
                            (memberID, memberUsername))
        # must insert value 0 in memory because no row will be made
        self.connection.commit()

    def get(self, row_column_list, dbTable="members"):
        rowIdentifier, rowValue, columnIdentifier, columnValue = row_column(row_column_list)
        if not (rowIdentifier and rowValue):
            self.cursor.execute(f"SELECT {columnIdentifier} FROM {dbTable}")
        else:
            self.cursor.execute(f"SELECT {columnIdentifier} FROM {dbTable} WHERE {rowIdentifier}=?",
                                (rowValue,))
        return self.cursor.fetchall()

    def get_actives(self):
        self.cursor.execute(f"SELECT memberID FROM leveling WHERE xpMult > 0")
        return [i[0] for i in self.cursor.fetchall()]

    def get_count(self):
        self.cursor.execute(f"SELECT COUNT(*) FROM leveling WHERE memberID IN "
                            f"(SELECT memberID FROM members WHERE inServer = 1)")
        return self.cursor.fetchall()[0][0]

    def get_ids(self, dbTable="members"):
        self.cursor.execute(f"SELECT memberID FROM {dbTable}")
        return [i[0] for i in self.cursor.fetchall()]

    def get_stats(self):
        self.cursor.execute(f"SELECT ROW_NUMBER() OVER (ORDER BY experience DESC) RowNum, memberUsername, voiceMinutes, "
                            f"messages, reactions, passiveHours, experience, level, memberID FROM leveling "
                            f"WHERE memberID IN (SELECT memberID FROM members WHERE inServer = 1)")
        return self.cursor.fetchall()

    def delete(self, memberID, dbTable="members"):
        self.cursor.execute(f"DELETE FROM {dbTable} WHERE 'memberID'=?", (memberID,))
        self.connection.commit()

    def update(self, row_column_list, dbTable="members"):
        rowIdentifier, rowValue, columnIdentifier, columnValue = row_column(row_column_list)
        if not (rowIdentifier and rowValue):
            self.cursor.execute(f"UPDATE {dbTable} SET {columnIdentifier}=?",
                                (columnValue,))
        else:
            self.cursor.execute(f"UPDATE {dbTable} SET {columnIdentifier}=? WHERE {rowIdentifier}=?",
                                (columnValue, rowValue))

        self.connection.commit()

    def __del__(self):
        self.connection.close()
