from sqlmodel import SQLModel, Field

class PaymentService(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    order_id: int
    amount: float
    status: str = Field(default="pending")
    payment_gateway: str