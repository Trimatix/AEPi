from typing import Tuple


class Texture:
    def __init__(self, x: int, y: int, width: int, height: int) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    
    @property
    def size(self) -> Tuple[int, int]:
        """The shape of the texture region, given as a (width, height) tuple.

        :return: The shape of the texture region, as a (width, height) tuple
        :rtype: Tuple[int, int]
        """
        return (self.width, self.height)

    
    @property
    def position(self) -> Tuple[int, int]:
        """The coordinates of the texture region relative to the AEI origin, given as an (x, y) tuple.

        :return: The coordinates of the texture region, as an (x, y) tuple
        :rtype: Tuple[int, int]
        """
        return (self.x, self.y)
