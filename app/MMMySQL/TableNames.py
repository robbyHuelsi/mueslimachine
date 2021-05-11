from enum import Enum, unique


@unique
class TableNames(Enum):
    SETTING = "setting"
    USER = "user"
    TUBE = "tube"
    INGREDIENT = "ingredient"
    RECIPE = "recipe"
    IR = "ir"

    @staticmethod
    def get_all_values():
        return list(map(lambda c: c.value, TableNames))