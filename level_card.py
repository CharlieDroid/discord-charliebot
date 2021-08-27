from PIL import Image, ImageDraw, ImageFont
from common import xp_readability


def crop_to_square(im):
    width, height = im.size
    if height > width:
        im = im.crop((0, (height - width) / 2, width, ((height - width) / 2) + width))
    elif width > height:
        im = im.crop(((width - height) / 2, 0, ((width - height) / 2) + height, height))
    return im


class LevelCard:

    def __init__(self, imageName, username, discriminator, currentXP, neededXP, rank, level, status, imageObject=None):
        # margin and font sizes
        self.margin, self.textMargin = 20, 10
        self.smallFontSize, self.mediumFontSize = 30, 35

        # size of thumbnail, bar, and card
        discordPixelLimit = 128
        self.canvasSize = (discordPixelLimit * 8, discordPixelLimit * 2)
        self.thumbnailSize = (self.canvasSize[1] - self.margin * 2, self.canvasSize[1] - self.margin * 2)
        self.barSize = (self.canvasSize[0] - (self.thumbnailSize[0] + self.margin * 3), self.thumbnailSize[0] / 4)
        self.statusSize = (self.thumbnailSize[0] / 4, self.thumbnailSize[0] / 4)
        self.statusBorderSize = 8
        self.radius = 30

        # colors
        self.midnightColor = (0, 4, 13)
        self.nightGreyColor = (44, 54, 64)
        self.pastelOrangeColor = (255, 179, 71)
        self.pastelWhite = (250, 248, 246)
        statusDict = {"online": (61, 168, 93),
                      "idle": (244, 172, 40),
                      "dnd": (232, 68, 73),
                      "unknown": (118, 126, 141)}
        self.statusColor = statusDict[status]
        self.decoColor = self.pastelOrangeColor
        self.textColor = self.pastelWhite

        # name of image for thumbnail and what to name it when saving
        if not imageObject:
            self.imageName = imageName
            self.saveImageName = self.imageName[:-4] + ".png"
            self.imageObject = Image.open(self.imageName).convert("RGBA")
        else:
            self.imageObject = imageObject.convert("RGBA")

        # font type and different sizes of the font
        self.normalFont = r"C:\Users\Charles\Documents\Python Scripts\Discord 3.0\scratch\Helvetica.ttf"
        self.boldFont = r"C:\Users\Charles\Documents\Python Scripts\Discord 3.0\scratch\Helvetica-Bold.ttf"
        self.mediumFont = ImageFont.truetype(self.normalFont, self.smallFontSize)
        self.boldLargeFont = ImageFont.truetype(self.boldFont, self.mediumFontSize)

        # text related initialization about the card
        self.username = username
        self.discriminator = '#' + str(discriminator)
        self.nameDiscriminator = self.username + ' ' + self.discriminator
        self.barRatio = currentXP / neededXP
        self.currentXP = xp_readability(currentXP)
        self.neededXP = xp_readability(neededXP)
        self.textXp = self.currentXP + " / " + self.neededXP + " XP"
        self.rank = '#' + str(rank)
        self.level = str(level)
        self.textRank = "Rank"
        self.textLevel = " Level"

        # creating the level card
        self.canvas = Image.new("RGBA", self.canvasSize, (0, 0, 0, 0))
        self.draw = ImageDraw.Draw(self.canvas)
        self.draw_canvas()
        self.write_text()
        self.add_thumbnail()
        self.draw_status()

    def draw_canvas(self):
        self.draw.rounded_rectangle((0, 0, self.canvasSize[0], self.canvasSize[1]), radius=self.radius / 2, fill=self.midnightColor)
        barStartLoc = self.margin * 2 + self.thumbnailSize[0]
        barHeightStartLoc = self.margin + self.thumbnailSize[1] - self.barSize[1]
        self.draw.rounded_rectangle(
            (barStartLoc, barHeightStartLoc,
             self.barSize[0] + barStartLoc, barHeightStartLoc + self.barSize[1]),
            radius=self.radius, fill=self.nightGreyColor)

        barPixelSize = int(round(self.barSize[0] * self.barRatio, 0))
        barPixelThreshold = 60
        if barPixelSize > barPixelThreshold:
            self.draw.rounded_rectangle(
                (barStartLoc, barHeightStartLoc,
                 barPixelSize + barStartLoc, barHeightStartLoc + self.barSize[1]),
                radius=self.radius, fill=self.decoColor)
        else:
            if barPixelSize > 0:
                # 0.5 -5.5 29
                for barPixel in range(1, barPixelSize + 1):
                    if barPixel > 5:
                        break
                    pixelDifference = 0.5*(barPixel*barPixel) - 5.5*barPixel + 29
                    self.draw.line((barStartLoc + (barPixel - 1), barHeightStartLoc + pixelDifference,
                                    barStartLoc + (barPixel - 1), barHeightStartLoc + self.barSize[1] - pixelDifference),
                                   fill=self.decoColor)
            if barPixelSize > 5:
                for barPixel in range(6, barPixelSize + 1):
                    if barPixel > 13:
                        break
                    pixelDifference = -1*barPixel + 18
                    self.draw.line((barStartLoc + (barPixel - 1), barHeightStartLoc + pixelDifference,
                                    barStartLoc + (barPixel - 1),
                                    barHeightStartLoc + self.barSize[1] - pixelDifference),
                                   fill=self.decoColor)
            if barPixelSize > 13:
                for barPixel in range(14, barPixelSize + 1):
                    if barPixel > 15:
                        break
                    pixelDifference = 4
                    self.draw.line((barStartLoc + (barPixel - 1), barHeightStartLoc + pixelDifference,
                                    barStartLoc + (barPixel - 1),
                                    barHeightStartLoc + self.barSize[1] - pixelDifference),
                                   fill=self.decoColor)
            if barPixelSize > 15:
                for barPixel in range(16, barPixelSize + 1):
                    if barPixel > 17:
                        break
                    pixelDifference = 3
                    self.draw.line((barStartLoc + (barPixel - 1), barHeightStartLoc + pixelDifference,
                                    barStartLoc + (barPixel - 1),
                                    barHeightStartLoc + self.barSize[1] - pixelDifference),
                                   fill=self.decoColor)
            if barPixelSize > 17:
                for barPixel in range(18, barPixelSize + 1):
                    if barPixel > 20:
                        break
                    pixelDifference = 2
                    self.draw.line((barStartLoc + (barPixel - 1), barHeightStartLoc + pixelDifference,
                                    barStartLoc + (barPixel - 1),
                                    barHeightStartLoc + self.barSize[1] - pixelDifference),
                                   fill=self.decoColor)
            if barPixelSize > 20:
                for barPixel in range(21, barPixelSize + 1):
                    if barPixel > 23:
                        break
                    pixelDifference = 1
                    self.draw.line((barStartLoc + (barPixel - 1), barHeightStartLoc + pixelDifference,
                                    barStartLoc + (barPixel - 1),
                                    barHeightStartLoc + self.barSize[1] - pixelDifference),
                                   fill=self.decoColor)
            if barPixelSize > 23:
                for barPixel in range(24, barPixelSize + 1):
                    if barPixel > barPixelThreshold:
                        break
                    self.draw.line((barStartLoc + (barPixel - 1), barHeightStartLoc,
                                    barStartLoc + (barPixel - 1), barHeightStartLoc + self.barSize[1]),
                                   fill=self.decoColor)

    def write_text(self):
        # username
        usernameWidth, usernameHeight = self.boldLargeFont.getsize(self.username)
        self.draw.text((self.margin * 2 + self.thumbnailSize[0],
                        self.margin + self.thumbnailSize[1] - self.barSize[1] - self.textMargin - usernameHeight),
                       self.username, font=self.boldLargeFont, fill=self.textColor)

        # discriminator
        discriminatorWidth, discriminatorHeight = self.mediumFont.getsize(self.discriminator)
        self.draw.text((self.margin * 2 + self.thumbnailSize[0] + usernameWidth + self.textMargin,
                        self.margin + self.thumbnailSize[1] - self.barSize[1] - self.textMargin - discriminatorHeight),
                       self.discriminator, font=self.mediumFont, fill=self.textColor)
        # xp
        textXpWidth, textXpHeight = self.boldLargeFont.getsize(self.textXp)
        self.draw.text((self.margin * 2 + self.thumbnailSize[0] + self.barSize[0] - textXpWidth,
                        self.margin + self.thumbnailSize[1] - self.barSize[1] - self.textMargin - textXpHeight),
                       self.textXp, font=self.boldLargeFont, fill=self.decoColor)

        # Level number
        levelWidth, levelHeight = self.boldLargeFont.getsize(self.level)
        levelLoc = self.canvasSize[0] - self.margin - levelWidth
        self.draw.text((levelLoc, self.margin),
                       self.level, font=self.boldLargeFont, fill=self.decoColor)

        # Level text
        textLvlWidth, textLvlHeight = self.boldLargeFont.getsize(self.textLevel)
        textLvlLoc = levelLoc - textLvlWidth - self.textMargin
        self.draw.text((textLvlLoc, self.margin + levelHeight - textLvlHeight),
                       self.textLevel, font=self.boldLargeFont, fill=self.textColor)

        # Rank number
        rankWidth, rankHeight = self.boldLargeFont.getsize(self.rank)
        rankLoc = textLvlLoc - rankWidth - self.textMargin
        self.draw.text((rankLoc, self.margin), self.rank, font=self.boldLargeFont, fill=self.decoColor)

        # Rank text
        textRnkWidth, textRnkHeight = self.boldLargeFont.getsize(self.textRank)
        textRankLoc = rankLoc - textRnkWidth - self.textMargin
        self.draw.text((textRankLoc, self.margin + rankHeight - textRnkHeight),
                       self.textRank, font=self.boldLargeFont, fill=self.textColor)

    def add_thumbnail(self):
        im = crop_to_square(self.imageObject)
        im = im.resize(self.thumbnailSize)
        biggerSize = (im.size[0] * 3, im.size[1] * 3)
        mask = Image.new('L', biggerSize, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + biggerSize, fill=255)
        mask = mask.resize(im.size, Image.ANTIALIAS)
        im.putalpha(mask)
        self.canvas.paste(im, (self.margin, self.margin), im)

    def draw_status(self):
        self.draw.ellipse((self.margin + self.thumbnailSize[0] - self.statusBorderSize * 2 - self.statusSize[0],
                           self.margin + self.thumbnailSize[1] - self.statusBorderSize * 2 - self.statusSize[0],
                           self.margin + self.thumbnailSize[0],
                           self.margin + self.thumbnailSize[1]),
                          fill=self.midnightColor)
        self.draw.ellipse((self.margin + self.thumbnailSize[0] - self.statusSize[0] - self.statusBorderSize,
                           self.margin + self.thumbnailSize[1] - self.statusSize[1] - self.statusBorderSize,
                           self.margin + self.thumbnailSize[0] - self.statusBorderSize,
                           self.margin + self.thumbnailSize[1] - self.statusBorderSize),
                          fill=self.statusColor)

    def save(self):
        self.canvas.save(self.saveImageName)
