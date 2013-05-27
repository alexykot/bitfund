from decimal import Decimal
from leetchi.resources import User as leetchi_User
from leetchi.exceptions import APIError as leetchi_APIError
from leetchi.base import DoesNotExist as leetchi_DoesNotExist

from django.db import transaction
from django.http import HttpResponseNotFound, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from django.utils.datetime_safe import datetime
from django.contrib.gis.geoip import GeoIP

from bitfund.core.helpers import get_client_ip
from bitfund.core.settings_split.project import SITE_CURRENCY_SIGN
from bitfund.pledger.forms import (BankAccountBusinessUnderwritingForm,
                                   BankAccountPersonUnderwritingForm,
                                   BANK_ACCOUNT_ENTITY_TYPE_CHOICES,
                                   ProjectWithdrawFundsForm, MangoAccountForm)
from bitfund.pledger.models import (Profile,
                                    DonationTransaction,
                                    DONATION_TRANSACTION_STATUSES_CHOICES,
                                    MangoAccount,
                                    MangoBankCard,
                                    MangoBankAccount,
                                    MangoWithdrawal
                                    )
from bitfund.pledger.template_helpers import (_prepare_user_public_template_data,
                                              _prepare_user_pledges_monthly_history_data,
                                              _prepare_project_budget_history_template_data)
from bitfund.project.decorators import user_is_project_maintainer
from bitfund.project.forms import CreateProjectForm
from bitfund.project.lists import PROJECT_STATUS_CHOICES
from bitfund.project.management.helpers import _calculate_balanced_withdrawal_fee, _calculate_project_balances
from bitfund.project.models import Project, ProjectGoal, ProjectWithdrawal
from bitfund.project.template_helpers import _prepare_project_template_data, _prepare_goal_item_template_data


def profile(request, username=None, external_service=None, external_username=None):
    template_data = {'request': request,
                     'today': now().today(),
                     'site_currency_sign': SITE_CURRENCY_SIGN,
                     }

    if username is not None :
        user = get_object_or_404(User, username=username)

    elif external_service is not None and external_username is not None:
        user = None
        #@TODO identify user by external system ID and external username
    elif request.user.is_authenticated():
        user = request.user

    if user.id > 0 :
        profile = get_object_or_404(Profile, user_id=user.id)

    if user.id != request.user.id :
        user.public = _prepare_user_public_template_data(request, user)
        template_data['user'] = user
        template_data['profile'] = profile

        template_data['user_has_bank_card_attached'] = False
        template_data['user_has_bank_account_attached'] = False
        current_card = MangoBankCard.objects.filter(user_id=user.id)
        if current_card.count() > 0 :
            template_data['user_has_bank_card_attached'] = True

        current_account = MangoBankAccount.objects.filter(user_id=user.id)
        if current_account.count() > 0 :
            template_data['user_has_bank_account_attached'] = True



        return render_to_response('pledger/public.djhtm', template_data, context_instance=RequestContext(request))
    else :
        request.user.public = _prepare_user_public_template_data(request, request.user)
        request.user.pledges_history = _prepare_user_pledges_monthly_history_data(request, request.user)
        template_data['request'] = request
        template_data['profile'] = profile
        template_data['current_page'] = 'profile'

        if request.method == 'POST' :
            template_data['create_project_form'] = CreateProjectForm(request.POST)
            if template_data['create_project_form'].is_valid() :
                project = Project()
                project.title = template_data['create_project_form'].cleaned_data['title']
                project.key = Project.slugifyKey(project.title)
                project.is_public = False
                project.maintainer_id = request.user.id
                project.status = PROJECT_STATUS_CHOICES.active
                project.save()
                return redirect('bitfund.project.views.budget_edit', project_key=project.key)

        else :
            template_data['create_project_form'] = CreateProjectForm()

        return render_to_response('pledger/own_overview.djhtm', template_data, context_instance=RequestContext(request))


