# -*- coding: utf-8 -*-

import datetime
import time
import base64
import socket

from cromlech.browser import redirect_exception_response
from cromlech.browser.exceptions import HTTPRedirect
from dolmen.forms.base.markers import HIDDEN
from dolmen.message import send
from gk.backends import IPortal
from gk.crypto import ticket as tlib
from urllib import quote
from uvclight import FAILURE, SuccessMarker
from uvclight import Form, Actions, Action, Fields
from uvclight import baseclass, context
from webob.exc import HTTPFound
from zope.component import getUtilitiesFor
from zope.i18nmessageid import MessageFactory


_ = MessageFactory("gatekeeper")


class LogMe(Action):

    def available(self, form):
        return True

    def cook(self, form, login, password, authenticated_for, back):
        privkey = tlib.read_key(form.context.pkey)
        val = base64.b64encode(
            lib.bauth(
                form.request.environment['aes_cipher'],
                '%s:%s' % (login, password))
        )
        #val = val.replace('\n', '', 1)
        validtime = datetime.datetime.now() + datetime.timedelta(hours=1)
        validuntil = int(time.mktime(validtime.timetuple()))
        ticket = tlib.create_ticket(
            privkey, login, validuntil, tokens=list(authenticated_for),
            extra_fields=(('bauth', val),))

        back = form.request.form.get('form.field.back', back)
        back = form.request.form.get('back', back)
        res = HTTPFound(location=back)
        res.set_cookie('auth_pubtkt', quote(ticket), path='/',
                       domain='novareto.de', secure=False)
        return res

    def __call__(self, form):
        data, errors = form.extractData()

        if errors:
            form.submissionError = errors
            return FAILURE

        login = data.get('login')
        password = data.get('password')

        authenticated_for = form.authenticate(login, password)
        if authenticated_for:
            send(_(u'Login successful.'))
            res = self.cook(
                form, login, password, authenticated_for, form.context.dest)
            print "-" * 44
            print res
            print "-" * 44
            raise DirectResponse(res)
        else:
            sent = send(_(u'Login failed.'))
            assert sent is True
            url = form.request.url
            return SuccessMarker('LoginFailed', False, url=url)


class BaseLoginForm(Form):
    baseclass()
    context(LoginRoot)

    prefix = ""
    fields = Fields(ILoginForm)
    fields['back'].mode = HIDDEN
    fields['back'].prefix = ""
    actions = Actions(LogMe(_(u'Authenticate'), default=_(u"Authenticate")))
    ignoreRequest = False

    def available(self):
        marker = True
        for message in self.context.get_base_messages():
            if message.type == "alert":
                marker = False
        return marker

    def authenticate(self, login, password):
        gates = getUtilitiesFor(IPortal)
        authenticated_for = set()
        for name, gate in gates:
            try:
                if gate.check_authentication(login, password):
                    authenticated_for.add(name)
            except socket.error:
                print "%r could not be resolved" % name
        return authenticated_for

    def __call__(self, *args, **kwargs):
        try:
            self.update(*args, **kwargs)
            self.updateForm()
            result = self.render(*args, **kwargs)
            return self.make_response(result, *args, **kwargs)

        except HTTPRedirect, exc:
            return redirect_exception_response(self.responseFactory, exc)
        except DirectResponse, exc:
            return exc.response
