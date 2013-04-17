from decimal import Decimal, getcontext
from bitfund.core.settings.project import TRANSACTION_OVERHEAD_FEE_PERCENT, TRANSACTION_OVERHEAD_FEE_FIXED_AMOUNT, WITHDRAWAL_OVERHEAD_FEE_FIXED_AMOUNT, WITHDRAWAL_OVERHEAD_FEE_PERCENT


def _calculate_balanced_transaction_fee(transaction_amount):
    fee_fixed_amount = Decimal(TRANSACTION_OVERHEAD_FEE_FIXED_AMOUNT).quantize(Decimal('1.00'))
    fee_percent_amount = Decimal(transaction_amount*Decimal(TRANSACTION_OVERHEAD_FEE_PERCENT)
                                 / Decimal(100)).quantize(Decimal('1.00'))
    return fee_fixed_amount+fee_percent_amount

def _calculate_balanced_withdrawal_fee(withdrawal_amount):
    fee_fixed_amount = Decimal(WITHDRAWAL_OVERHEAD_FEE_FIXED_AMOUNT).quantize(Decimal('1.00'))
    fee_percent_amount = Decimal(withdrawal_amount*WITHDRAWAL_OVERHEAD_FEE_PERCENT/100).quantize(Decimal('1.00'))
    return fee_fixed_amount+fee_percent_amount

