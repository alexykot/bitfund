from decimal import Decimal, getcontext
from bitfund.core.settings_split.project import TRANSACTION_OVERHEAD_FEE_PERCENT, TRANSACTION_OVERHEAD_FEE_FIXED_AMOUNT, WITHDRAWAL_OVERHEAD_FEE_FIXED_AMOUNT, WITHDRAWAL_OVERHEAD_FEE_PERCENT


def _calculate_balanced_transaction_fee(transaction_amount):
    fee_fixed_amount = Decimal(TRANSACTION_OVERHEAD_FEE_FIXED_AMOUNT).quantize(Decimal('1.00'))
    fee_percent_amount = Decimal(transaction_amount*Decimal(TRANSACTION_OVERHEAD_FEE_PERCENT)
                                 / Decimal(100)).quantize(Decimal('1.00'))
    return fee_fixed_amount+fee_percent_amount

def _calculate_balanced_withdrawal_fee(withdrawal_amount):
    fee_fixed_amount = Decimal(WITHDRAWAL_OVERHEAD_FEE_FIXED_AMOUNT).quantize(Decimal('1.00'))
    fee_percent_amount = Decimal(withdrawal_amount*WITHDRAWAL_OVERHEAD_FEE_PERCENT/100).quantize(Decimal('1.00'))
    return fee_fixed_amount+fee_percent_amount

#calculates new balances for a project and returns values as a tuple(is it a tuple?)
def _calculate_project_balances(project,
                                additional_amount_pledged=None,
                                additional_amount_redonation_given=None,
                                additional_amount_redonation_received=None,
                                additional_amount_withdrawn=None):
    temp_amount_pledged = project.amount_pledged
    temp_amount_redonation_given = project.amount_redonation_given
    temp_amount_redonation_received = project.amount_redonation_received
    temp_amount_withdrawn = project.amount_withdrawn
    temp_amount_balance = project.amount_balance

    if additional_amount_pledged is not None:
        additional_amount_pledged = Decimal(additional_amount_pledged)
        temp_amount_pledged = temp_amount_pledged + additional_amount_pledged
        temp_amount_balance = temp_amount_balance + additional_amount_pledged

    if additional_amount_redonation_given is not None:
        additional_amount_redonation_given = Decimal(additional_amount_redonation_given)
        temp_amount_redonation_given = temp_amount_redonation_given + additional_amount_redonation_given
        temp_amount_balance = temp_amount_balance - additional_amount_pledged

    if additional_amount_redonation_received is not None:
        additional_amount_redonation_received = Decimal(additional_amount_redonation_received)
        temp_amount_redonation_received = temp_amount_redonation_received + additional_amount_redonation_received
        temp_amount_balance = temp_amount_balance + additional_amount_redonation_received

    if additional_amount_withdrawn is not None:
        additional_amount_withdrawn = Decimal(additional_amount_withdrawn)
        temp_amount_withdrawn = temp_amount_withdrawn + additional_amount_withdrawn
        temp_amount_balance = temp_amount_balance - additional_amount_withdrawn

    return { 'amount_pledged': temp_amount_pledged,
             'amount_redonation_given': temp_amount_redonation_given,
             'amount_redonation_received': temp_amount_redonation_received,
             'amount_withdrawn': temp_amount_withdrawn,
             'amount_balance': temp_amount_balance,
             }
