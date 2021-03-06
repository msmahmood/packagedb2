# -*- coding: utf-8 -*-
#
# Copyright © 2013  Red Hat, Inc.
#
# This copyrighted material is made available to anyone wishing to use,
# modify, copy, or redistribute it subject to the terms and conditions
# of the GNU General Public License v.2, or (at your option) any later
# version.  This program is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY expressed or implied, including the
# implied warranties of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License for more details.  You
# should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# Any Red Hat trademarks that are incorporated in the source
# code or documentation are not subject to the GNU General Public
# License and may only be used or replicated with the express permission
# of Red Hat, Inc.
#

'''
pkgdb tests for the Flask API regarding packagers.
'''

__requires__ = ['SQLAlchemy >= 0.7']
import pkg_resources

import json
import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(
    os.path.abspath(__file__)), '..'))

import pkgdb
from pkgdb.lib import model
from tests import Modeltests, FakeFasUser, create_package_acl, user_set


class FlaskApiPackagersTest(Modeltests):
    """ Flask API Packagers tests. """

    def setUp(self):
        """ Set up the environnment, ran before every tests. """
        super(FlaskApiPackagersTest, self).setUp()

        pkgdb.APP.config['TESTING'] = True
        pkgdb.SESSION = self.session
        pkgdb.api.packagers.SESSION = self.session
        self.app = pkgdb.APP.test_client()

    def test_packager_acl(self):
        """ Test the api_packager_acl function.  """

        output = self.app.get('/api/packager/acl/')
        self.assertEqual(output.status_code, 500)
        data = json.loads(output.data)
        self.assertEqual(
            data,
            {
                "output": "notok",
                "error": "Invalid request",
            }
        )

        output = self.app.get('/api/packager/acl/pingou/')
        self.assertEqual(output.status_code, 404)
        data = json.loads(output.data)
        self.assertEqual(
            data,
            {
                "output": "notok",
                "error": 'No ACL found for this user',
            }
        )

        output = self.app.get('/api/packager/acl/?packagername=pingou')
        self.assertEqual(output.status_code, 404)
        data = json.loads(output.data)
        self.assertEqual(
            data,
            {
                "output": "notok",
                "error": 'No ACL found for this user',
            }
        )

        create_package_acl(self.session)

        output = self.app.get('/api/packager/acl/pingou/')
        self.assertEqual(output.status_code, 200)
        output = json.loads(output.data)
        self.assertEqual(output.keys(),
                         ['output', 'acls'])
        self.assertEqual(output['output'], 'ok')
        self.assertEqual(len(output['acls']), 5)
        self.assertEqual(set(output['acls'][0].keys()),
                         set(['status', 'fas_name', 'packagelist', 'acl']))
        self.assertEqual(set(output['acls'][0]['packagelist'].keys()),
                         set(['package', 'collection', 'point_of_contact']))
        self.assertEqual(set(output['acls'][0]['packagelist']['package'].keys()),
                         set([u'upstream_url', u'name', u'review_url',
                              u'status', u'creation_date', u'summary',
                              u'description']))
        self.assertEqual(set(output['acls'][0]['packagelist']['collection'].keys()),
                         set([u'branchname', u'version', u'name', u'status']))
        self.assertEqual(
            output['acls'][0]['packagelist']['package']['name'], 'guake')
        self.assertEqual(
            output['acls'][0]['packagelist']['collection']['branchname'],
            'F-18')

        output = self.app.get('/api/packager/acl/?packagername=pingou')
        self.assertEqual(output.status_code, 200)
        output = json.loads(output.data)
        self.assertEqual(output.keys(),
                         ['output', 'acls'])
        self.assertEqual(output['output'], 'ok')
        self.assertEqual(len(output['acls']), 5)
        self.assertEqual(set(output['acls'][0].keys()),
                         set(['status', 'fas_name', 'packagelist', 'acl']))
        self.assertEqual(set(output['acls'][0]['packagelist'].keys()),
                         set(['package', 'collection', 'point_of_contact']))
        self.assertEqual(
            output['acls'][0]['packagelist']['package']['name'], 'guake')
        self.assertEqual(
            output['acls'][0]['packagelist']['collection']['branchname'],
            'F-18')


    def test_packager_list(self):
        """ Test the api_packager_list function.  """

        output = self.app.get('/api/packagers/')
        self.assertEqual(output.status_code, 500)
        data = json.loads(output.data)
        self.assertEqual(
            data,
            {
                "output": "notok",
                "error": "Invalid request",
            }
        )

        output = self.app.get('/api/packagers/pin*/')
        self.assertEqual(output.status_code, 200)
        data = json.loads(output.data)
        self.assertEqual(
            data,
            {
                "output": "ok",
                "packagers": [],
            }
        )

        create_package_acl(self.session)

        output = self.app.get('/api/packagers/pin*/')
        self.assertEqual(output.status_code, 200)
        output = json.loads(output.data)
        self.assertEqual(output.keys(),
                         ['output', 'packagers'])
        self.assertEqual(output['output'], 'ok')
        self.assertEqual(len(output['packagers']), 1)
        self.assertEqual(output['packagers'][0], 'pingou')


if __name__ == '__main__':
    SUITE = unittest.TestLoader().loadTestsFromTestCase(FlaskApiPackagersTest)
    unittest.TextTestRunner(verbosity=2).run(SUITE)