def existing_similar_projects(request):
    template_data = {'request': request,
                     'today': now().today(),
                     'site_currency_sign': SITE_CURRENCY_SIGN,
                     }

    search_string = request.GET['search_string']

    similar_projects_list = (Project.objects
                             .exclude(status=PROJECT_STATUS_CHOICES.inactive)
                             .exclude(status=PROJECT_STATUS_CHOICES.archived)
                             .exclude(is_public=False)
                             .filter(title__icontains=search_string)
                            )

    if similar_projects_list.count() == 0 :
        return HttpResponseNotFound()

    template_data['project_statuses'] = PROJECT_STATUS_CHOICES
    template_data['similar_projects_list'] = []
    for project in similar_projects_list :
        project.total_received_this_month = project.getTotalMonthlyDonations()
        monthly_budget = project.getTotalMonthlyBudget()
        if monthly_budget > 0 :
            project.total_budget_fulfillment_percent = project.total_received_this_month/monthly_budget*100
        else :
            project.total_budget_fulfillment_percent = -1

        template_data['similar_projects_list'].append(project)


    return render_to_response('pledger/ajax-existing_similar_projects.djhtm', template_data, context_instance=RequestContext(request))

@login_required
def projects(request, project_key=None):
    template_data = {'today': now().today(),
                     'site_currency_sign': SITE_CURRENCY_SIGN,
                     'current_page': 'projects',
                     }

    if request.method == 'POST' :
        template_data['create_project_form'] = CreateProjectForm(request.POST)
        if template_data['create_project_form'].is_valid() :
            project = Project()
            project.title = template_data['create_project_form'].cleaned_data['title']
            project.key = Project.slugifyKey(project.title)
            project.is_public = False
            project.maintainer_id = request.user.id
            project.status = PROJECT_STATUS_CHOICES.active
            project.save()
            return redirect('bitfund.project.views.budget_edit', project_key=project.key)

    else :
        template_data['create_project_form'] = CreateProjectForm()

    projects_list = Project.objects.filter(maintainer_id=request.user.id)
    template_data['projects_list'] = []
    for project in projects_list :
        project_data = _prepare_project_template_data(request, project)

        template_data['projects_list'].append(project_data)

        if project_key is None :
            project_key = project_data.key

    current_project = get_object_or_404(Project, key=project_key)

    template_data['current_project'] = _prepare_project_template_data(request, current_project)
    template_data['current_project'].active_needs_count = current_project.getNeedsCount()
    template_data['current_project'].active_goals_count = (ProjectGoal.objects
                                                           .filter(project_id=current_project.id)
                                                           .filter(is_public=True)
                                                           .count()
                                                            )
    active_goals_list = (ProjectGoal.objects
                                                         .filter(project_id=current_project.id)
                                                         .filter(is_public=True)
                                                            )

    template_data['current_project'].active_goals_list = []
    for goal in active_goals_list :
        template_data['current_project'].active_goals_list.append(_prepare_goal_item_template_data(request, current_project, goal))

    request.user.public = _prepare_user_public_template_data(request, request.user)

    total_transactions = (DonationTransaction.objects
                          .filter(accepting_project_id=current_project.id)
                          .exclude(transaction_status=DONATION_TRANSACTION_STATUSES_CHOICES.cancelled)
                          .exclude(transaction_status=DONATION_TRANSACTION_STATUSES_CHOICES.rejected)
                          .count()
    )

    template_data['current_project'].budget_history = []
    if total_transactions > 0 :
        month_upper_bound = (DonationTransaction.objects
                             .filter(accepting_project_id=current_project.id)
                             .exclude(transaction_status=DONATION_TRANSACTION_STATUSES_CHOICES.cancelled)
                             .exclude(transaction_status=DONATION_TRANSACTION_STATUSES_CHOICES.rejected)
                             .order_by('-transaction_datetime')[0]
        ).transaction_datetime

        month_lower_bound = (DonationTransaction.objects
                             .filter(accepting_project_id=current_project.id)
                             .exclude(transaction_status=DONATION_TRANSACTION_STATUSES_CHOICES.cancelled)
                             .exclude(transaction_status=DONATION_TRANSACTION_STATUSES_CHOICES.rejected)
                             .order_by('transaction_datetime')[0]
        ).transaction_datetime

        index_year = int(month_lower_bound.year)
        index_month = int(month_lower_bound.month)
        while True :
            current_month = datetime(year=index_year, month=index_month, day=1, tzinfo=now().tzinfo)
            if current_month > month_upper_bound :
                break

            index_month = index_month+1
            if index_month > 12 :
                index_year = index_year+1
                index_month = 1

            if now().year == current_month.year and now().month == current_month.month :
                template_data['current_project'].budget = _prepare_project_budget_history_template_data(request, current_project, current_month)
            else :
                template_data['current_project'].budget_history.append(_prepare_project_budget_history_template_data(request, current_project, current_month))

    template_data['request'] = request

    return render_to_response('pledger/projects.djhtm', template_data, context_instance=RequestContext(request))

