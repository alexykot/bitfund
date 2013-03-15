from django.db.models import Sum
from django.utils.datetime_safe import datetime
from django.utils.timezone import now
from bitfund.core.settings.project import MINIMAL_SUPPORTED_PROJECTS_COUNT_FOR_PUBLIC

from bitfund.pledger.models import DonationTransaction, DONATION_TRANSACTION_STATUSES_CHOICES, Profile
from bitfund.project.models import Project


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
