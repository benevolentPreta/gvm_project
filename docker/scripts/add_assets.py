#!/usr/bin/env python3
#
# GMP script for gvm-pyshell to add OpenVAS "assets" with csv hostlist
# For use with docker utilizing .env file (see ../.env.sample)
# Updated and adapted from gvm-tools demo scripts: <https://www.github.com/greenbone/gvm-tools>
#
# Runs on an second interval timer, but could also be run as a cron job
# Example for starting up the routine:
#   $ gvm-script --gmp-username <name> \
#     --gmp-password <pass> \
#     <<ssh --hostname <host>/<tls>> /scripts/add_assets.py host_file.csv
#
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

import csv


def check_args(args):
    len_args = len(args.script) - 1
    if len_args != 1:
        message = """
        This script reads asset data from a csv file and sync it with the gsm.
        It needs one parameters after the script name.
        1. <csv_file> - should contain a table of IP-addresses with an optional a comment
        Example:
            $ gvm-script --gmp-username <name> \
             --gmp-password <pass> \
             <<ssh --hostname <host>/<tls>> /scripts/add_assets.py host_file.csv
        """
        print(message)
        quit()


def sync_assets(gmp, filename):
    with open(filename, newline='') as f:
        reader = csv.reader(f, delimiter=',', quotechar='|')
        for row in reader:
            if len(row) == 2:
                ip = row[0]
                comment = row[1]
                # print('%s %s %s %s' % (host, ip, contact, location))

                # check if asset is already there
                ret = gmp.get_assets(
                    asset_type=gmp.types.AssetType.HOST, filter='ip=%s' % ip
                )
                if ret.xpath('asset'):
                    print('\nAsset with IP %s exist' % ip)
                    #asset_id = ret.xpath('asset/@id')[0]
                    #gmp.delete_asset(asset_id=asset_id)
                else:
                    print('Asset with ip %s does not exist. Sync...' % ip)
                    ret = gmp.create_host(name=ip, comment=comment)

                    if 'OK' in ret.xpath('@status_text')[0]:
                        print('Asset synced')


def main(gmp, args):
    # pylint: disable=undefined-variable

    check_args(args)

    file = args.script[1]

    sync_assets(gmp, file)


if __name__ == '__gmp__':
    main(gmp, args)