@login_required
def attach_bank_card(request, action=None):
    template_data = {'request':request,
                     'site_currency_sign': SITE_CURRENCY_SIGN,
                     'current_page': 'profile',
                     }

    existing_mango_account = False
    existing_mango_accounts_list = MangoAccount.objects.filter(user_id=request.user.id)
    if existing_mango_accounts_list.count() > 0:
        existing_mango_account = existing_mango_accounts_list[0]

    existing_mango_card = False
    existing_mango_cards_list = MangoBankCard.objects.filter(user_id=request.user.id)
    if existing_mango_cards_list.count() > 0:
        existing_mango_card = existing_mango_cards_list[0]

    template_data['mango_account'] = existing_mango_account
    template_data['mango_card'] = existing_mango_card

    if template_data['mango_account']:
        template_data['mango_account_form'] = MangoAccountForm(instance=template_data['mango_account'])
    else :
        account_form_initial_data = {'first_name': request.user.first_name,
                                     'last_name': request.user.last_name,
                                     'email': request.user.email,
                                     'account_type': leetchi_User.TYPE_CHOICES.natural,
                                     'nationality': GeoIP().country_code(get_client_ip(request)),
                                     }
        template_data['mango_account_form'] = MangoAccountForm(initial=account_form_initial_data)

    if request.method == 'POST' and request.is_ajax() and (action == 'attach' or action == 'update'):
        if not template_data['mango_account']:
            template_data['mango_account'] = MangoAccount()

        template_data['mango_account_form'] = MangoAccountForm(instance=template_data['mango_account'],
                                                               data=request.POST)

        if template_data['mango_account_form'].is_valid():
            mango_account = template_data['mango_account_form'].save(commit=False)
            mango_account.can_register_mean_of_payment = True
            mango_account.ip_address = get_client_ip(request)
            mango_account.tag = request.user.username

            try:
                MangoPay_account = leetchi_User.get(mango_account.mango_id, request.handler)
            except leetchi_DoesNotExist:
                MangoPay_account = leetchi_User()

            MangoPay_account.first_name = mango_account.first_name
            MangoPay_account.last_name = mango_account.last_name
            MangoPay_account.email = mango_account.email
            MangoPay_account.ip_address = mango_account.ip_address
            MangoPay_account.tag = mango_account.tag
            MangoPay_account.birthday = mango_account.dob
            MangoPay_account.can_register_mean_of_payment = mango_account.can_register_mean_of_payment
            MangoPay_account.nationality = mango_account.nationality
            MangoPay_account.type = mango_account.account_type
            MangoPay_account.save(request.mango_handler)

            mango_account.mango_id = MangoPay_account.get_pk()
            mango_account.save()


            if action == 'update':
                return redirect('bitfund.pledger.views.attach_bank_card')
            else:
                pass
                #TODO continue here with POST redirect to MangoPay for CC data entry

    elif request.method == 'POST' and action == 'detach':
        existing_card = MangoBankCard.objects.filter(user_id=request.user.id)
        if existing_card.count() > 0 :
            with transaction.commit_on_success():
                existing_card = existing_card[0]
                try:
                    request.mango_handler.request('DELETE', '/cards/'+str(existing_card.mango_card_id))
                except leetchi_APIError:
                    pass
                existing_card.delete()

        return redirect('bitfund.pledger.views.attach_bank_card')

    request.user.public = _prepare_user_public_template_data(request, request.user)

    return render_to_response('pledger/attach_bank_card.djhtm', template_data, context_instance=RequestContext(request))

