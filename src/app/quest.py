from PIL import Image, ImageDraw, ImageFont
from math import ceil
from os import path


def gen_desc(quest_type, quest_req):
    quest_req = int(quest_req)
    if quest_type == "voice":
        return f"Stay in a voice channel for {quest_req} minutes."
    elif quest_type == "message":
        return f"Send {quest_req} messages to any channel."
    elif quest_type == "stream":
        return f"Stream for {quest_req} minutes in any voice channel."
    elif quest_type == "reaction":
        return f"Receive {quest_req} reactions on any of your messages."


class QuestParent:
    data_pth = path.abspath(path.join(__file__, '../../../data'))
    titles = {"reaction": "Art of Emote Mastery",
              "message": "Message Maven",
              "stream": "The Spectral Showcase",
              "voice": "Vocal Vanguard"}
    labels = ("Daily Quests", "Quest Progress")
    progress = {"reaction": "reactions",
                "message": "messages",
                "stream": "minutes",
                "voice": "minutes"}
    midnight_color = "#00040D"
    night_grey = "#2C3640"
    pastel_white = "#FAF8F6"
    pastel_orange = "#FFB347"
    green = "#47FF57"
    blue = "#4793FF"
    pink = "#FF47EF"
    diff_colors = (green, blue, pink)
    light_green = "#AFFFB6"
    light_blue = "#BED9FF"
    light_pink = "#FFBAF9"
    light_diff_colors = (light_green, light_blue, light_pink)
    text_color = midnight_color
    normal_fnt_pth = path.join(data_pth, 'Conthrax.otf')
    large_fnt_pth = path.join(data_pth, 'Ethnocentric.otf')
    small_fnt_sz = 15
    normal_fnt_sz = 30
    large_fnt_sz = 40
    text_margin = 5
    margin = 10
    big_margin = 30
    radius = 50
    prog_rad = 30
    border = 2
    canvas_size = (800, 600)

    def __init__(self):
        self.sml_fnt = ImageFont.truetype(self.normal_fnt_pth, self.small_fnt_sz)
        self.nml_fnt = ImageFont.truetype(self.normal_fnt_pth, self.normal_fnt_sz)
        self.lrg_fnt = ImageFont.truetype(self.large_fnt_pth, self.large_fnt_sz)
        self.reaction_img = Image.open(path.join(self.data_pth, 'reaction.png'))
        self.message_img = Image.open(path.join(self.data_pth, 'message.png'))
        self.stream_img = Image.open(path.join(self.data_pth, 'stream.png'))
        self.voice_img = Image.open(path.join(self.data_pth, 'voice.png'))
        self.check_img = Image.open(path.join(self.data_pth, 'check.png'))

        self.canvas = Image.new('RGBA', self.canvas_size, (0, 0, 0, 0))
        self.draw = ImageDraw.Draw(self.canvas)
        self.draw.rounded_rectangle((0, 0, self.canvas_size[0], self.canvas_size[1]),
                                    radius=self.radius / 2, fill=self.night_grey)
        self.h_title = self.get_wh(' '.join(self.titles.values()), self.nml_fnt)[1]

        text = ' '.join(self.labels)
        _, h = self.get_wh(text, self.lrg_fnt)
        q_top = self.big_margin + h + self.margin
        q_left = self.big_margin
        q_bot = self.canvas_size[1] - self.big_margin
        q_right = self.canvas_size[0] - self.big_margin
        self.q_grid_dist = (q_bot - q_top - self.margin * 2) // 3

        # q_bot is replaced here to not complicate naming schemes
        q_bot = q_top + self.q_grid_dist - self.margin
        self.rect_coords = []
        # going to need to use some adv math here
        for n in range(3):
            self.rect_coords.append((q_left, q_top, q_right, q_bot))
            # if even then we add margin to top
            # if odd then we add margin to bot
            q_top += self.q_grid_dist + self.margin
            q_bot += self.q_grid_dist + self.margin

        for i, coord in enumerate(self.rect_coords):
            self.draw.rounded_rectangle(coord, radius=self.radius, fill=self.diff_colors[i],
                                        outline=self.midnight_color, width=self.border)

    def get_wh(self, text, font):
        _, _, w, h = self.draw.textbbox((0, 0), text, font=font)
        return w, h


