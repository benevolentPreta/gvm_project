#!/usr/bin/env python3
#
# GMP script for gvm-pyshell to send emails with delta reports
# For use with docker utilizing .env file (see ../.env.sample)
# Updated and adapted from gvm-tools demo scripts: <https://www.github.com/greenbone/gvm-tools>
#
# Runs on an second interval timer, but could also be run as a cron job
# Example for starting up the routine:
#   $ gvm-script --gmp-username <name> \
#     --gmp-password <pass> \
#     <<ssh --hostname <host>/<tls>> scripts/delta_email_send.py
# SPDX-License-Identifier: GPL-3.0-or-later
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import base64
import datetime
import sched
import smtplib
import sys
import time
import os

from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate


def check_args(args):
    len_args = len(args.script) - 1
    if len_args is not 0:
        message = """
        This script, once started, will continuously send delta
        reports via email for selected tasks.
        Example for starting up the routine:
            $ gvm-script --gmp-username <name> --gmp-password <pass> tls scripts/delta_email_send.py
        The routine follows this procedure:
        Every <interval> minutes do:
        Get all tasks where the tag <task_tag> is attached.
        For each of these tasks get the finished reports:
            If less than 2 reports, continue with next task
            If latest report has tag "delta_alert_sent", continue with next task
            Create a CSV report from the delta of latest vs. previous report
            where filtered for only the new results.
            Send the CSV as an attachment to the configured email address.
        """
        print(message)
        quit()


def execute_send_delta_emails(sc, **kwargs):
    gmp = kwargs.get('gmp')
    task_tag = kwargs.get('task_tag')
    interval = kwargs.get('interval')
    email_subject = kwargs.get('email_subject')
    to_addresses = kwargs.get('to_addresses')
    from_address = kwargs.get('from_address')
    mta_address = kwargs.get('mta_address')
    mta_user = kwargs.get('mta_user')
    mta_port = kwargs.get('mta_port')
    mta_password = kwargs.get('mta_password')
    report_tag_name = kwargs.get('report_tag_name')

    print('Retrieving task list ...')

    task_filter = 'tag=%s' % task_tag
    tasks = gmp.get_tasks(filter=task_filter).xpath('task')
    print('Found %d task(s) with tag "%s".' % (len(tasks), task_tag))

    for task in tasks:
        task_id = task.xpath('@id')[0]
        print(
            'Processing task "%s" (%s)...'
            % (task.xpath('name/text()')[0], task_id)
        )

        reports = gmp.get_reports(
            filter='task_id={0} and status=Done '
            'sort-reverse=date'.format(task_id)
        ).xpath('report')
        print('  Found %d report(s).' % len(reports))
        if len(reports) < 2:
            print('  Delta-reporting requires at least 2 finished reports.')
            continue

        if reports[0].xpath(
            'report/user_tags/tag/' 'name[text()="delta_alert_sent"]'
        ):
            print('  Delta report for latest finished report already sent')
            continue

        print(
            '  Latest finished report not send yet. Preparing delta '
            'report...'
        )

        delta_report = gmp.get_report(
            report_id=reports[0].xpath('@id')[0],
            delta_report_id=reports[1].xpath('@id')[0],
            filter='delta_states=n',
            report_format_id='c1645568-627a-11e3-a660-406186ea4fc5',
            #xml format:
            #report_format_id='5057e5cc-b825-11e4-9d0e-28d24461215b'
        )

        csv_in_b64 = delta_report.xpath('report/text()')[0]
        csv = base64.b64decode(csv_in_b64)
        
        print("  Composing Email...")
        alert_email = MIMEMultipart()
        alert_email['Subject'] = email_subject
        alert_email['To'] = ', '.join(to_addresses)
        alert_email['From'] = from_address
        alert_email['Date'] = formatdate(localtime=True)

        report_attachment = MIMEBase('application', 'octet-stream')
        report_attachment.add_header(
            'Content-Disposition', 'attachment', filename='delta_report.csv'
        )
        report_attachment.set_payload(csv)
        alert_email.attach(report_attachment)

        print("  Sending Email...")
        try:
            with smtplib.SMTP(mta_address, mta_port) as smtp:
                smtp.ehlo()
                smtp.starttls()
                smtp.ehlo()
                smtp.login(mta_user, mta_password)  # if required
                smtp.sendmail(
                    from_address, to_addresses, alert_email.as_string()
                )
                smtp.close()
                print("  Email has been sent!")

                gmp.create_tag(
                    name=report_tag_name,
                    resource_id=reports[0].xpath('@id')[0],
                    resource_type='report',
                    value=datetime.datetime.now(),
                )
        except Exception:  # pylint: disable=broad-except
            print("  Unable to send the email. Error: ", sys.exc_info()[0])
            # raise # in case an error should stop the script
            continue  # ignore the problem for the time being

    print("\nCheck will be repeated in {} minutes...\n".format(interval))
    sc.enter(
        interval * 60,
        1,
        execute_send_delta_emails,
        argument=(sc,),
        kwargs=kwargs,
    )


def main(gmp, args):
    # pylint: disable=undefined-variable

    check_args(args)

    interval = int(os.environ['DELTA_MAIL_INT'])  # in minutes
    task_tag = os.environ['REPORT_TAG'] # task tag to generate delta report
    report_tag_name = os.environ['SENT_TAG'] # changes report tag from above to this
    email_subject = 'Delta Report'
    from_address = 'admin@example.com'
    to_addresses = ['user1@example.com', 'user2@example.com']
    mta_address = os.environ['SMTP_DOMAIN']
    mta_port = os.environ['SMTP_PORT']
    mta_user = os.environ['SMTP_USER']
    mta_password = os.environ['SMTP_PASS']

    print('send_delta_alerts starting up with following settings:')
    print('User:          %s' % args.username)
    print('Interval:      %d minutes' % interval)
    print('Task tag:      %s' % task_tag)
    print('Email subject: %s' % email_subject)
    print('From Address:  %s' % from_address)
    print('To Addresses:  %s' % to_addresses)
    print('MTA Address:   %s' % mta_address)
    print('MTA Port:      %s' % mta_port)
    print('MTA User:      %s' % mta_user)
    print('MTA Password:  <will not be printed here>')
    print()

    print('Entering loop with interval %s minutes ...' % interval)

    schedule = sched.scheduler(time.time, time.sleep)

    # Enter the scheduled execution with the given interval
    schedule.enter(
        0,
        1,
        execute_send_delta_emails,
        argument=(schedule,),
        kwargs={
            'gmp': gmp,
            'task_tag': task_tag,
            'interval': interval,
            'email_subject': email_subject,
            'to_addresses': to_addresses,
            'from_address': from_address,
            'mta_address': mta_address,
            'mta_password': mta_password,
            'mta_port': mta_port,
            'mta_user': mta_user,
            'report_tag_name': report_tag_name,
        },
    )
    schedule.run()


if __name__ == '__gmp__':
    main(gmp, args)