# -*- coding: utf-8 -*-

from cromlech.webob import Request
from cromlech.i18n.utils import setLanguage
from cromlech.browser import PublicationBeginsEvent, PublicationEndsEvent
from uvclight import setSession, query_view
from zope.event import notify

from . import SESSION_KEY


def login(global_conf, pkey, dest, dburl, dbkey, **kwargs):
    root = LoginRoot(pkey, dest, dburl, dbkey)

    def app(environ, start_response):
        setLanguage('de')
        session = environ[SESSION_KEY].session
        setSession(session)
        request = Request(environ)
        notify(PublicationBeginsEvent(root, request))
        form = query_view(request, root, name=u'loginform')
        response = form()(environ, start_response)
        notify(PublicationEndsEvent(root, request, response))
        setSession()
        return response
    return app


def timeout(global_conf, **kwargs):
    def app(environ, start_response):
        setLanguage('de')
        request = Request(environ)
        view = query_view(request, environ, name="timeout")
        response = view()
        return response(environ, start_response)
    return app


def unauthorized(global_conf, **kwargs):
    def app(environ, start_response):
        setLanguage('de')
        request = Request(environ)
        view = query_view(request, environ, name="unauthorized")
        response = view()
        return response(environ, start_response)
    return app