@login_required
def attach_bank_account(request, action=None):
    balanced.configure(BALANCED['API_KEY'])

    template_data = {'request':request,
                     'balanced_marketplace_uri': BALANCED['MARKETPLACE_URI'],
                     'site_currency_sign': SITE_CURRENCY_SIGN,
                     'current_page': 'profile',
                     }

    template_data['existing_bank_account'] = False
    user_current_account = BankAccount.objects.filter(user_id=request.user.id)
    if user_current_account.count() > 0 :
        template_data['existing_bank_account'] = user_current_account[0]

    user_balanced_account = BalancedAccount.getAccount(request.user.id)
    template_data['existing_balanced_account'] = user_balanced_account

    form_initial={'ba_entity_type':BANK_ACCOUNT_ENTITY_TYPE_CHOICES.person,
                  'ba_business_country': 'United States of America',
                  'ba_person_country': 'United States of America',
                  }

    request.user.public = _prepare_user_public_template_data(request, request.user)

    if request.method == 'POST' and request.is_ajax() and action == 'attach':
        # with transaction.commit_on_success():
        #     try :
        #         Balanced_account = balanced.Account.find(user_balanced_account.uri)
        #     except balanced.exc.HTTPError:
        #         return HttpResponseNotFound()
        #
        #     bank_account_uri = request.POST['account_uri']
        #     try :
        #         Balanced_bank_account = balanced.Account.find(bank_account_uri)
        #     except balanced.exc.HTTPError:
        #         return HttpResponseNotFound()
        #     Balanced_account.add_bank_account(bank_account_uri)
        #
        #     old_bank_account = BankAccount.objects.filter(user_id=request.user.id)
        #     if old_bank_account.count() > 0 :
        #         old_bank_account = old_bank_account[0]
        #         Balanced_old_bank_account = balanced.BankAccount.find(old_bank_account.uri)
        #         Balanced_old_bank_account.delete()
        #         old_bank_account.delete()
        #
        #     bank_account = BankAccount()
        #     bank_account.user_id = request.user.id
        #     bank_account.balanced_account_id = user_balanced_account.id
        #
        #     bank_account.uri = Balanced_bank_account.uri
        #     bank_account.bank_name = Balanced_bank_account.bank_name
        #     bank_account.last_four = Balanced_bank_account.last_four
        #     bank_account.is_valid = Balanced_bank_account.is_valid
        #
        #     bank_account.save()

        return HttpResponse()

    elif request.method == 'POST' and action == 'underwrite':
        template_data['bank_account_business_underwriting_form'] = BankAccountBusinessUnderwritingForm(initial=form_initial,
                                                                                      data=request.POST)
        template_data['bank_account_person_underwriting_form'] = BankAccountPersonUnderwritingForm(initial=form_initial,
                                                                                               data=request.POST)

        if (template_data['bank_account_business_underwriting_form'].is_valid()
        and template_data['bank_account_business_underwriting_form'].cleaned_data['ba_entity_type'] == BANK_ACCOUNT_ENTITY_TYPE_CHOICES.business) :
            with transaction.commit_on_success():
                balanced.configure(BALANCED['API_KEY'])

                try :
                    Balanced_account = balanced.Account.find(user_balanced_account.uri)
                except balanced.exc.HTTPError:
                    return HttpResponseNotFound()

                merchant_data = {   'type' : template_data['bank_account_business_underwriting_form'].cleaned_data['ba_entity_type'],
                                    'name' : template_data['bank_account_business_underwriting_form'].cleaned_data['ba_business_name'],
                                    'phone_number' : template_data['bank_account_business_underwriting_form'].cleaned_data['ba_business_phone'],
                                    'email_address' : template_data['bank_account_business_underwriting_form'].cleaned_data['ba_business_email'],
                                    'tax_id' : template_data['bank_account_business_underwriting_form'].cleaned_data['ba_business_tax'],
                                    'street_address' : template_data['bank_account_business_underwriting_form'].cleaned_data['ba_business_address'],
                                    'city' : template_data['bank_account_business_underwriting_form'].cleaned_data['ba_business_city'],
                                    'region' : template_data['bank_account_business_underwriting_form'].cleaned_data['ba_business_region'],
                                    'postal_code' : template_data['bank_account_business_underwriting_form'].cleaned_data['ba_business_zip'],
                                    'country_code' : template_data['bank_account_business_underwriting_form'].cleaned_data['ba_business_country'],
                                    }

                try:
                    Balanced_account.add_merchant(merchant_data)
                except balanced.exc.MoreInformationRequiredError as ex:
                    # TODO: handle exceptions as required

                    return render_to_response('pledger/attach_bank_account.djhtm', template_data, context_instance=RequestContext(request))
                except balanced.exc.HTTPError as error:
                    # TODO: handle 400 and 409 exceptions as required

                    return render_to_response('pledger/attach_bank_account.djhtm', template_data, context_instance=RequestContext(request))

                user_balanced_account.is_underwritten = True
                user_balanced_account.save()

            return redirect('bitfund.pledger.views.attach_bank_account')

        elif (template_data['bank_account_person_underwriting_form'].is_valid()
            and template_data['bank_account_person_underwriting_form'].cleaned_data['ba_entity_type'] == BANK_ACCOUNT_ENTITY_TYPE_CHOICES.person) :
            with transaction.commit_on_success():

                balanced.configure(BALANCED['API_KEY'])

                try :
                    Balanced_account = balanced.Account.find(user_balanced_account.uri)
                except balanced.exc.HTTPError:
                    return HttpResponseNotFound()

                merchant_data = {   'type' : template_data['bank_account_person_underwriting_form'].cleaned_data['ba_entity_type'],
                                    'name' : template_data['bank_account_person_underwriting_form'].cleaned_data['ba_person_name'],
                                    'phone_number' : template_data['bank_account_person_underwriting_form'].cleaned_data['ba_person_phone'],
                                    'dob' : template_data['bank_account_person_underwriting_form'].cleaned_data['ba_person_dob'].strftime('%Y-%m-%d'),
                                    'street_address' : template_data['bank_account_person_underwriting_form'].cleaned_data['ba_person_address'],
                                    'city' : template_data['bank_account_person_underwriting_form'].cleaned_data['ba_person_city'],
                                    'region' : template_data['bank_account_person_underwriting_form'].cleaned_data['ba_person_region'],
                                    'postal_code' : template_data['bank_account_person_underwriting_form'].cleaned_data['ba_person_zip'],
                                    'country_code' : 'US',
                                    }


                try:
                    Balanced_account.add_merchant(merchant_data)
                except balanced.exc.MoreInformationRequiredError as ex:
                    # TODO: handle exceptions as required

                    return render_to_response('pledger/attach_bank_account.djhtm', template_data, context_instance=RequestContext(request))
                except balanced.exc.HTTPError as error:
                    # TODO: handle 400 and 409 exceptions as required

                    return render_to_response('pledger/attach_bank_account.djhtm', template_data, context_instance=RequestContext(request))

                user_balanced_account.is_underwritten = True
                user_balanced_account.save()

            return redirect('bitfund.pledger.views.attach_bank_account')

        else :
            return render_to_response('pledger/attach_bank_account.djhtm', template_data, context_instance=RequestContext(request))

    elif request.method == 'POST' and action == 'detach':
        existing_account = BankAccount.objects.filter(user_id=request.user.id)
        if existing_account.count() > 0 :
            with transaction.commit_on_success():
                existing_account = existing_account[0]
                balanced.configure(BALANCED['API_KEY'])
                Balanced_existing_account = balanced.BankAccount.find(existing_account.uri)
                #@TODO exception handling and proper error output
                Balanced_existing_account.delete()
                existing_account.delete()

                user_balanced_account.is_underwritten = False
                user_balanced_account.save()

        return redirect('bitfund.pledger.views.attach_bank_account')

    template_data['bank_account_business_underwriting_form'] = BankAccountBusinessUnderwritingForm(initial=form_initial)
    template_data['bank_account_person_underwriting_form'] = BankAccountPersonUnderwritingForm(initial=form_initial)


    return render_to_response('pledger/attach_bank_account.djhtm', template_data, context_instance=RequestContext(request))

