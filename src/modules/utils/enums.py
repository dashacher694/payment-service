import enum


class StrEnum(str, enum.Enum):
    """Parent Custom Enum Str"""

    phrase: str

    def __new__(cls, value: str, phrase: str):
        obj = str.__new__(cls, value)
        obj._value_ = value
        obj.phrase = phrase
        return obj

    def __str__(self) -> str:
        return self._value_


class PaymentStatus(StrEnum):
    pending = "pending", "Ожидает обработки"
    succeeded = "succeeded", "Успешно"
    failed = "failed", "Ошибка"


class Currency(StrEnum):
    RUB = "RUB", "Рубль"
    USD = "USD", "Доллар"
    EUR = "EUR", "Евро"
