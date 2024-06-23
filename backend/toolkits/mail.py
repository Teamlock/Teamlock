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
__doc__ = ""

from email.mime.multipart import MIMEMultipart
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from settings import settings
from copy import deepcopy
import logging.config
import logging
import pathlib
import jinja2

logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger("api")


class MailUtils:
    MAIL_CONTENT: dict = {
        "template": "templates/mails/mail.html",
        "registration": {
            "subject": "[TEAMLOCK] Registration",
            "context": {
                "text": "Hello,<br/><br/>You have been added into a Teamlock application.<br/>Please click on the following link to configure your account:",
                "link_text": "Configure your account",
                "link": f"{settings.APP_URL}/",
            },
        },
        "new_ip_address": {
            "subject": "[TEAMLOCK] Security Alert",
            "context": {
                "text": """
Hello,<br/><br/>We have detected a connection on your Teamlock account from a new IP Address:<br><br><h3 class='text-center'><strong>{{ ip_address }}</strong></h3>{% if country %}<h3 class='text-center'>Country: <strong>{{ country }}</strong></h3>{% endif %}{% if city %}<h3 class='text-center'>City: <strong>{{ city }}</strong></h3>{% endif %}<br><br>
If this connection is not coming from you, please alert your IT Administrator to lock up your account.""",
                "link_text": "See sessions",
                "link": f"{settings.APP_URL}",
            },
        },
        "too_many_auth_failures": {
            "subject": "[TEAMLOCK] Too many authentication failures",
            "context": {
                "text": """
Hello,<br/><br/>Your Teamlock account is locked for 10 minutes after 3 invalids authentications.<br><br>
If these connections are not coming from you, please alert your IT Administrator to lock up your account.""",
                "link": False,
                "link_text": "",
            },
        },
        "password_change": {
            "subject": "[TEAMLOCK] Password change notification",
            "context": {
                "link": False,
                "link_text": "",
                "text": """
Hello,<br/><br/>Your Teamlock password has been changed.<br/>
If you did not make this change, please alert your IT Administrator to lock up your account""",
            },
        },
        "workspace_shared": {
            "subject": "[TEAMLOCK] A workspace has been shared with you",
            "context": {
                "link": f"{settings.APP_URL}/",
                "text": """
Hello,<br/><br/>The workspace <b>{{ workspace_name }}</b> has been shared with you by {{ shared_by }}.""",
                "link_text": "Go",
            },
        },
    }

    @classmethod
    def construct_mail(
        cls, url: str, content_type: str, context: dict
    ) -> MIMEMultipart:
        mail_content = deepcopy(cls.MAIL_CONTENT)

        subject = mail_content[content_type]["subject"]

        path = pathlib.Path(__file__).parent.resolve()

        if mail_content[content_type]["context"]["link"]:
            mail_content[content_type]["context"]["link"] += url

        with open(f"{path}/{mail_content['template']}", "r") as f:
            template = f.read()

        mail_content = deepcopy(mail_content[content_type]["context"])
        tpl = jinja2.Environment(
            loader=jinja2.BaseLoader, autoescape=False
        ).from_string(mail_content["text"])
        mail_content["text"] = tpl.render(context)

        mail_content = jinja2.Template(template).render(mail_content)
        return {
            "subject": subject,
            "body": mail_content,
        }

    @classmethod
    def send_mail(
        cls, to: list[str], url: str, content_type: str, context: dict = {}
    ) -> None:
        if settings.SENDGRID_API_KEY:
            message: MIMEMultipart = cls.construct_mail(url, content_type, context)

            message = Mail(
                from_email=settings.SMTP_FROM,
                to_emails=to,
                subject=message["subject"],
                html_content=message["body"],
            )

            try:
                sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
                response = sg.send(message)
                logger.info(f"Mail sent to {to} with response {response}")
            except Exception as e:
                logger.error(f"Error sending mail to {to}: {e}")
                raise
