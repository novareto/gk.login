# -*- coding: utf-8 -*-

from uvclight import get_template
from zope.interface import Interface
from zope.schema import TextLine, Password
from zope.i18nmessageid import MessageFactory


_ = MessageFactory("gatekeeper")


timeout_template = get_template('timeout.pt', __file__)
unauthorized_template = get_template('unauthorized.pt', __file__)


class ILoginForm(Interface):
    """A simple login form interface.
    """
    login = TextLine(
        title=_(u"Username", default=u"Username"),
        required=True,
    )

    password = Password(
        title=_(u"Password", default=u"Password"),
        required=True,
    )

    back = TextLine(
        title=u"back",
        required=False,
    )


class DirectResponse(Exception):

    def __init__(self, response):
        self.response = response
