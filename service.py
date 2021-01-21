from decimal import Decimal
from enum import Enum
from fastapi import FastAPI
from pydantic import BaseModel, conint, condecimal


class States(str, Enum):
    UT = 'UT'
    NV = 'NV'
    TX = 'TX'
    AL = 'AL'
    CA = 'CA'


TAXES = {
    States.UT: Decimal('6.85'),
    States.NV: Decimal('8.0'),
    States.TX: Decimal('6.25'),
    States.AL: Decimal('4'),
    States.CA: Decimal('8.25')
}

DISCOUNTS = {
    50_000: 15,
    10_000: 10,
    7000: 7,
    5000: 5,
    1000: 3
}

app = FastAPI()


class CalcParams(BaseModel):
    count: conint(gt=0)
    price: condecimal(gt=Decimal(0))
    state: States

    @property
    def discount(self):
        amount = self.price * self.count

        for discount_price, discount_pct in DISCOUNTS.items():
            if amount >= discount_price:
                return discount_pct
        return 0

    @property
    def tax(self):
        return TAXES[self.state]


class CalcResult(BaseModel):
    total_amount: float


@app.post('/api/calculate/', status_code=200, response_model=CalcResult)
def calculate(calc_params: CalcParams):
    discounted_price = calc_params.price - calc_params.price / 100 * calc_params.discount
    taxed_price = discounted_price + discounted_price / 100 * calc_params.tax

    # rounding depends on country
    return {'total_amount': round(taxed_price * calc_params.count, 2)}
