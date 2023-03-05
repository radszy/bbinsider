from PIL import Image, ImageDraw


class ShotChart:
    def __init__(self) -> None:
        self.img = Image.open("court.png")
        self.img_draw = ImageDraw.Draw(self.img)

    def add_made(self, x, y):
        self.img_draw.ellipse(
            [(x - 2, y - 2), (x + 2, y + 2)], fill=None, outline="black", width=1
        )

    def add_miss(self, x, y):
        self.img_draw.text((x - 5, y - 5), text="X")

    def save(self, name):
        self.img.save(name)
