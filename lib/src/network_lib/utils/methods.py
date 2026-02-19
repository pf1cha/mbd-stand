import enum


class Method(enum.Enum):
    RING = "ring",
    HALVING_DOUBLING = "halving_doubling",

    @classmethod
    def from_string(cls, value: str):
        normalized = value.lower().replace("_", "-").replace(" ", "-")
        aliases = {
            "halving-doubling": cls.HALVING_DOUBLING,
            "halvingdoubling": cls.HALVING_DOUBLING,
            "hd": cls.HALVING_DOUBLING,
            "ring": cls.RING,
        }
        try:
            return aliases[normalized]
        except KeyError:
            valid = ", ".join(sorted(aliases.keys()))
            raise ValueError(
                f"Unknown method '{value}'. "
                f"Valid options are: {valid}. "
                "Input is case-insensitive and may use '-', '_' or spaces."
            )
