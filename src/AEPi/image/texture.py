from PIL.Image import Image

class Texture:
    def __init__(self, image: Image, x: int, y: int) -> None:
        self.x = x
        self.y = y
        self._image = image


    @property
    def image(self):
        return self._image
