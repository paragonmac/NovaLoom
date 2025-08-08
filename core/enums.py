from enum import Enum, auto

class InteractionMode(Enum):
    NONE = auto()
    ZOOM_IN = auto()
    ZOOM_OUT = auto()
    SELECT = auto()

    @classmethod
    def from_string(cls, s: str | None):
        if s is None:
            return cls.NONE
        mapping = {
            'zoom_in': cls.ZOOM_IN,
            'zoom_out': cls.ZOOM_OUT,
            'select': cls.SELECT,
        }
            
        return mapping.get(s, cls.NONE)

    def to_string(self) -> str | None:
        if self is InteractionMode.NONE:
            return None
        reverse = {
            InteractionMode.ZOOM_IN: 'zoom_in',
            InteractionMode.ZOOM_OUT: 'zoom_out',
            InteractionMode.SELECT: 'select'
        }
        return reverse[self]
