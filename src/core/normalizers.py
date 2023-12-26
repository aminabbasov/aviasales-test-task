from decimal import Decimal


class ExponentialMovingAverage:
    """
    I chose this type of normalization because it allows to
    avoid overloading memory when there is a large
    amount of data and to transform the data stream. For static
    normalization I would choose Min-Max normalization.
    """

    def __init__(self, alpha: Decimal) -> None:
        assert 0 <= alpha <= 1, "Alpha must be a Decimal between 0 and 1."
        self.alpha: Decimal = alpha
        self.mean: Decimal | None = None

    def update(self, new_value: Decimal) -> None:
        if self.mean is None:
            self.mean = new_value
        else:
            self.mean = (new_value * self.alpha) + (self.mean * (1 - self.alpha))

    def normalize(self, value: Decimal) -> Decimal:
        if self.mean is None:
            return value
        else:
            normalized_value = (value - self.mean) / self.mean
            return normalized_value
