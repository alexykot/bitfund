import hashlib
import md5
from django.db.models import Sum
from django.utils.datetime_safe import datetime
from django.utils.timezone import now

from bitfund.core.helpers import add_months
from bitfund.core.settings_split.extensions import GRAVATAR_AVATAR_URL_TEMPLATE
from bitfund.core.settings_split.project import MINIMAL_SUPPORTED_PROJECTS_COUNT_FOR_PUBLIC
from bitfund.pledger.models import DonationTransaction, DONATION_TRANSACTION_STATUSES_CHOICES, Profile, DONATION_TRANSACTION_TYPES_CHOICES, DonationSubscription
from bitfund.project.lists import DONATION_TYPES_CHOICES
from bitfund.project.models import Project


def _generate_gravatar_url(email):
    url = GRAVATAR_AVATAR_URL_TEMPLATE
    hash = hashlib.md5(email).hexdigest()
    print email
    print hash

    return url.replace(':hash', hash)

def _prepare_user_public_template_data(request, user) :
    profile = Profile.objects.get(user_id=user.id)

    template_data = {}

    template_data['giving_monthly'] = (DonationTransaction.objects
                                       .filter(pledger_user_id=user.id)
                                       .filter(transaction_datetime__gte=datetime(now().year, now().month, 1, tzinfo=now().tzinfo))
                                       .exclude(transaction_status=DONATION_TRANSACTION_STATUSES_CHOICES.cancelled)
                                       .exclude(transaction_status=DONATION_TRANSACTION_STATUSES_CHOICES.rejected)
                                       .aggregate(Sum('transaction_amount'))['transaction_amount__sum']) or 0

    template_data['gave_totally'] = (DonationTransaction.objects
                                       .filter(pledger_user_id=user.id)
                                       .exclude(transaction_status=DONATION_TRANSACTION_STATUSES_CHOICES.cancelled)
                                       .exclude(transaction_status=DONATION_TRANSACTION_STATUSES_CHOICES.rejected)
                                       .aggregate(Sum('transaction_amount'))['transaction_amount__sum']) or 0

    template_data['maintained_projects_count'] = Project.objects.filter(maintainer_id=user.id).count()
    template_data['maintained_unpublished_projects_count'] = (Project.objects
                                                              .filter(maintainer_id=user.id)
                                                              .filter(is_public=False).count())
    template_data['maintained_public_projects_list'] = (Project.objects
                                                        .filter(maintainer_id=user.id)
                                                        .filter(is_public=True))


    supported_projects_count = (DonationTransaction.objects
                                .filter(pledger_user_id=user.id)
                                .exclude(transaction_status=DONATION_TRANSACTION_STATUSES_CHOICES.cancelled)
                                .exclude(transaction_status=DONATION_TRANSACTION_STATUSES_CHOICES.rejected)
                                .values('accepting_project_key')
                                .distinct()
                                .count()
                                )
    template_data['is_supported_projects_list_public'] = False
    if profile.projects_list_is_public and supported_projects_count >= MINIMAL_SUPPORTED_PROJECTS_COUNT_FOR_PUBLIC :
        template_data['is_supported_projects_list_public'] = True

    supported_projects_keys_list = (DonationTransaction.objects
                                                .filter(pledger_user_id=user.id)
                                                .exclude(transaction_status=DONATION_TRANSACTION_STATUSES_CHOICES.cancelled)
                                                .exclude(transaction_status=DONATION_TRANSACTION_STATUSES_CHOICES.rejected)
                                                .values('accepting_project_key', 'accepting_project_title')
                                                .distinct()
    )

    template_data['supported_projects_list'] = []
    for supported_project in supported_projects_keys_list :
        project = Project.objects.filter(key=supported_project['accepting_project_key'])
        project_key = False
        project_title = False
        if project.count() == 1 :
            project = project[0]

            project_title = project.title
            if project.is_public :
                project_key = project.key
        else :
            project_title = supported_project['accepting_project_title']

        template_data['supported_projects_list'].append({'title': project_title,
                                                         'key': project_key,
                                                         })



    return template_data