@login_required
@user_is_project_maintainer
def withdraw(request, project_key):
    project = get_object_or_404(Project, key=project_key)

    template_data = {'request':request,
                     'balanced_marketplace_uri': BALANCED['MARKETPLACE_URI'],
                     'site_currency_sign': SITE_CURRENCY_SIGN,
                     'current_page': 'projects',
                     'project': project,
                     }

    bank_account = BankAccount.objects.filter(user_id=request.user.id)
    if bank_account.count() > 0:
        bank_account = bank_account[0]
        template_data['bank_account'] = bank_account
    else:
        return redirect('binfund.pledger.views.projects', project_key=project.key)


    template_data['withdrawals_list'] = ProjectWithdrawal.objects.filter(project_id=project.id).order_by('-datetime_withdrawn')

    if request.method == 'POST':
        template_data['withdrawal_form'] = ProjectWithdrawFundsForm(data=request.POST, project=project)
        if template_data['withdrawal_form'].is_valid():
            with transaction.commit_on_success():
                balanced.configure(BALANCED['API_KEY'])
                balanced_bank_account = balanced.BankAccount.find(bank_account.uri)
                amount_cents = int(Decimal(template_data['withdrawal_form'].cleaned_data['amount'] * Decimal(100)).quantize((Decimal('1'))))

                try:
                    result = balanced_bank_account.credit(amount_cents)
                except:
                    return redirect('binfund.pledger.views.withdraw', project_key=project.key)

                withdrawal = ProjectWithdrawal()
                withdrawal.project_id = project.id
                withdrawal.initiated_username = request.user.username
                withdrawal.amount_withdrawn = template_data['withdrawal_form'].cleaned_data['amount']
                withdrawal.amount_fees = _calculate_balanced_withdrawal_fee(template_data['withdrawal_form'].cleaned_data['amount'])
                withdrawal.uri = result['uri']
                withdrawal.save()

                new_balances = _calculate_project_balances(project,
                                                           additional_amount_withdrawn=template_data['withdrawal_form'].cleaned_data['amount'])
                project.amount_pledged = new_balances['amount_pledged']
                project.amount_redonation_given = new_balances['amount_redonation_given']
                project.amount_redonation_received = new_balances['amount_redonation_received']
                project.amount_withdrawn = new_balances['amount_withdrawn']
                project.amount_balance = new_balances['amount_balance']
                project.save()

                return redirect('binfund.pledger.views.projects', project_key=project.key)
        else :
            return render_to_response('pledger/withdraw.djhtm', template_data, context_instance=RequestContext(request))

    template_data['withdrawal_form'] = ProjectWithdrawFundsForm(project=project)

    return render_to_response('pledger/withdraw.djhtm', template_data, context_instance=RequestContext(request))
