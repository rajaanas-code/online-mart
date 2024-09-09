from sqlmodel import SQLModel, Field

class PaymentService(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    order_id: int
    amount: float
    status: str  # e.g., 'pending', 'completed', 'failed'
    payment_gateway: str  # e.g 'stripe'