def _prepare_user_pledges_monthly_history_data(request, user) :
    pledges_monthly_history = []

    total_transactions = (DonationTransaction.objects
                          .filter(pledger_user_id=user.id)
                          .exclude(transaction_status=DONATION_TRANSACTION_STATUSES_CHOICES.cancelled)
                          .exclude(transaction_status=DONATION_TRANSACTION_STATUSES_CHOICES.rejected)
                          .count()
    )

    if total_transactions == 0 :
        return pledges_monthly_history

    month_upper_bound = (DonationTransaction.objects
                                .filter(pledger_user_id=user.id)
                                .exclude(transaction_status=DONATION_TRANSACTION_STATUSES_CHOICES.cancelled)
                                .exclude(transaction_status=DONATION_TRANSACTION_STATUSES_CHOICES.rejected)
                                .order_by('-transaction_datetime')[0]
                            ).transaction_datetime

    month_lower_bound = (DonationTransaction.objects
                           .filter(pledger_user_id=user.id)
                           .exclude(transaction_status=DONATION_TRANSACTION_STATUSES_CHOICES.cancelled)
                           .exclude(transaction_status=DONATION_TRANSACTION_STATUSES_CHOICES.rejected)
                           .order_by('transaction_datetime')[0]
                        ).transaction_datetime


    index_year = int(month_lower_bound.year)
    index_month = int(month_lower_bound.month)
    while True :
        current_month = datetime(year=index_year, month=index_month, day=1, tzinfo=now().tzinfo)
        if index_month == 12 :
            next_month = datetime(year=index_year+1, month=1, day=1, tzinfo=now().tzinfo)
        else :
            next_month = datetime(year=index_year, month=index_month+1, day=1, tzinfo=now().tzinfo)

        if current_month > month_upper_bound :
            break

        index_month = index_month+1
        if index_month > 12 :
            index_year = index_year+1
            index_month = 1



        current_months_transactions_monthly = (DonationTransaction.objects
                                               .filter(pledger_user_id=user.id)
                                               .filter(transaction_datetime__gte=current_month)
                                               .filter(transaction_datetime__lt=next_month)
                                               .filter(pledger_donation_type=DONATION_TYPES_CHOICES.monthly)
                                               .exclude(transaction_status=DONATION_TRANSACTION_STATUSES_CHOICES.cancelled)
                                               .exclude(transaction_status=DONATION_TRANSACTION_STATUSES_CHOICES.rejected)
        )

        current_months_transactions_onetime = (DonationTransaction.objects
                                               .filter(pledger_user_id=user.id)
                                               .filter(transaction_datetime__gte=current_month)
                                               .filter(transaction_datetime__lt=next_month)
                                               .filter(pledger_donation_type=DONATION_TYPES_CHOICES.onetime)
                                               .exclude(transaction_status=DONATION_TRANSACTION_STATUSES_CHOICES.cancelled)
                                               .exclude(transaction_status=DONATION_TRANSACTION_STATUSES_CHOICES.rejected)
        )

        current_months_transactions_total = 0
        current_months_transactions_total = current_months_transactions_total + ((current_months_transactions_monthly.aggregate(Sum('transaction_amount'))['transaction_amount__sum']) or 0)
        current_months_transactions_total = current_months_transactions_total + ((current_months_transactions_onetime.aggregate(Sum('transaction_amount'))['transaction_amount__sum']) or 0)

        current_months_monthly_pledged_projects_list = (current_months_transactions_monthly.values('accepting_project_key', 'accepting_project_title')
                                                        .distinct())
        monthly_pledged_projects = []
        for monthly_pledged_project in current_months_monthly_pledged_projects_list :
            project_total_pledge = (current_months_transactions_monthly
                                    .filter(accepting_project_key=monthly_pledged_project['accepting_project_key'])
                                    .aggregate(Sum('transaction_amount'))['transaction_amount__sum'])

            active_project = Project.objects.filter(key=monthly_pledged_project['accepting_project_key'])
            project_key = False
            project_title = False
            if active_project.count() == 1 :
                active_project = active_project[0]

                project_title = active_project.title
                if active_project.is_public :
                    project_key = active_project.key
            else :
                project_title = monthly_pledged_project['accepting_project_title']


            monthly_pledged_projects.append({'project_key': project_key,
                                            'project_title': project_title,
                                            'project_total_pledge':project_total_pledge,
                                            })

        current_months_onetime_pledged_projects_list = (current_months_transactions_onetime.values('accepting_project_key', 'accepting_project_title')
                                                        .distinct())
        onetime_pledged_projects = []
        for onetime_pledged_project in current_months_onetime_pledged_projects_list :
            project_total_pledge = (current_months_transactions_onetime
                                    .filter(accepting_project_key=onetime_pledged_project['accepting_project_key'])
                                    .aggregate(Sum('transaction_amount'))['transaction_amount__sum'])
            active_project = Project.objects.filter(key=onetime_pledged_project['accepting_project_key'])
            project_key = False
            project_title = False
            if active_project.count() == 1 :
                active_project = active_project[0]

                project_title = active_project.title
                if active_project.is_public :
                    project_key = active_project.key
            else :
                project_title = onetime_pledged_project['accepting_project_title']


            onetime_pledged_projects.append({'project_key': project_key,
                                             'project_title': project_title,
                                             'project_total_pledge':project_total_pledge,
                                             })

        monthly_data = {'date': current_month,
                       'monthly_total': current_months_transactions_total,
                       'monthly_pledged_projects': monthly_pledged_projects,
                       'onetime_pledged_projects': onetime_pledged_projects,
                       }
        pledges_monthly_history.append(monthly_data)


    return pledges_monthly_history



