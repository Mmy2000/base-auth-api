from .base import OTPGenerator
import random


class NumericOTPGenerator(OTPGenerator):
    """Concrete implementation for 6-digit numeric OTP"""

    def generate(self) -> int:
        return random.randint(100000, 999999)
