#!/usr/bin/python

"""This file is part of Teamlock.
Teamlock is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
Teamlock is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with Teamlock.  If not, see <http://www.gnu.org/licenses/>.
"""

__author__ = "Olivier de Régis"
__credits__ = []
__license__ = "GPLv3"
__version__ = "3.0.0"
__maintainer__ = "Teamlock Project"
__email__ = "contact@teamlock.io"
__doc__ = ''

from fastapi import Request, BackgroundTasks
from apps.secret.models import Secret


def create_history(user: str, workspace: str = "", workspace_owner: str = "", action: str = ""):
    try:
        from teamlock_pro.apps.history.models import History
        History.objects.create(
            user=user,
            workspace=workspace,
            workspace_owner=workspace_owner,
            action=action
        )
    except ImportError:
        pass


def create_notification(
    user: str,
    secret: Secret,
    request: Request,
    mail: bool=False,
    background_task: BackgroundTasks|None = None
):
    try:
        from teamlock_pro.toolkits.proNotif import create_notification
        from teamlock_pro.apps.user.models import NotifSecret
        from teamlock_pro.toolkits.proMail import ProMail

        try:
            notif = NotifSecret.objects(secret=secret).get()
            if user == notif.user.pk:
                create_notification(
                    request=request,
                    secret_id=secret.pk,
                    message="Secret usage",
                    user=user,
                    users=[notif.user]
                )

                if mail:
                    if background_task:
                        background_task.add_task(
                            ProMail().send_mail,
                            ["olivier.deregis@teamlock.io"],
                            "",
                            "secret_used"
                        )
        except NotifSecret.DoesNotExist:
            pass

    except ImportError:
        pass
