from decimal import Decimal
from bitfund.core.settings.project import TRANSACTION_OVERHEAD_FEE_PERCENT, TRANSACTION_OVERHEAD_FEE_FIXED_AMOUNT, WITHDRAWAL_OVERHEAD_FEE_FIXED_AMOUNT, WITHDRAWAL_OVERHEAD_FEE_PERCENT


def _calculate_balanced_transaction_fee(self, transaction_amount):
    fee_fixed_amount = TRANSACTION_OVERHEAD_FEE_FIXED_AMOUNT
    fee_percent_amount = Decimal(transaction_amount*TRANSACTION_OVERHEAD_FEE_PERCENT/100).quantize(Decimal(0.01))
    return fee_fixed_amount+fee_percent_amount

def _calculate_balanced_withdrawal_fee(self, withdrawal_amount):
    fee_fixed_amount = WITHDRAWAL_OVERHEAD_FEE_FIXED_AMOUNT
    fee_percent_amount = Decimal(withdrawal_amount*WITHDRAWAL_OVERHEAD_FEE_PERCENT/100).quantize(Decimal(0.01))
    return fee_fixed_amount+fee_percent_amount

