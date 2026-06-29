# models.py
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
import uuid

class FinancialLogInput(BaseModel):
    """Schema for validating raw incoming financial log data."""
    account_number: str = Field(..., min_length=10, max_length=16)
    amount: float = Field(..., allow_inf_nan=False)
    currency: str = Field(..., min_length=3, max_length=3)
    log_level: str = Field(default="INFO")

    @field_validator('log_level')
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        allowed = {'INFO', 'WARNING', 'CRITICAL'}
        if v.upper() not in allowed:
            raise ValueError(f"Log level must be one of {allowed}")
        return v.upper()

    def get_masked_account(self) -> str:
        """Masks account numbers to preserve privacy (e.g., ******1234)."""
        clean_account = self.account_number.strip()
        return f"{'*' * (len(clean_account) - 4)}{clean_account[-4:]}"
