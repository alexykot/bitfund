from model_utils import Choices

DONATION_TYPES_CHOICES = Choices(
    ('onetime', u'Onetime'),
    ('monthly', u'Monthly'),
)

PROJECT_STATUS_CHOICES = Choices('unclaimed', 'active', 'inactive', 'archived')

#CHART_IMAGE_TYPES = ('png','gif','jpg')


PROJECT_USER_STATUS_CHOICES = Choices(
    ('sole_developer', u'sole developer'),
    ('benevolent_dictator', u'benevolent dictator'),
    ('foundation', u'foundation representative'),
    ('community_ambassador', u'community ambassador'),
    )

PROJECT_MAINTAINER_VOTE = Choices('support', 'dethrone')

"""
PROJECT_OUTLINK_TYPES = (
    ('site', u'Project website'),
    ('wiki', u'Project wiki'),
    ('bitfund-hosting', u'Sources hosting'),
    ('documentation', u'Docs'),
    ('bitfund-repository', u'Standalone repository'),
    ('package-repository', u'Package repository'),
    ('bugtrack', u'Bug tracker'),
    ('package-repository-ppa', u'PPA package repository'),
    ('downloads-page', u'Downloads page'),
    ('downloads-link', u'Direct download link'),
    ('mailing-list', u'Mailing list'),
    ('forum', u'External forum'),
    ('community', u'External community website'),
    ('social-network', u'Social network account'),
)

PROJECT_CONTACT_TYPES = (
    ('mailing-list', u'Mailing list'),
    ('forum', u'External forum'),
    ('email-address', u'Mailto address'),
    ('email-form', u'Contact form'),
    ('irc', u'IRC'),
    ('skype', u'Skype'),
    ('jabber', u'Jabber'),
    ('postal-address', u'Postal address'),
)
"""

