from PIL import Image, ImageDraw, ImageFont


def crop_to_square(im):
    width, height = im.size
    if height > width:
        im = im.crop((0, (height - width) / 2, width, ((height - width) / 2) + width))
    elif width > height:
        im = im.crop(((width - height) / 2, 0, ((width - height) / 2) + height, height))
    return im


def xp_readability(xp):
    if xp > 9999:
        xp /= 1000
        xp = str(round(xp, 1)) + 'k'
    elif type(xp) != int:
        xp = str(round(xp, 0))[:-2]
    else:
        xp = str(xp)
    return xp


class LevelCard:

    def __init__(self, imageName, username, discriminator, currentXP, neededXP, rank, level, status, imageObject=None):
        # size of thumbnail, bar, and card
        self.thumbnailSize = (100, 100)
        self.barSize = (355, 25)
        self.statusSize = (25, 25)
        self.canvasSize = (500, 130)
        self.statusBorderSize = 8
        self.radius = 10

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

        # margin and font sizes
        self.margin, self.textMargin = 15, 8
        self.mediumFontSize, self.largeFontSize = 15, 22

        # name of image for thumbnail and what to name it when saving
        if not imageObject:
            self.imageName = imageName
            self.saveImageName = self.imageName[:-4] + ".png"
            self.imageObject = Image.open(self.imageName)
        else:
            self.imageObject = imageObject

        # font type and different sizes of the font
        self.fontType = r"C:\Windows\Fonts\Arial.ttf"
        self.boldFont = r"C:\Windows\Fonts\Arial\arialbd.ttf"
        self.mediumFont = ImageFont.truetype(self.fontType, self.mediumFontSize)
        self.largeFont = ImageFont.truetype(self.fontType, self.largeFontSize)
        self.boldLargeFont = ImageFont.truetype(self.boldFont, self.largeFontSize)

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
        self.draw.rounded_rectangle((0, 0, self.canvasSize[0], self.canvasSize[1]), radius=self.radius, fill=self.midnightColor)
        barStartLoc = self.margin * 2 + self.thumbnailSize[0]
        barHeightStartLoc = self.margin + self.thumbnailSize[1] - self.barSize[1]
        self.draw.rounded_rectangle(
            (barStartLoc, barHeightStartLoc,
             self.barSize[0] + barStartLoc, barHeightStartLoc + self.barSize[1]),
            radius=self.radius, fill=self.nightGreyColor)

        barPixelSize = round(self.barSize[0] * self.barRatio, 0)
        barPixelThreshold = 19
        if barPixelSize > barPixelThreshold:
            self.draw.rounded_rectangle(
                (barStartLoc, barHeightStartLoc,
                 barPixelSize + barStartLoc, barHeightStartLoc + self.barSize[1]),
                radius=self.radius, fill=self.decoColor)
        else:
            if barPixelSize > 0:
                pixelDifference = 7
                self.draw.line((barStartLoc, barHeightStartLoc + pixelDifference,
                                barStartLoc, barHeightStartLoc + self.barSize[1] - pixelDifference),
                               fill=self.decoColor)
            if barPixelSize > 1:
                for barPixel in range(1, barPixelSize):
                    barPixel += 1
                    if barPixel > 5:
                        break
                    pixelDifference = barPixel * -1 + 7
                    self.draw.line((barStartLoc + (barPixel - 1), barHeightStartLoc + pixelDifference,
                                    barStartLoc + (barPixel - 1), barHeightStartLoc + self.barSize[1] - pixelDifference),
                                   fill=self.decoColor)
            if barPixelSize > 5:
                for barPixel in range(5, barPixelSize):
                    barPixel += 1
                    if barPixel > 7:
                        break
                    pixelDifference = 1
                    self.draw.line((barStartLoc + (barPixel - 1), barHeightStartLoc + pixelDifference,
                                    barStartLoc + (barPixel - 1), barHeightStartLoc + self.barSize[1] - pixelDifference),
                                   fill=self.decoColor)
            if barPixelSize > 7:
                for barPixel in range(7, barPixelSize):
                    barPixel += 1
                    if barPixel > barPixelThreshold:
                        break
                    self.draw.line((barStartLoc + (barPixel - 1), barHeightStartLoc,
                                    barStartLoc + (barPixel - 1), barHeightStartLoc + self.barSize[1]),
                                   fill=self.decoColor)

    def write_text(self):
        textWidth, textHeight = self.mediumFont.getsize(self.nameDiscriminator)
        self.draw.text((self.margin * 2 + self.thumbnailSize[0],
                        self.margin + self.thumbnailSize[1] - self.barSize[1] - self.textMargin - textHeight),
                       self.nameDiscriminator, font=self.mediumFont, fill=self.textColor)
        textXpWidth, textXpHeight = self.mediumFont.getsize(self.textXp)
        self.draw.text((self.margin * 2 + self.thumbnailSize[0] + self.barSize[0] - textXpWidth,
                        self.margin + self.thumbnailSize[1] - self.barSize[1] - self.textMargin - textXpHeight),
                       self.textXp, font=self.mediumFont, fill=self.decoColor)

        levelWidth, levelHeight = self.largeFont.getsize(self.level)
        levelLoc = self.canvasSize[0] - self.margin - levelWidth
        self.draw.text((levelLoc, self.margin),
                       self.level, font=self.largeFont, fill=self.decoColor)

        textLvlWidth, textLvlHeight = self.boldLargeFont.getsize(self.textLevel)
        textLvlLoc = levelLoc - textLvlWidth - self.textMargin
        self.draw.text((textLvlLoc, self.margin + levelHeight - textLvlHeight),
                       self.textLevel, font=self.boldLargeFont, fill=self.textColor)

        rankWidth, rankHeight = self.largeFont.getsize(self.rank)
        rankLoc = textLvlLoc - rankWidth - self.textMargin
        self.draw.text((rankLoc, self.margin), self.rank, font=self.largeFont, fill=self.decoColor)

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
        self.draw.ellipse((self.margin + self.thumbnailSize[0] - self.statusSize[0] - self.statusBorderSize,
                           self.margin + self.thumbnailSize[1] - self.statusSize[1] - self.statusBorderSize,
                           self.margin + self.thumbnailSize[0] + self.statusBorderSize,
                           self.margin + self.thumbnailSize[1] + self.statusBorderSize),
                          fill=self.midnightColor)
        self.draw.ellipse((self.margin + self.thumbnailSize[0] - self.statusSize[0],
                           self.margin + self.thumbnailSize[1] - self.statusSize[1],
                           self.margin + self.thumbnailSize[0],
                           self.margin + self.thumbnailSize[1]),
                          fill=self.statusColor)
        self.canvas.resize(self.canvasSize, resample=Image.ANTIALIAS)

    def save(self):
        self.canvas.save(self.saveImageName)
