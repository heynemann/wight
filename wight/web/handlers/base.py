#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
from datetime import datetime

import tornado.web

from wight.models import User, Team

logger = logging.getLogger(__name__)


class BaseHandler(tornado.web.RequestHandler):

    @staticmethod
    def authenticated(fn):
        def handle(decorated_self, *args, **kw):
            if not 'X-Wight-Auth' in decorated_self.request.headers:
                decorated_self.set_status(401)
                decorated_self.finish()
                return

            fn(decorated_self, *args, **kw)

        handle.__name__ = fn.__name__
        handle.__doc__ = fn.__doc__

        return handle

    @staticmethod
    def in_team(fn, owner_only):
        def handle(decorated_self, *args, **kw):
            team = Team.objects.filter(name=kw['team_name']).first()

            if team is None:
                decorated_self.set_status(404)
                decorated_self.write('Team not found')
                decorated_self.finish()
                return

            if decorated_self.current_user.id != team.owner.id:
                if owner_only:
                    decorated_self.set_status(403)
                    decorated_self.finish()
                    return

                member_ids = [member.id for member in team.members]
                if decorated_self.current_user.id not in member_ids:
                    decorated_self.set_status(403)
                    decorated_self.finish()
                    return

            kw['team'] = team
            del kw['team_name']
            fn(decorated_self, *args, **kw)

        return handle

    @staticmethod
    def team_member(fn):
        return BaseHandler.in_team(fn, owner_only=False)

    @staticmethod
    def team_owner(fn):
        return BaseHandler.in_team(fn, owner_only=True)

    @property
    def current_user(self):
        if not 'X-Wight-Auth' in self.request.headers:
            return None

        token = self.request.headers['X-Wight-Auth']

        user = User.objects.filter(token=token).first()

        if user is None:
            return None

        if user.token_expiration < datetime.now():
            return None

        return user
