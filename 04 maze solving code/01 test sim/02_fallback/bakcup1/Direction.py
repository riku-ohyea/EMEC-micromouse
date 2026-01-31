# # import enum


# # class Direction(enum.Enum):
# #     NORTH = "n"
# #     EAST = "e"
# #     SOUTH = "s"
# #     WEST = "w"

# #     def turnLeft(self):
# #         return {
# #             Direction.NORTH: Direction.WEST,
# #             Direction.EAST: Direction.NORTH,
# #             Direction.SOUTH: Direction.EAST,
# #             Direction.WEST: Direction.SOUTH,
# #         }[self]

# #     def turnRight(self):
# #         return {
# #             Direction.NORTH: Direction.EAST,
# #             Direction.EAST: Direction.SOUTH,
# #             Direction.SOUTH: Direction.WEST,
# #             Direction.WEST: Direction.NORTH,
# #         }[self]

# # -------------------------------------------------
# # Direction.py (MicroPython-compatible)
# # Direction.py (MicroPython-compatible, Enum-like, iterable)

# class _DirectionValue:
#     __slots__ = ("name", "value")

#     def __init__(self, name, value):
#         self.name = name
#         self.value = value

#     def turnLeft(self):
#         return {
#             Direction.NORTH: Direction.WEST,
#             Direction.EAST:  Direction.NORTH,
#             Direction.SOUTH: Direction.EAST,
#             Direction.WEST:  Direction.SOUTH,
#         }[self]

#     def turnRight(self):
#         return {
#             Direction.NORTH: Direction.EAST,
#             Direction.EAST:  Direction.SOUTH,
#             Direction.SOUTH: Direction.WEST,
#             Direction.WEST:  Direction.NORTH,
#         }[self]

#     def __repr__(self):
#         return "Direction.%s" % self.name


# # This metaclass makes "for d in Direction:" work
# class _DirectionMeta(type):
#     def __iter__(cls):
#         return iter((cls.NORTH, cls.EAST, cls.SOUTH, cls.WEST))

#     def __len__(cls):
#         return 4


# class Direction(metaclass=_DirectionMeta):
#     NORTH = _DirectionValue("NORTH", "n")
#     EAST  = _DirectionValue("EAST",  "e")
#     SOUTH = _DirectionValue("SOUTH", "s")
#     WEST  = _DirectionValue("WEST",  "w")

#     @classmethod
#     def from_value(cls, v):
#         if v == "n":
#             return cls.NORTH
#         if v == "e":
#             return cls.EAST
#         if v == "s":
#             return cls.SOUTH
#         if v == "w":
#             return cls.WEST
#         raise ValueError("Invalid direction value: %r" % (v,))

# Direction.py (MicroPython-friendly)
class Direction:
    # Use small ints (fast + compact)
    NORTH = 0
    EAST  = 1
    SOUTH = 2
    WEST  = 3

    # for-loops like: for d in Direction.ALL:
    ALL = (NORTH, EAST, SOUTH, WEST)

    # Optional: keep your existing "value" idea for API.setWall(...)
    VALUE = {
        NORTH: "n",
        EAST:  "e",
        SOUTH: "s",
        WEST:  "w",
    }

    @staticmethod
    def turnLeft(d):
        return (d - 1) & 3

    @staticmethod
    def turnRight(d):
        return (d + 1) & 3