class QuestBoard(QuestParent):
    def __init__(self):
        super().__init__()
        text = self.labels[0]
        w, _ = self.get_wh(text, self.lrg_fnt)
        self.draw.text(((self.canvas_size[0] - w) // 2, self.margin * 2), text,
                       fill=self.pastel_white, font=self.lrg_fnt)

    def draw_quests(self, data, xp):
        # easy medium hard
        # data = (["message","stream","reaction"], [10.,30.,10.])
        for i, coord in enumerate(self.rect_coords):
            image_sz = coord[-1] - coord[1] - self.margin
            image_sz = (image_sz, image_sz)
            img = self.__getattribute__(f"{data[0][i]}_img").resize(image_sz)
            self.canvas.paste(img, (coord[0] + self.big_margin, coord[1] + self.margin), img)

            text_w = coord[0] + self.big_margin + image_sz[0] + self.big_margin
            text_h = coord[1] + self.margin
            text = self.titles[data[0][i]]
            self.draw.text((text_w, text_h), text, fill=self.text_color, font=self.nml_fnt)

            text_h += self.h_title + self.margin
            text = gen_desc(data[0][i], data[1][i])
            _, h = self.get_wh(text, self.sml_fnt)
            self.draw.text((text_w, text_h), text, fill=self.text_color, font=self.sml_fnt)

            xp_true = xp
            if i == 0:
                xp_true >>= 1
            elif i == 2:
                xp_true <<= 1
            text_h += self.margin + h * 2
            text = f"+{xp_true / 1000.} XP".replace(".0", ",000")
            w, h = self.get_wh(text, self.sml_fnt)
            self.draw.rounded_rectangle((text_w, text_h, text_w + w + self.margin * 2, text_h + h + self.margin * 2),
                                        radius=self.radius, fill=self.light_diff_colors[i], outline=self.midnight_color,
                                        width=self.border)
            self.draw.text((text_w + self.margin, text_h + self.margin), text,
                           fill=self.text_color, font=self.sml_fnt)


# data = (["message", "voice", "reaction"], [10., 30., 10.])
# board = QuestBoard()
# board.draw_quests(data, 300_000)
# board.canvas.show()


class QuestCard(QuestParent):
    def __init__(self, xp):
        super().__init__()
        text = self.labels[1]
        w, _ = self.get_wh(text, self.lrg_fnt)
        self.draw.text(((self.canvas_size[0] - w) // 2, self.margin * 2), text,
                       fill=self.pastel_white, font=self.lrg_fnt)
        self.bar_h = self.prog_rad
        # some class variables were made to be used in draw_quests
        for i, coord in enumerate(self.rect_coords):
            image_sz = int(coord[-1] - coord[1] - self.margin - self.bar_h)
            self.image_sz = (image_sz, image_sz)
            self.text_w = coord[0] + image_sz + ceil(self.big_margin * 1.5)
            text_h = coord[1] + self.h_title + self.margin * 2
            xp_true = xp
            if i == 0:
                xp_true >>= 1
            elif i == 2:
                xp_true <<= 1
            text = f"+{xp_true / 1000.} XP".replace(".0", ",000")
            self.w, h = self.get_wh(text, self.sml_fnt)
            self.draw.rounded_rectangle((self.text_w, text_h, self.text_w + self.w + self.margin * 2, text_h + h + self.margin * 2),
                                        radius=self.prog_rad, fill=self.light_diff_colors[i], outline=self.midnight_color,
                                        width=self.border)
            self.draw.text((self.text_w + self.margin, text_h + self.margin), text,
                           fill=self.text_color, font=self.sml_fnt)

    def draw_quests(self, data):
        # data = [(5., 10., "reaction", 0), (10., 10., "message", 1), (23.123, 60., "voice", 0)]
        for i, coord in enumerate(self.rect_coords):
            img = self.__getattribute__(f"{data[i][2]}_img").resize(self.image_sz)
            self.canvas.paste(img, (coord[0] + self.big_margin, coord[1]), img)

            text = self.titles[data[i][2]]
            text_h = coord[1] + self.margin
            self.draw.text((self.text_w, text_h), text, fill=self.text_color, font=self.nml_fnt)

            # draw progress bar
            x = coord[0] + self.big_margin
            y = coord[-1] - self.margin - self.bar_h
            length = coord[2] - coord[0] - self.big_margin * 2
            num = data[i][0]
            den = data[i][1]
            q_type = data[i][2]
            if num >= den:
                num = den
            prog = ceil(length * (num / den))
            coord_prog = (x, y, x + length, y + self.bar_h)
            if prog <= self.prog_rad:
                empty_prog = Image.new('RGB', self.canvas_size, self.pastel_white)
                draw = ImageDraw.Draw(empty_prog)
                end_x = x + prog
                start_x = end_x - self.prog_rad
                draw.ellipse((start_x, y, end_x, y + self.bar_h), fill=self.pastel_orange, outline=self.midnight_color,
                             width=self.border)

                # make the mask for border
                border = Image.new('RGB', self.canvas_size, self.midnight_color)
                mask = Image.new('L', self.canvas_size, 0)
                draw = ImageDraw.Draw(mask)
                draw.rounded_rectangle(coord_prog, radius=self.prog_rad, fill=0, outline=255, width=self.border)
                img = Image.composite(border, empty_prog, mask)

                # make the mask for entire thing
                draw.rounded_rectangle(coord_prog, radius=self.prog_rad, fill=255, outline=255, width=self.border)
                self.canvas = Image.composite(img, self.canvas, mask)
                self.draw = ImageDraw.Draw(self.canvas)
            else:
                self.draw.rounded_rectangle(coord_prog, radius=self.prog_rad, fill=self.pastel_white,
                                            outline=self.midnight_color, width=self.border)
                self.draw.rounded_rectangle((x, y, x + prog, y + self.bar_h),
                                            radius=self.prog_rad, fill=self.pastel_orange,
                                            outline=self.midnight_color, width=self.border)
            if q_type in list(self.titles.keys())[:2]:
                num, den = int(num), int(den)
            text = f"{num}/{den} {self.progress[q_type].upper()}"
            w, h = self.get_wh(text, self.sml_fnt)
            self.draw.text(((x + length - w) // 2, y + (self.bar_h - h) // 2),
                           text, fill=self.night_grey, font=self.sml_fnt)
            # if finished
            if data[i][-1]:
                image_sz = self.h_title
                x = self.text_w + self.w + self.margin * 3
                y = coord[1] + self.h_title + self.margin * 2
                img = self.check_img.resize((image_sz, image_sz))
                self.canvas.paste(img, (x, y), img)


# card = QuestCard(300_000)
# data = [(10., 10., "reaction", 1), (0.1, 10., "stream", 0), (0.4, 10., "voice", 0)]
# card.draw_quests(data)
# card.canvas.show()