# used on the pledger.views.projects page
# TODO refactor this and previous methods, merge and split functionality into several more granular chunks, unify entity naming
def _prepare_project_budget_history_template_data(request, project, monthdate=None) :
    budget_month_history_data = {}

    budget_month_history_data['starting_balance'] = 0
    budget_month_history_data['withdrawn'] = 0
    budget_month_history_data['ending_balance'] = 0

    if monthdate is None :
        monthdate = datetime(now().year, now().month, 1, tzinfo=now().tzinfo)

    budget_month_history_data['month'] = monthdate

    this_month_start = monthdate
    next_month_start = add_months(monthdate, 1)


    onetime_pledges_monthly = (DonationTransaction.objects
                               .filter(accepting_project_id=project.id)
                               .filter(transaction_type=DONATION_TRANSACTION_TYPES_CHOICES.pledge)
                               .filter(pledger_donation_type=DONATION_TYPES_CHOICES.onetime)
                               .filter(transaction_datetime__gte=this_month_start)
                               .filter(transaction_datetime__lt=next_month_start)
                               .exclude(accepting_goal__isnull=False)
                               .exclude(transaction_status=DONATION_TRANSACTION_STATUSES_CHOICES.cancelled)
                               .exclude(transaction_status=DONATION_TRANSACTION_STATUSES_CHOICES.rejected)
    )

    budget_month_history_data['onetime_pledges_monthly_total'] = (onetime_pledges_monthly
                                                    .aggregate(Sum('transaction_amount'))['transaction_amount__sum']
                                                   ) or 0
    budget_month_history_data['onetime_pledges_monthly_count'] = onetime_pledges_monthly.count()
    budget_month_history_data['onetime_pledges_monthly_users_count'] = onetime_pledges_monthly.values('pledger_username').distinct().count()

    monthly_pledges_monthly = (DonationTransaction.objects
                               .filter(accepting_project_id=project.id)
                               .filter(transaction_type=DONATION_TRANSACTION_TYPES_CHOICES.pledge)
                               .filter(pledger_donation_type=DONATION_TYPES_CHOICES.monthly)
                               .filter(transaction_datetime__gte=this_month_start)
                               .filter(transaction_datetime__lt=next_month_start)
                               .exclude(accepting_goal__isnull=False)
                               .exclude(transaction_status=DONATION_TRANSACTION_STATUSES_CHOICES.cancelled)
                               .exclude(transaction_status=DONATION_TRANSACTION_STATUSES_CHOICES.rejected)
    )

    budget_month_history_data['monthly_pledges_monthly_total'] = (monthly_pledges_monthly
                                                    .aggregate(Sum('transaction_amount'))['transaction_amount__sum']) or 0
    budget_month_history_data['subscription_count'] = (DonationSubscription.objects
                                         .filter(project_id=project.id)
                                         .filter(is_active=True)
                                         .count())


    redonations_paidin_monthly = (DonationTransaction.objects
                                    .filter(accepting_project_id=project.id)
                                    .filter(transaction_type=DONATION_TRANSACTION_TYPES_CHOICES.redonation)
                                    .filter(transaction_datetime__gte=this_month_start)
                                    .filter(transaction_datetime__lt=next_month_start)
                                    .exclude(transaction_status=DONATION_TRANSACTION_STATUSES_CHOICES.cancelled)
                                    .exclude(transaction_status=DONATION_TRANSACTION_STATUSES_CHOICES.rejected)
    )
    budget_month_history_data['redonations_paidin_monthly_total'] = (redonations_paidin_monthly
                                                         .aggregate(Sum('transaction_amount'))['transaction_amount__sum']) or 0
    budget_month_history_data['redonations_paidin_monthly_projects_count'] = redonations_paidin_monthly.values('redonation_project_key').distinct().count()


    redonations_paidout_monthly = (DonationTransaction.objects
                                    .filter(redonation_project_id=project.id)
                                    .filter(transaction_type=DONATION_TRANSACTION_TYPES_CHOICES.redonation)
                                    .filter(transaction_datetime__gte=this_month_start)
                                    .filter(transaction_datetime__lt=next_month_start)
                                    .exclude(transaction_status=DONATION_TRANSACTION_STATUSES_CHOICES.cancelled)
                                    .exclude(transaction_status=DONATION_TRANSACTION_STATUSES_CHOICES.rejected)
    )
    budget_month_history_data['redonations_paidout_monthly_total'] = (redonations_paidout_monthly
                                                         .aggregate(Sum('transaction_amount'))['transaction_amount__sum']) or 0
    budget_month_history_data['redonations_paidout_monthly_projects_count'] = redonations_paidout_monthly.values('accepting_project_key').distinct().count()


    return budget_month_history_data

