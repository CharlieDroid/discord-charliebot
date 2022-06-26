from PIL import Image, ImageDraw, ImageFont


def round_off(num):
    return int(round(num, 0))


def crop_to_square(im):
    width, height = im.size
    if height > width:
        im = im.crop((0, (height - width) / 2, width, ((height - width) / 2) + width))
    elif width > height:
        im = im.crop(((width - height) / 2, 0, ((width - height) / 2) + height, height))
    return im


class Leaderboard:

    def __init__(self, rowData, imageName=None):
        # rowData must contain
        # [(rank, imageObject, name, messages, voiceMinutes, passiveHours, Experience, Level, levelRatio),...]
        # new rowData
        # [(rank, imageObject, name, voiceMinutes, messages, reactions, passiveHours, XP, Level, levelRatio),...]
        self.numUsers = len(rowData)
        self.rowHeight = 100
        self.margin, self.textMargin = 15, 10
        self.canvasNoMargin = (1000, self.rowHeight * self.numUsers)
        self.canvasSize = (self.canvasNoMargin[0] + self.margin * 2, self.canvasNoMargin[1] + (self.margin * 2))
        self.radius = 10
        self.thumbnailSize = (70, 70)
        self.levelSize = 70
        self.rankSize = 40
        self.levelThickness = 3
        # stats space is the space in between stats (lmao)
        # change 200, the higher the closer, the lower the farther
        stats_total_space = self.canvasNoMargin[0] - self.rankSize - self.thumbnailSize[0] - self.levelSize - 200
        self.statsSpace = int(round(stats_total_space / len(rowData[0][3:-1]), 0))
        self.smallFontSize, self.mediumFontSize, self.largeFontSize = 12, 20, 22

        self.midnightColor = (0, 4, 13)
        self.nightGreyColor = (44, 54, 64)
        self.pastelOrangeColor = (255, 179, 71)
        self.pastelWhite = (250, 248, 246)
        self.pastelGold = (220, 180, 35)
        self.pastelSilver = (180, 184, 193)
        self.pastelBronze = (158, 104, 30)
        self.labelColor = (207, 207, 202)
        self.valueColor = self.pastelWhite

        if imageName:
            self.imageObject = Image.open(imageName).convert("RGBA")

        self.normalFont = r"C:\Users\Charles\Documents\Python Scripts\Discord 3.0\scratch\Helvetica.ttf"
        self.boldFont = r"C:\Users\Charles\Documents\Python Scripts\Discord 3.0\scratch\Helvetica-Bold.ttf"
        self.mediumFont = ImageFont.truetype(self.normalFont, self.smallFontSize)
        self.boldLargeFont = ImageFont.truetype(self.boldFont, self.mediumFontSize)
        self.boldMediumFont = ImageFont.truetype(self.boldFont, self.largeFontSize)

        self.canvas = Image.new("RGBA", self.canvasSize, (0, 0, 0, 0))
        self.draw = ImageDraw.Draw(self.canvas)
        self.draw.rounded_rectangle((0, 0, self.canvasSize[0], self.canvasSize[1]),
                                    radius=self.radius / 2, fill=self.midnightColor)

        self.levelLabel = "LEVEL"
        self.experienceLabel = "XP GAINED"
        self.passiveLabel = "HOURS JOINED"
        self.reactionsLabel = "REACTIONS"
        self.messagesLabel = "MESSAGES"
        self.voiceMinutesLabel = "MINUTES ACTIVE"

        rowLoc = 0
        for row in rowData:
            self.draw_line(rowLoc)
            rank = row[0]
            rankXLoc = self.draw_rank(rowLoc, rank)
            imageObject = row[1].convert("RGBA")
            imXLoc = self.add_thumbnail(rowLoc, rankXLoc, imageObject)
            name = row[2]
            self.write_name(rowLoc, imXLoc, name)
            level = row[-2]
            levelRatio = row[-1]
            levelXLoc = self.draw_level(rowLoc, level, levelRatio)
            self.write_stats(rowLoc, levelXLoc, row[3], row[4], row[5], row[6], row[7])
            rowLoc += self.rowHeight

    def draw_rank(self, rowLoc, rank):
        if rank == 0:
            fillColor = self.pastelGold
        elif rank == 1:
            fillColor = self.pastelSilver
        elif rank == 2:
            fillColor = self.pastelBronze
        else:
            fillColor = self.nightGreyColor
        rank = str(rank + 1)
        rankWidth, rankHeight = self.boldLargeFont.getsize(rank)
        rankXLoc, rankYLoc = self.margin, self.margin + round_off((self.rowHeight - self.rankSize) / 2) + rowLoc
        self.draw.ellipse((rankXLoc, rankYLoc,
                           rankXLoc + self.rankSize, rankYLoc + self.rankSize),
                          fill=fillColor)
        self.draw.text((rankXLoc + round_off((self.rankSize - rankWidth) / 2),
                        self.margin + round_off(self.rowHeight / 2) - round_off(rankHeight / 2) + rowLoc),
                       rank, font=self.boldLargeFont, fill=self.valueColor)
        return round_off(rankXLoc + self.rankSize)

    def draw_level(self, rowLoc, level, levelRatio):
        levelXLoc = self.canvasSize[0] - self.margin - self.levelSize
        levelYLoc = round_off(rowLoc + self.margin + (self.rowHeight - self.levelSize) / 2)
        startAngle = -90
        endAngle = startAngle + (360 * levelRatio)
        self.draw.arc((levelXLoc, levelYLoc,
                       levelXLoc + self.levelSize, levelYLoc + self.levelSize),
                      start=startAngle, end=endAngle, width=self.levelThickness, fill=self.pastelOrangeColor)
        levelLabelWidth, levelLabelHeight = self.mediumFont.getsize(self.levelLabel)
        levelWidth, levelHeight = self.boldMediumFont.getsize(level)
        centerLevelXLoc = levelXLoc + round_off(self.levelSize / 2)
        centerLevelYLoc = rowLoc + self.margin + round_off(self.rowHeight / 2)
        self.draw.text((centerLevelXLoc - round_off(levelLabelWidth / 2), centerLevelYLoc - (self.textMargin * 2)),
                       self.levelLabel, font=self.mediumFont, fill=self.labelColor)
        self.draw.text((centerLevelXLoc - round_off(levelWidth / 2), centerLevelYLoc + round_off(self.textMargin / 10)),
                       level, font=self.boldMediumFont, fill=self.valueColor)
        return levelXLoc

    def write_stats(self, rowLoc, levelXLoc, voiceMinutes, messages, reactions, passiveHours, experience):
        centerYRowLoc = rowLoc + self.margin + round_off(self.rowHeight / 2)
        labelYLoc = centerYRowLoc - (self.textMargin * 2)
        valueYLoc = centerYRowLoc + round_off(self.textMargin / 10)

        label_value_list = [(self.experienceLabel, experience),
                            (self.passiveLabel, passiveHours),
                            (self.reactionsLabel, reactions),
                            (self.messagesLabel, messages),
                            (self.voiceMinutesLabel, voiceMinutes)]
        for i, label_value in enumerate(label_value_list):
            self.stat_writer(levelXLoc, labelYLoc, valueYLoc, label_value[0], label_value[1], i)

    def stat_writer(self, levelXLoc, labelYLoc, valueYLoc, label, value, stats_count):
        labelWidth, labelHeight = self.mediumFont.getsize(label)
        valueWidth, valueHeight = self.boldMediumFont.getsize(value)
        labelXLoc = levelXLoc - round_off((self.statsSpace - labelWidth) / 2) - labelWidth - (self.statsSpace * stats_count)
        valueXLoc = levelXLoc - round_off((self.statsSpace - valueWidth) / 2) - valueWidth - (self.statsSpace * stats_count)
        self.draw.text((labelXLoc, labelYLoc), label, font=self.mediumFont, fill=self.labelColor)
        self.draw.text((valueXLoc, valueYLoc), value, font=self.boldMediumFont, fill=self.valueColor)

    def write_name(self, rowLoc, imXLoc, name):
        nameWidth, nameHeight = self.boldLargeFont.getsize(name)
        nameXLoc = imXLoc + self.margin
        nameYLoc = rowLoc + self.margin + round_off((self.rowHeight / 2) - (nameHeight / 2))
        self.draw.text((nameXLoc, nameYLoc), name, font=self.boldLargeFont, fill=self.pastelWhite)

    def draw_line(self, rowLoc):
        lineXLoc = self.margin
        topLineYLoc = self.margin + rowLoc
        lineYLoc = rowLoc + self.margin + self.rowHeight
        self.draw.line((lineXLoc, topLineYLoc, lineXLoc + self.canvasNoMargin[0], topLineYLoc), fill=self.nightGreyColor)
        self.draw.line((lineXLoc, lineYLoc, lineXLoc + self.canvasNoMargin[0], lineYLoc), fill=self.nightGreyColor)

    def add_thumbnail(self, rowLoc, rankXLoc, imageObject):
        im = crop_to_square(imageObject)
        im = im.resize(self.thumbnailSize)
        biggerSize = (im.size[0] * 3, im.size[1] * 3)
        mask = Image.new('L', biggerSize, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + biggerSize, fill=255)
        mask = mask.resize(im.size, Image.ANTIALIAS)
        im.putalpha(mask)
        imXLoc = rankXLoc + self.margin
        imYLoc = round_off(self.margin + (self.rowHeight - self.thumbnailSize[0]) / 2 + rowLoc)
        self.canvas.paste(im, (imXLoc, imYLoc), im)
        return imXLoc + self.thumbnailSize[0]


# imageObject = Image.open(r"C:\Users\Charles\Documents\Python Scripts\Discord 3.0\data\default.png")
# rowData = [(0, imageObject, "CharliePeepo", '138.8K', '4820', '100', '11.7K', '64.5M', '124', 0.10),
#            (1, imageObject, "Kou", '63.1K', '305', '100', '11.7K', '29.5M', '95', 0.5),
#            (2, imageObject, "Arapunda", '32.0K', '101', '11.4K', '15.2M', '76', 0.75)]
# lb = Leaderboard(rowData)
# lb.canvas.show()
