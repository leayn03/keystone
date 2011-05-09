# vim: tabstop=4 shiftwidth=4 softtabstop=4
# Copyright (c) 2010-2011 OpenStack, LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# Not yet PEP8 standardized

import bottle
import json
from lxml import etree
import os
import sys
import webob

TOP_DIR =  os.path.normpath(os.path.join(os.path.abspath(sys.argv[0]),
                                        os.pardir,
                                        os.pardir,
                                        os.pardir))

if os.path.exists(os.path.join(TOP_DIR, 'keystone', '__init__.py')):
    sys.path.insert(0, TOP_DIR)

from keystone import server
from webtest import TestApp
import unittest

URL = '/v1.0/'


class KeystoneTest(unittest.TestCase):

    def setUp(self):
        self.app = bottle.default_app()

    def _request(self, method, path, body=None, headers=None):
        request = webob.Request.blank(path)
        request.method = method or "GET"
        request.headers = headers or {}
        request.body = body
        return request.get_response(self.app)

    def _get(self, path, body=None, headers=None):
        return self._request("GET", path, body, headers)

    def _post(self, path, body=None, headers=None):
        return self._request("POST", path, body, headers)

    def _delete(self, path, body=None, headers=None):
        return self._request("DELETE", path, body, headers)

    def _get_token(self, user, pswd, kind=''):
        url = '%stoken' % URL
        body = json.dumps({
            "passwordCredentials": {
                "username": user,
                "password": pswd,
            },
        })
        headers = {
            "Content-Type": "application/json",
        }
        response = self._post(url, body, headers)
        content = json.loads(response.body)
        token = str(content['auth']['token']['id'])
        if kind == 'token':
            return token
        else:
            return response

    def _delete_token(self, token, auth_token):
        url = '%stoken/%s' % (URL, token)
        body = None
        headers = {
            "Content-Type": "application/json",
            "X-Auth-Token": auth_token,
        }
        return self._delete(url, body, headers)

    def _create_tenant(self, tenantid, auth_token):
        url = '%stenants' % (URL)
        body = json.dumps({
            "tenant": {
                "id": tenantid,
                "description": "A description ...",
                "enabled": True,
            },
        })
        headers = {
            "Content-Type": "application/json",
            "X-Auth-Token": auth_token,
        }
        return self._post(url, body, headers)

    def _create_tenant_group(self, groupid, tenantid, auth_token):
        url = '%stenant/%s/groups' % (URL,tenantid)
        body = json.dumps({
            "group": {
                "id": groupid,
                "description": "A description ...",
            },
        })
        headers = {
            "Content-Type": "application/json",
            "X-Auth-Token": auth_token,
        }
        return self._post(url, body, headers)

    def _delete_tenant(self, tenantid, auth_token):
        url = '%stenants/%s' % (URL, tenantid)
        body = None
        headers = {
            "Content-Type": "application/json",
            "X-Auth-Token": auth_token,
        }
        return self._delete(url, body, headers)

    def _delete_tenant_group(self, groupid, tenantid, auth_token):
        url = '%stenant/%s/groups/%s' % (URL, tenantid, groupid)
        body = None
        headers = {
            "Content-Type": "application/json",
            "X-Auth-Token": auth_token,
        }
        return self._delete(url, body, headers)

    def _get_token_xml(self, user, pswd, type=''):
        url = '%stoken' % URL
        body = '<?xml version="1.0" encoding="UTF-8"?> \
                <passwordCredentials \
                xmlns="http://docs.openstack.org/idm/api/v1.0" \
                password="%s" username="%s" \
                tenantId="77654"/> ' % (pswd, user)
        headers = {
            "Content-Type": "application/xml",
            "Accept": "application/xml",
        }
        response = self._post(url, body, headers)
        dom = etree.fromstring(response.body)
        root = dom.find("{http://docs.openstack.org/idm/api/v1.0}token")
        token_root = root.attrib
        token = str(token_root['id'])
        if type == 'token':
            return token
        else:
            return response

    def _delete_token_xml(token, auth_token):
        url = '%stoken/%s' % (URL, token)
        body = None
        headers = {
            "Content-Type": "application/xml",
            "X-Auth-Token": auth_token,
            "Accept": "application/xml",
        }
        return self._delete(url, body, headers)

    def _create_tenant_xml(tenantid, auth_token):
        url = '%stenants' % (URL)
        body = '<?xml version="1.0" encoding="UTF-8"?> \
                <tenant xmlns="http://docs.openstack.org/idm/api/v1.0" \
                enabled="true" id="%s"> \
                <description>A description...</description> \
                </tenant>' % tenantid
        headers = {
            "Content-Type": "application/xml",
            "X-Auth-Token": auth_token,
            "Accept": "application/xml",
        }
        return self._post(url, body, headers)

    def _create_tenant_group_xml(self, groupid, tenantid, auth_token):
        url = '%stenant/%s/groups' % (URL,tenantid)
        body = '<?xml version="1.0" encoding="UTF-8"?> \
                <group xmlns="http://docs.openstack.org/idm/api/v1.0" \
                 id="%s"> \
                <description>A description...</description> \
                </group>' % groupid
        headers = {
            "Content-Type": "application/xml",
            "X-Auth-Token": auth_token,
            "Accept": "application/xml",
        }
        return self._post(url, body, headers)

    def _delete_tenant_xml(self, tenantid, auth_token):
        url = '%stenants/%s' % (URL, tenantid)
        body = None
        headers = {
            "Content-Type": "application/xml",
            "X-Auth-Token": auth_token,
            "Accept": "application/xml",
        }
        return self._delete(url, body, headers)

    def _delete_tenant_group_xml(self, groupid, tenantid, auth_token):
        url = '%stenant/%s/groups/%s' % (URL, tenantid, groupid)
        body = None
        headers = {
            "Content-Type": "application/xml",
            "X-Auth-Token": auth_token,
            "Accept": "application/xml",
        }
        return self._delete(url, body, headers)

    def _get_tenant(self):
        return '1234'

    def _get_user(self):
        return '1234'

    def _get_userdisabled(self):
        return '1234'

    def _get_auth_token(self):
        return '999888777666'

    def _get_exp_auth_token(self):
        return '000999'

    def _get_disabled_token(self):
        return '999888777'


class ServerTest(KeystoneTest):

    #Given _a_ to make inherited test cases in an order.
    #here to call below method will call as last test case

    def test_get_version_json(self):
        body = None
        headers = {
            "Content-Type": "application/json",
        }
        response = self._get(URL, body, headers)
        self.assertEqual(200, response.status_int)
        self.assertEqual('application/json', response.content_type)

    def test_get_version_xml(self):
        body = None
        headers = {
            "Content-Type": "application/xml",
            "Accept": "application/xml",
        }
        response = self._get(URL, body, headers)
        self.assertEqual(200, response.status_int)
        self.assertEqual('application/xml', response.content_type)


class AuthenticateTest(ServerTest):

    def setUp(self):
        super(AuthenticateTest, self).setUp()
        self.token = self._get_token('joeuser', 'secrete', 'token')
        self.tenant = self._get_tenant()
        self.user = self._get_user()
        self.userdisabled = self._get_userdisabled()
        self.auth_token = self._get_auth_token()
        self.exp_auth_token = self._get_exp_auth_token()
        self.disabled_token = self._get_disabled_token()

    def tearDown(self):
        self._delete_token(self.token, self.auth_token)

    def test_a_authorize(self):
        response = self._get_token('joeuser', 'secrete')
        self.assertEqual(200, response.status_int)
        self.assertEqual('application/json', response.content_type)

    def test_a_authorize_xml(self):
        response = self._get_token_xml('joeuser', 'secrete')
        self.assertEqual(200, response.status_int)
        self.assertEqual('application/xml', response.content_type)

    def test_a_authorize_user_disaabled(self):
        url = '%stoken' % URL
        body = json.dumps({
            "passwordCredentials": {
                "username": "disabled",
                "password": "self.tenant_group='test_tenant_group'secrete",
            },
        })
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        response = self._post(url, body, headers)
        content = json.loads(response.body)
        if response.status_int == 500:
            self.fail('IDM fault')
        elif response.status_int == 503:
            self.fail('Service Not Available')
        self.assertEqual(403, response.status_int)

    def test_a_authorize_user_disaabled_xml(self):
        url = '%stoken' % URL
        body = '<?xml version="1.0" encoding="UTF-8"?> \
                <passwordCredentials \
                xmlns="http://docs.openstack.org/idm/api/v1.0" \
                password="secrete" username="disabled" \
                />'
        headers = {
            "Content-Type": "application/xml",
            "Accept": "application/xml",
        }
        response = self._post(url, body, headers)
        content = etree.fromstring(response.body)
        if response.status_int == 500:
            self.fail('IDM fault')
        elif response.status_int == 503:
            self.fail('Service Not Available')
        self.assertEqual(403, response.status_int)

    def test_a_authorize_user_wrong(self):
        url = '%stoken' % URL
        body = json.dumps({
            "passwordCredentials": {
                "username-w": "disabled",
                "password": "secrete",
            },
        })
        headers = {
            "Content-Type": "application/json",
        }
        response = self._post(url, body, headers)
        content = json.loads(response.body)
        if response.status_int == 500:
            self.fail('IDM fault')
        elif response.status_int == 503:
            self.fail('Service Not Available')
        self.assertEqual(400, response.status_int)

    def test_a_authorize_user_wrong_xml(self):
        url = '%stoken' % URL
        body = '<?xml version="1.0" encoding="UTF-8"?> \
                <passwordCredentials \
                xmlns="http://docs.openstack.org/idm/api/v1.0" \
                password="secrete" username-w="disabled" \
                />'
        headers = {
            "Content-Type": "application/xml",
            "Accept": "application/xml",
        }
        response = self._post(url, body, headers)
        content = etree.fromstring(response.body)
        if response.status_int == 500:
            self.fail('IDM fault')
        elif response.status_int == 503:
            self.fail('Service Not Available')
        self.assertEqual(400, response.status_int)


class validate_token(AuthenticateTest):

    def test_validate_token_true(self):
        h = httplib2.Http(".cache")

        url = '%stoken/%s?belongsTo=%s' % (URL, self.token, self.tenant)
        resp, content = h.request(url, "GET", body='',\
                                headers={"Content-Type": "application/json", \
                                         "X-Auth-Token": self.auth_token})
        if int(resp['status']) == 500:
            self.fail('IDM fault')
        elif int(resp['status']) == 503:
            self.fail('Service Not Available')
        self.assertEqual(200, int(resp['status']))
        self.assertEqual('application/json', resp['content-type'])

    def test_validate_token_true_xml(self):
        h = httplib2.Http(".cache")
        url = '%stoken/%s?belongsTo=%s' % (URL, self.token, self.tenant)
        resp, content = h.request(url, "GET", body='',\
                                headers={"Content-Type": "application/xml", \
                                         "X-Auth-Token": self.auth_token,
                                         "ACCEPT": "application/xml"})
        if int(resp['status']) == 500:
            self.fail('IDM fault')
        elif int(resp['status']) == 503:
            self.fail('Service Not Available')
        self.assertEqual(200, int(resp['status']))
        self.assertEqual('application/xml', resp['content-type'])

    def test_validate_token_expired(self):
        h = httplib2.Http(".cache")
        url = '%stoken/%s?belongsTo=%s' % (URL, self.exp_auth_token, \
                                            self.tenant)
        resp, content = h.request(url, "GET", body='',\
                                headers={"Content-Type": "application/json", \
                                         "X-Auth-Token": self.exp_auth_token})
        if int(resp['status']) == 500:
            self.fail('IDM fault')
        elif int(resp['status']) == 503:
            self.fail('Service Not Available')
        self.assertEqual(401, int(resp['status']))
        self.assertEqual('application/json', resp['content-type'])

    def test_validate_token_expired_xml(self):
        h = httplib2.Http(".cache")

        url = '%stoken/%s?belongsTo=%s' % (URL, self.exp_auth_token, \
                                            self.tenant)
        resp, content = h.request(url, "GET", body='',\
                                headers={"Content-Type": "application/xml", \
                                         "X-Auth-Token": self.exp_auth_token,
                                         "ACCEPT": "application/xml"})
        if int(resp['status']) == 500:
            self.fail('IDM fault')
        elif int(resp['status']) == 503:
            self.fail('Service Not Available')
        self.assertEqual(401, int(resp['status']))
        self.assertEqual('application/xml', resp['content-type'])

    def test_validate_token_invalid(self):
        h = httplib2.Http(".cache")
        url = '%stoken/%s?belongsTo=%s' % (URL, 'NonExistingToken', \
                                            self.tenant)
        resp, content = h.request(url, "GET", body='',\
                                headers={"Content-Type": "application/json", \
                                         "X-Auth-Token": self.auth_token})

        if int(resp['status']) == 500:
            self.fail('IDM fault')
        elif int(resp['status']) == 503:
            self.fail('Service Not Available')
        self.assertEqual(404, int(resp['status']))
        self.assertEqual('application/json', resp['content-type'])

    def test_validate_token_invalid_xml(self):
        h = httplib2.Http(".cache")
        url = '%stoken/%s?belongsTo=%s' % (URL, 'NonExistingToken', \
                                            self.tenant)
        resp, content = h.request(url, "GET", body='',\
                                headers={"Content-Type": "application/json", \
                                         "X-Auth-Token": self.auth_token})
        if int(resp['status']) == 500:
            self.fail('IDM fault')
        elif int(resp['status']) == 503:
            self.fail('Service Not Available')
        self.assertEqual(404, int(resp['status']))
        self.assertEqual('application/json', resp['content-type'])


class tenant_test(KeystoneTest):

    def setUp(self):
        super(tenant_test, self).setUp()
        self.token = self._get_token('joeuser', 'secrete', 'token')
        self.tenant = self._get_tenant()
        self.user = self._get_user()
        self.userdisabled = self._get_userdisabled()
        self.auth_token = self._get_auth_token()
        self.exp_auth_token = self._get_exp_auth_token()
        self.disabled_token = self._get_disabled_token()

    def tearDown(self):
        resp, content = delete_tenant(self.tenant, self.auth_token)
""" "passwordCredentials" : {"username" : "joeuser","password": "secrete","tenantId": "1234"}
"""

class create_tenant_test(tenant_test):

    def test_tenant_create(self):
        resp, content = delete_tenant('test_tenant', str(self.auth_token))

        resp, content = create_tenant('test_tenant', str(self.auth_token))
        self.tenant = 'test_tenant'

        if int(resp['status']) == 500:
            self.fail('IDM fault')
        elif int(resp['status']) == 503:
            self.fail('Service Not Available')

        if int(resp['status']) not in (200, 201):

            self.fail('Failed due to %d' % int(resp['status']))

    def test_tenant_create_xml(self):
        resp, content = delete_tenant_xml('test_tenant', str(self.auth_token))
        resp, content = create_tenant_xml('test_tenant', str(self.auth_token))
        self.tenant = 'test_tenant'
        content = etree.fromstring(content)
        if int(resp['status']) == 500:
            self.fail('IDM fault')
        elif int(resp['status']) == 503:
            self.fail('Service Not Available')

        if int(resp['status']) not in (200, 201):

            self.fail('Failed due to %d' % int(resp['status']))

    def test_tenant_create_again(self):

        resp, content = create_tenant("test_tenant", str(self.auth_token))
        resp, content = create_tenant("test_tenant", str(self.auth_token))
        if int(resp['status']) == 200:
            self.tenant = content['tenant']['id']
        if int(resp['status']) == 500:
            self.fail('IDM fault')
        elif int(resp['status']) == 503:
            self.fail('Service Not Available')
        self.assertEqual(409, int(resp['status']))
        if int(resp['status']) == 200:
            self.tenant = content['tenant']['id']

    def test_tenant_create_again_xml(self):

        resp, content = create_tenant_xml("test_tenant", str(self.auth_token))
        resp, content = create_tenant_xml("test_tenant", str(self.auth_token))
        content = etree.fromstring(content)
        if int(resp['status']) == 200:
            self.tenant = content.get("id")

        if int(resp['status']) == 500:
            self.fail('IDM fault')
        elif int(resp['status']) == 503:
            self.fail('Service Not Available')
        self.assertEqual(409, int(resp['status']))
        if int(resp['status']) == 200:
            self.tenant = content.get("id")

    def test_tenant_create_forbidden_token(self):
        h = httplib2.Http(".cache")
        resp, content = create_tenant("test_tenant", str(self.auth_token))
        if int(resp['status']) == 200:
            self.tenant = content['tenant']['id']

        url = '%stenants' % (URL)
        body = {"tenant": {"id": self.tenant,
                           "description": "A description ...",
                           "enabled": True}}
        resp, content = h.request(url, "POST", body=json.dumps(body),
                                  headers={"Content-Type": "application/json",
                                         "X-Auth-Token": self.token})

        if int(resp['status']) == 500:
            self.fail('IDM fault')
        elif int(resp['status']) == 503:
            self.fail('Service Not Available')
        self.assertEqual(403, int(resp['status']))

    def test_tenant_create_forbidden_token_xml(self):
        h = httplib2.Http(".cache")
        resp, content = create_tenant_xml("test_tenant", str(self.auth_token))
        content = etree.fromstring(content)
        if int(resp['status']) == 200:
            self.tenant = content.get('id')

        url = '%stenants' % (URL)
        body = '<?xml version="1.0" encoding="UTF-8"?> \
            <tenant xmlns="http://docs.openstack.org/idm/api/v1.0" \
            enabled="true" id="%s"> \
            <description>A description...</description> \
            </tenant>' % self.tenant
        resp, content = h.request(url, "POST", body=body,\
                                headers={"Content-Type": "application/xml",\
                                         "X-Auth-Token": self.token,
                                         "ACCEPT": "application/xml"})

        if int(resp['status']) == 500:
            self.fail('IDM fault')
        elif int(resp['status']) == 503:
            self.fail('Service Not Available')
        self.assertEqual(403, int(resp['status']))

    def test_tenant_create_expired_token(self):
        h = httplib2.Http(".cache")
        resp, content = create_tenant("test_tenant", str(self.auth_token))
        if int(resp['status']) == 200:
            self.tenant = content['tenant']['id']

        url = '%stenants' % (URL)
        body = {"tenant": {"id": self.tenant,
                           "description": "A description ...",
                           "enabled": True}}
        resp, content = h.request(url, "POST", body=json.dumps(body),
                                headers={"Content-Type": "application/json",
                                         "X-Auth-Token": self.exp_auth_token})

        if int(resp['status']) == 500:
            self.fail('IDM fault')
        elif int(resp['status']) == 503:
            self.fail('Service Not Available')
        self.assertEqual(401, int(resp['status']))

    def test_tenant_create_expired_token_xml(self):
        h = httplib2.Http(".cache")
        resp, content = create_tenant_xml("test_tenant", str(self.auth_token))
        content = etree.fromstring(content)
        if int(resp['status']) == 200:
            self.tenant = content.get('id')

        url = '%stenants' % (URL)
        body = '<?xml version="1.0" encoding="UTF-8"?> \
            <tenant xmlns="http://docs.openstack.org/idm/api/v1.0" \
            enabled="true" id="%s"> \
            <description>A description...</description> \
            </tenant>' % self.tenant

        resp, content = h.request(url, "POST", body=body,\
                                headers={"Content-Type": "application/xml",\
                                         "X-Auth-Token": self.exp_auth_token,
                                         "ACCEPT": "application/xml"})

        if int(resp['status']) == 500:
            self.fail('IDM fault')
        elif int(resp['status']) == 503:
            self.fail('Service Not Available')
        self.assertEqual(401, int(resp['status']))

    def test_tenant_create_missing_token(self):
        h = httplib2.Http(".cache")
        resp, content = create_tenant("test_tenant", str(self.auth_token))
        if int(resp['status']) == 200:
            self.tenant = content['tenant']['id']

        url = '%stenants' % (URL)
        body = {"tenant": {"id": self.tenant,
                           "description": "A description ...",
                           "enabled": True}}
        resp, content = h.request(url, "POST", body=json.dumps(body),
                                headers={"Content-Type": "application/json"})

        if int(resp['status']) == 500:
            self.fail('IDM fault')
        elif int(resp['status']) == 503:
            self.fail('Service Not Available')
        self.assertEqual(401, int(resp['status']))

    def test_tenant_create_missing_token_xml(self):
        h = httplib2.Http(".cache")
        resp, content = create_tenant_xml("test_tenant", str(self.auth_token))
        content = etree.fromstring(content)
        if int(resp['status']) == 200:
            self.tenant = content.get('id')

        url = '%stenants' % (URL)

        body = '<?xml version="1.0" encoding="UTF-8"?> \
            <tenant xmlns="http://docs.openstack.org/idm/api/v1.0" \
            enabled="true" id="%s"> \
            <description>A description...</description> \
            </tenant>' % self.tenant
        resp, content = h.request(url, "POST", body=body,\
                                headers={"Content-Type": "application/xml",
                                         "ACCEPT": "application/xml"})

        if int(resp['status']) == 500:
            self.fail('IDM fault')
        elif int(resp['status']) == 503:
            self.fail('Service Not Available')
        self.assertEqual(401, int(resp['status']))

    def test_tenant_create_disabled_token(self):
        h = httplib2.Http(".cache")
        resp, content = create_tenant("test_tenant", str(self.auth_token))
        if int(resp['status']) == 200:
            self.tenant = content['tenant']['id']

        url = '%stenants' % (URL)
        body = '{"tenant": { "id": "%s", \
                "description": "A description ...", "enabled"\
                :true  } }' % self.tenant
        resp, content = h.request(url, "POST", body=body,\
                                headers={"Content-Type": "application/json",\
                                         "X-Auth-Token": self.disabled_token})

        if int(resp['status']) == 500:
            self.fail('IDM fault')
        elif int(resp['status']) == 503:
            self.fail('Service Not Available')
        self.assertEqual(403, int(resp['status']))

    def test_tenant_create_disabled_token_xml(self):
        h = httplib2.Http(".cache")
        resp, content = create_tenant_xml("test_tenant", str(self.auth_token))
        content = etree.fromstring(content)
        if int(resp['status']) == 200:
            self.tenant = content.get('id')

        url = '%stenants' % (URL)
        body = '<?xml version="1.0" encoding="UTF-8"?> \
            <tenant xmlns="http://docs.openstack.org/idm/api/v1.0" \
            enabled="true" id="%s"> \
            <description>A description...</description> \
            </tenant>' % self.tenant
        resp, content = h.request(url, "POST", body=body,\
                                headers={"Content-Type": "application/xml",
                                         "X-Auth-Token": self.disabled_token,
                                         "ACCEPT": "application/xml"})

        if int(resp['status']) == 500:
            self.fail('IDM fault')
        elif int(resp['status']) == 503:
            self.fail('Service Not Available')
        self.assertEqual(403, int(resp['status']))

    def test_tenant_create_invalid_token(self):
        h = httplib2.Http(".cache")
        resp, content = create_tenant("test_tenant", str(self.auth_token))
        if int(resp['status']) == 200:
            self.tenant = content['tenant']['id']

        url = '%stenants' % (URL)
        body = '{"tenant": { "id": "%s", \
                "description": "A description ...", "enabled"\
                :true  } }' % self.tenant
        resp, content = h.request(url, "POST", body=body,\
                                headers={"Content-Type": "application/json",\
                                         "X-Auth-Token": 'nonexsitingtoken'})

        if int(resp['status']) == 500:
            self.fail('IDM fault')
        elif int(resp['status']) == 503:
            self.fail('Service Not Available')
        self.assertEqual(401, int(resp['status']))

    def test_tenant_create_invalid_token_xml(self):
        h = httplib2.Http(".cache")
        resp, content = create_tenant_xml("test_tenant", str(self.auth_token))
        content = etree.fromstring(content)
        if int(resp['status']) == 200:
            self.tenant = content.get('id')

        url = '%stenants' % (URL)
        body = '<?xml version="1.0" encoding="UTF-8"?> \
            <tenant xmlns="http://docs.openstack.org/idm/api/v1.0" \
            enabled="true" id="%s"> \
            <description>A description...</description> \
            </tenant>' % self.tenant
        resp, content = h.request(url, "POST", body=body,\
                                headers={"Content-Type": "application/xml",\
                                         "X-Auth-Token": 'nonexsitingtoken',
                                         "ACCEPT": "application/xml"})

        if int(resp['status']) == 500:
            self.fail('IDM fault')
        elif int(resp['status']) == 503:
            self.fail('Service Not Available')
        self.assertEqual(401, int(resp['status']))


class get_tenants_test(tenant_test):

    def test_get_tenants(self):
        h = httplib2.Http(".cache")
        resp, content = create_tenant(self.tenant, str(self.auth_token))
        url = '%stenants' % (URL)
        #test for Content-Type = application/json
        resp, content = h.request(url, "GET", body='{}',\
                                headers={"Content-Type": "application/json",\
                                         "X-Auth-Token": self.auth_token})
        if int(resp['status']) == 500:
            self.fail('IDM fault')
        elif int(resp['status']) == 503:
            self.fail('Service Not Available')
        self.assertEqual(200, int(resp['status']))

    def test_get_tenants_xml(self):
        h = httplib2.Http(".cache")
        resp, content = create_tenant(self.tenant, str(self.auth_token))
        url = '%stenants' % (URL)
        #test for Content-Type = application/json
        resp, content = h.request(url, "GET", body='',\
                                headers={"Content-Type": "application/xml",\
                                         "X-Auth-Token": self.auth_token,
                                         "ACCEPT": "application/xml"})
        if int(resp['status']) == 500:
            self.fail('IDM fault')
        elif int(resp['status']) == 503:
            self.fail('Service Not Available')
        self.assertEqual(200, int(resp['status']))

    def test_get_tenants_forbidden_token(self):
        h = httplib2.Http(".cache")
        resp, content = create_tenant(self.tenant, str(self.auth_token))
        url = '%stenants' % (URL)
        #test for Content-Type = application/json
        resp, content = h.request(url, "GET", body='{}',\
                                headers={"Content-Type": "application/json",\
                                         "X-Auth-Token": self.token})
        if int(resp['status']) == 500:
            self.fail('IDM fault')
        elif int(resp['status']) == 503:
            self.fail('Service Not Available')
        self.assertEqual(403, int(resp['status']))

    def test_get_tenants_forbidden_token_xml(self):
        h = httplib2.Http(".cache")
        resp, content = create_tenant(self.tenant, str(self.auth_token))
        url = '%stenants' % (URL)
        #test for Content-Type = application/json
        resp, content = h.request(url, "GET", body='',\
                                headers={"Content-Type": "application/xml",\
                                         "X-Auth-Token": self.token,
                                         "ACCEPT": "application/xml"})
        if int(resp['status']) == 500:
            self.fail('IDM fault')
        elif int(resp['status']) == 503:
            self.fail('Service Not Available')
        self.assertEqual(403, int(resp['status']))

    def test_get_tenants_exp_token(self):
        h = httplib2.Http(".cache")
        resp, content = create_tenant(self.tenant, str(self.auth_token))
        url = '%stenants' % (URL)
        #test for Content-Type = application/json
        resp, content = h.request(url, "GET", body='{}',\
                                headers={"Content-Type": "application/json",\
                                         "X-Auth-Token": self.exp_auth_token})
        if int(resp['status']) == 500:
            self.fail('IDM fault')
        elif int(resp['status']) == 503:
            self.fail('Service Not Available')
        self.assertEqual(401, int(resp['status']))

    def test_get_tenants_exp_token_xml(self):
        h = httplib2.Http(".cache")
        resp, content = create_tenant(self.tenant, str(self.auth_token))
        url = '%stenants' % (URL)
        #test for Content-Type = application/json
        resp, content = h.request(url, "GET", body='',\
                                headers={"Content-Type": "application/xml",\
                                         "X-Auth-Token": self.exp_auth_token,
                                         "ACCEPT": "application/xml"})
        if int(resp['status']) == 500:
            self.fail('IDM fault')
        elif int(resp['status']) == 503:
            self.fail('Service Not Available')
        self.assertEqual(401, int(resp['status']))


class get_tenant_test(tenant_test):

    def test_get_tenant(self):
        h = httplib2.Http(".cache")
        resp, content = create_tenant(self.tenant, str(self.auth_token))
        url = '%stenants/%s' % (URL, self.tenant)
        #test for Content-Type = application/json
        resp, content = h.request(url, "GET", body='{}',\
                                headers={"Content-Type": "application/json",\
                                         "X-Auth-Token": self.auth_token})
        if int(resp['status']) == 500:
            self.fail('IDM fault')
        elif int(resp['status']) == 503:
            self.fail('Service Not Available')
        self.assertEqual(200, int(resp['status']))

    def test_get_tenant_xml(self):
        h = httplib2.Http(".cache")
        resp, content = create_tenant(self.tenant, str(self.auth_token))
        url = '%stenants/%s' % (URL, self.tenant)
        #test for Content-Type = application/json
        resp, content = h.request(url, "GET", body='',\
                                headers={"Content-Type": "application/xml",\
                                         "X-Auth-Token": self.auth_token,
                                         "ACCEPT": "application/xml"})
        if int(resp['status']) == 500:
            self.fail('IDM fault')
        elif int(resp['status']) == 503:
            self.fail('Service Not Available')
        self.assertEqual(200, int(resp['status']))

    def test_get_tenant_bad(self):
        h = httplib2.Http(".cache")
        resp, content = create_tenant(self.tenant, str(self.auth_token))
        url = '%stenants/%s' % (URL, 'tenant_bad')
        #test for Content-Type = application/json
        resp, content = h.request(url, "GET", body='{',\
                                headers={"Content-Type": "application/json",\
                                         "X-Auth-Token": self.auth_token})
        if int(resp['status']) == 500:
            self.fail('IDM fault')
        elif int(resp['status']) == 503:
            self.fail('Service Not Available')
        self.assertEqual(404, int(resp['status']))

    def test_get_tenant_bad_xml(self):
        h = httplib2.Http(".cache")
        resp, content = create_tenant(self.tenant, str(self.auth_token))
        url = '%stenants/%s' % (URL, 'tenant_bad')
        #test for Content-Type = application/json
        resp, content = h.request(url, "GET", body='{',\
                                headers={"Content-Type": "application/xml",\
                                         "X-Auth-Token": self.auth_token,
                                         "ACCEPT": "application/xml"})
        if int(resp['status']) == 500:
            self.fail('IDM fault')
        elif int(resp['status']) == 503:
            self.fail('Service Not Available')
        self.assertEqual(404, int(resp['status']))

    def test_get_tenant_not_found(self):
        h = httplib2.Http(".cache")
        resp, content = create_tenant(self.tenant, str(self.auth_token))
        url = '%stenants/NonexistingID' % (URL)
        #test for Content-Type = application/json
        resp, content = h.request(url, "GET", body='{}',\
                                headers={"Content-Type": "application/json",\
                                         "X-Auth-Token": self.auth_token})
        if int(resp['status']) == 500:
            self.fail('IDM fault')
        elif int(resp['status']) == 503:
            self.fail('Service Not Available')
        self.assertEqual(404, int(resp['status']))

    def test_get_tenant_not_found_xml(self):
        h = httplib2.Http(".cache")
        resp, content = create_tenant(self.tenant, str(self.auth_token))
        url = '%stenants/NonexistingID' % (URL)
        #test for Content-Type = application/json
        resp, content = h.request(url, "GET", body='',\
                                headers={"Content-Type": "application/xml",\
                                         "X-Auth-Token": self.auth_token,
                                         "ACCEPT": "application/xml"})
        if int(resp['status']) == 500:
            self.fail('IDM fault')
        elif int(resp['status']) == 503:
            self.fail('Service Not Available')
        self.assertEqual(404, int(resp['status']))


class update_tenant_test(tenant_test):

    def test_update_tenant(self):
        h = httplib2.Http(".cache")
        resp, content = create_tenant(self.tenant, str(self.auth_token))
        url = '%stenants/%s' % (URL, self.tenant)
        data = '{"tenant": { "description": "A NEW description..." ,\
                "enabled":true }}'
        #test for Content-Type = application/json
        resp, content = h.request(url, "PUT", body=data,\
                                headers={"Content-Type": "application/json",\
                                         "X-Auth-Token": self.auth_token})
        body = json.loads(content)
        if int(resp['status']) == 500:
            self.fail('IDM fault')
        elif int(resp['status']) == 503:
            self.fail('Service Not Available')
        self.assertEqual(200, int(resp['status']))
        self.assertEqual(int(self.tenant), int(body['tenant']['id']))
        self.assertEqual('A NEW description...', \
                         body['tenant']['description'])

    def test_update_tenant_xml(self):
        h = httplib2.Http(".cache")
        resp, content = create_tenant_xml(self.tenant, str(self.auth_token))
        url = '%stenants/%s' % (URL, self.tenant)
        data = '<?xml version="1.0" encoding="UTF-8"?> \
             <tenant xmlns="http://docs.openstack.org/idm/api/v1.0" \
             enabled="true"> \
             <description>A NEW description...</description> \
             </tenant>'

        #test for Content-Type = application/json
        resp, content = h.request(url, "PUT", body=data,\
                                headers={"Content-Type": "application/xml",\
                                         "X-Auth-Token": self.auth_token,
                                         "ACCEPT": "application/xml"})
        body = etree.fromstring(content)
        desc = body.find("{http://docs.openstack.org/idm/api/v1.0}description")
        if int(resp['status']) == 500:
            self.fail('IDM fault')
        elif int(resp['status']) == 503:
            self.fail('Service Not Available')
        self.assertEqual(200, int(resp['status']))
        self.assertEqual(int(self.tenant), int(body.get('id')))
        self.assertEqual('A NEW description...', \
                         desc.text)

    def test_update_tenant_bad(self):
        h = httplib2.Http(".cache")
        resp, content = create_tenant(self.tenant, str(self.auth_token))
        url = '%stenants/%s' % (URL, self.tenant)
        data = '{"tenant": { "description_bad": "A NEW description...",\
                "enabled":true  }}'
        #test for Content-Type = application/json

        resp, content = h.request(url, "PUT", body=data,\
                                headers={"Content-Type": "application/json",\
                                         "X-Auth-Token": self.auth_token})
        if int(resp['status']) == 500:
            self.fail('IDM fault')
        elif int(resp['status']) == 503:
            self.fail('Service Not Available')
        self.assertEqual(400, int(resp['status']))

    def test_update_tenant_bad_xml(self):
        h = httplib2.Http(".cache")
        resp, content = create_tenant(self.tenant, str(self.auth_token))
        url = '%stenants/%s' % (URL, self.tenant)
        data = '<?xml version="1.0" encoding="UTF-8"?> \
             <tenant xmlns="http://docs.openstack.org/idm/api/v1.0" \
             enabled="true"> \
             <description_bad>A NEW description...</description> \
             </tenant>'
        #test for Content-Type = application/json
        resp, content = h.request(url, "PUT", body=data,\
                                headers={"Content-Type": "application/xml",\
                                         "X-Auth-Token": self.auth_token,
                                         "ACCEPT": "application/xml"})
        if int(resp['status']) == 500:
            self.fail('IDM fault')
        elif int(resp['status']) == 503:
            self.fail('Service Not Available')
        self.assertEqual(400, int(resp['status']))

    def test_update_tenant_not_found(self):
        h = httplib2.Http(".cache")
        resp, content = create_tenant(self.tenant, str(self.auth_token))
        url = '%stenants/NonexistingID' % (URL)
        data = '{"tenant": { "description": "A NEW description...",\
                "enabled":true  }}'
        #test for Content-Type = application/json
        resp, content = h.request(url, "GET", body=data,\
                                headers={"Content-Type": "application/json",\
                                         "X-Auth-Token": self.auth_token})
        if int(resp['status']) == 500:
            self.fail('IDM fault')
        elif int(resp['status']) == 503:
            self.fail('Service Not Available')
        self.assertEqual(404, int(resp['status']))

    def test_update_tenant_not_found_xml(self):
        h = httplib2.Http(".cache")
        resp, content = create_tenant(self.tenant, str(self.auth_token))
        url = '%stenants/NonexistingID' % (URL)
        data = '<?xml version="1.0" encoding="UTF-8"?> \
             <tenant xmlns="http://docs.openstack.org/idm/api/v1.0" \
             enabled="true"> \
             <description_bad>A NEW description...</description> \
             </tenant>'
        #test for Content-Type = application/json
        resp, content = h.request(url, "GET", body=data,\
                                headers={"Content-Type": "application/xml",\
                                         "X-Auth-Token": self.auth_token,
                                         "ACCEPT": "application/xml"})
        if int(resp['status']) == 500:
            self.fail('IDM fault')
        elif int(resp['status']) == 503:
            self.fail('Service Not Available')
        self.assertEqual(404, int(resp['status']))


class delete_tenant_test(tenant_test):

    def test_delete_tenant_not_found(self):
        #resp,content=create_tenant("test_tenant_delete", str(self.auth_token))
        resp, content = delete_tenant("test_tenant_delete111", \
                                        str(self.auth_token))
        self.assertEqual(404, int(resp['status']))

    def test_delete_tenant_not_found_xml(self):
        #resp,content=create_tenant("test_tenant_delete", str(self.auth_token))
        resp, content = delete_tenant_xml("test_tenant_delete111", \
                                            str(self.auth_token))
        self.assertEqual(404, int(resp['status']))

    def test_delete_tenant(self):
        resp, content = create_tenant("test_tenant_delete", \
                                    str(self.auth_token))
        resp, content = delete_tenant("test_tenant_delete", \
                                        str(self.auth_token))
        self.assertEqual(204, int(resp['status']))

    def test_delete_tenant_xml(self):
        resp, content = create_tenant_xml("test_tenant_delete", \
                                          str(self.auth_token))
        resp, content = delete_tenant_xml("test_tenant_delete", \
                                            str(self.auth_token))
        self.assertEqual(204, int(resp['status']))



    class tenant_group_test(unittest.TestCase):

        def setUp(self):
            self.token = self._get_token('joeuser', 'secrete', 'token')
            self.tenant = self._get_tenant()
            self.user = self._get_user()
            self.userdisabled = self._get_userdisabled()
            self.auth_token = self._get_auth_token()
            self.exp_auth_token = self._get_exp_auth_token()
            self.disabled_token = self._get_disabled_token()
            self.tenant_group = 'test_tenant_group'

        def tearDown(self):
            resp, content = delete_tenant_group('test_tenant_group', \
                                            self.tenant, self.auth_token)
            resp, content = delete_tenant(self.tenant, self.auth_token)


    class create_tenant_group_test(tenant_group_test):

        def test_tenant_group_create(self):
            resp, content = delete_tenant('test_tenant', str(self.auth_token))
            resp, content = create_tenant('test_tenant', str(self.auth_token))

            respG, contentG = delete_tenant_group('test_tenant_group', \
                                            'test_tenant', str(self.auth_token))
            respG, contentG = create_tenant_group('test_tenant_group', \
                                            'test_tenant', str(self.auth_token))

            self.tenant = 'test_tenant'
            self.tenant_group = 'test_tenant_group'

            if int(resp['status']) == 500:
                self.fail('IDM fault')
            elif int(resp['status']) == 503:
                self.fail('Service Not Available')

            if int(respG['status']) not in (200, 201):

                self.fail('Failed due to %d' % int(respG['status']))

        def test_tenant_group_create_xml(self):
            resp, content = delete_tenant_xml('test_tenant', str(self.auth_token))
            resp, content = create_tenant_xml('test_tenant', str(self.auth_token))
            respG, contentG = delete_tenant_group_xml('test_tenant_group', \
                                                "test_tenant", str(self.auth_token))
            respG, contentG = create_tenant_group_xml('test_tenant_group', \
                                                "test_tenant", str(self.auth_token))

            self.tenant = 'test_tenant'
            self.tenant_group = 'test_tenant_group'
            content = etree.fromstring(content)
            if int(resp['status']) == 500:
                self.fail('IDM fault')
            elif int(resp['status']) == 503:
                self.fail('Service Not Available')

            if int(respG['status']) not in (200, 201):

                self.fail('Failed due to %d' % int(respG['status']))

        def test_tenant_group_create_again(self):

            resp, content = create_tenant("test_tenant", str(self.auth_token))

            respG, contentG = create_tenant_group('test_tenant_group', \
                                            "test_tenant", str(self.auth_token))
            respG, contentG = create_tenant_group('test_tenant_group', \
                                            "test_tenant", str(self.auth_token))

            if int(respG['status']) == 200:
                self.tenant = content['tenant']['id']
                self.tenant_group = contentG['group']['id']
            if int(respG['status']) == 500:
                self.fail('IDM fault')
            elif int(respG['status']) == 503:
                self.fail('Service Not Available')
            self.assertEqual(409, int(respG['status']))
            if int(respG['status']) == 200:
                self.tenant = content['tenant']['id']
                self.tenant_group = contentG['group']['id']

        def test_tenant_group_create_again_xml(self):

            resp, content = create_tenant_xml("test_tenant", str(self.auth_token))

            respG, contentG = create_tenant_group_xml('test_tenant_group', \
                                            "test_tenant", str(self.auth_token))
            respG, contentG = create_tenant_group_xml('test_tenant_group', \
                                            "test_tenant", str(self.auth_token))

            content = etree.fromstring(content)
            contentG = etree.fromstring(contentG)
            if int(respG['status']) == 200:
                self.tenant = content.get("id")
                self.tenant_group = contentG.get("id")

            if int(respG['status']) == 500:
                self.fail('IDM fault')
            elif int(respG['status']) == 503:
                self.fail('Service Not Available')
            self.assertEqual(409, int(respG['status']))
            if int(respG['status']) == 200:
                self.tenant = content.get("id")
                self.tenant_group = contentG.get("id")

        def test_tenant_group_create_forbidden_token(self):
            h = httplib2.Http(".cache")
            resp, content = create_tenant("test_tenant", str(self.auth_token))
            respG, contentG = create_tenant_group_xml('test_tenant_group', \
                                            "test_tenant", str(self.auth_token))
            if int(resp['status']) == 200:
                self.tenant = content['tenant']['id']

            if int(respG['status']) == 200:
                self.tenant_group = respG['group']['id']

            url = '%stenant/%s/groups' % (URL, self.tenant)
            body = {"group": {"id": self.tenant_group,
                               "description": "A description ..."
                               }}
            resp, content = h.request(url, "POST", body=json.dumps(body),
                                      headers={"Content-Type": "application/json",
                                             "X-Auth-Token": self.token})

            if int(resp['status']) == 500:
                self.fail('IDM fault')
            elif int(resp['status']) == 503:
                self.fail('Service Not Available')
            self.assertEqual(403, int(resp['status']))

        def test_tenant_group_create_forbidden_token_xml(self):
            h = httplib2.Http(".cache")
            resp, content = create_tenant("test_tenant", str(self.auth_token))
            if int(resp['status']) == 200:
                self.tenant = content['tenant']['id']

            url = '%stenant/%s/groups' % (URL, self.tenant)
            body = '<?xml version="1.0" encoding="UTF-8"?> \
                <group xmlns="http://docs.openstack.org/idm/api/v1.0" \
                 id="%s"> \
                <description>A description...</description> \
                </group>' % self.tenant_group
            resp, content = h.request(url, "POST", body=body,\
                                    headers={"Content-Type": "application/xml", \
                                             "X-Auth-Token": self.token,
                                             "ACCEPT": "application/xml"})

            if int(resp['status']) == 500:
                self.fail('IDM fault')
            elif int(resp['status']) == 503:
                self.fail('Service Not Available')

            self.assertEqual(403, int(resp['status']))

        def test_tenant_group_create_expired_token(self):
            h = httplib2.Http(".cache")
            resp, content = create_tenant("test_tenant", str(self.auth_token))
            if int(resp['status']) == 200:
                self.tenant = content['tenant']['id']

            url = '%stenant/%s/groups' % (URL, self.tenant)
            body = {"group": {"id": self.tenant_group,
                               "description": "A description ..."
                               }}
            resp, content = h.request(url, "POST", body=json.dumps(body),
                                    headers={"Content-Type": "application/json",
                                             "X-Auth-Token": self.exp_auth_token})

            if int(resp['status']) == 500:
                self.fail('IDM fault')
            elif int(resp['status']) == 503:
                self.fail('Service Not Available')
            self.assertEqual(401, int(resp['status']))

        def test_tenant_group_create_expired_token_xml(self):
            h = httplib2.Http(".cache")
            resp, content = create_tenant_xml("test_tenant", str(self.auth_token))
            content = etree.fromstring(content)
            if int(resp['status']) == 200:
                self.tenant = content.get('id')

            url = '%stenant/%s/groups' % (URL, self.tenant)
            body = '<?xml version="1.0" encoding="UTF-8"?> \
                <group xmlns="http://docs.openstack.org/idm/api/v1.0" \
                 id="%s"> \
                <description>A description...</description> \
                </group>' % self.tenant

            resp, content = h.request(url, "POST", body=body,\
                                    headers={"Content-Type": "application/xml", \
                                             "X-Auth-Token": self.exp_auth_token,
                                             "ACCEPT": "application/xml"})

            if int(resp['status']) == 500:
                self.fail('IDM fault')
            elif int(resp['status']) == 503:
                self.fail('Service Not Available')
            self.assertEqual(401, int(resp['status']))

        def test_tenant_group_create_missing_token(self):
            h = httplib2.Http(".cache")
            resp, content = create_tenant("test_tenant", str(self.auth_token))
            if int(resp['status']) == 200:
                self.tenant = content['tenant']['id']

            url = '%stenant/%s/groups' % (URL, self.tenant)
            body = {"group": {"id": self.tenant_group,
                               "description": "A description ..."}}
            resp, content = h.request(url, "POST", body=json.dumps(body),
                                    headers={"Content-Type": "application/json"})

            if int(resp['status']) == 500:
                self.fail('IDM fault')
            elif int(resp['status']) == 503:
                self.fail('Service Not Available')
            self.assertEqual(401, int(resp['status']))

        def test_tenant_group_create_missing_token_xml(self):
            h = httplib2.Http(".cache")
            resp, content = create_tenant_xml("test_tenant", str(self.auth_token))
            content = etree.fromstring(content)
            if int(resp['status']) == 200:
                self.tenant = content.get('id')

            url = '%stenant/%s/groups' % (URL, self.tenant)

            body = '<?xml version="1.0" encoding="UTF-8"?> \
                <group xmlns="http://docs.openstack.org/idm/api/v1.0" \
                id="%s"> \
                <description>A description...</description> \
                </group>' % self.tenant_group
            resp, content = h.request(url, "POST", body=body,\
                                    headers={"Content-Type": "application/xml",
                                             "ACCEPT": "application/xml"})

            if int(resp['status']) == 500:
                self.fail('IDM fault')
            elif int(resp['status']) == 503:
                self.fail('Service Not Available')
            self.assertEqual(401, int(resp['status']))

        def test_tenant_group_create_disabled_token(self):
            h = httplib2.Http(".cache")
            resp, content = create_tenant("test_tenant", str(self.auth_token))
            if int(resp['status']) == 200:
                self.tenant = content['tenant']['id']

            url = '%stenant/%s/groups' % (URL, self.tenant)
            body = '{"group": { "id": "%s", \
                    "description": "A description ..." } }' % self.tenant_group
            resp, content = h.request(url, "POST", body=body,\
                                    headers={"Content-Type": "application/json",\
                                             "X-Auth-Token": self.disabled_token})

            if int(resp['status']) == 500:
                self.fail('IDM fault')
            elif int(resp['status']) == 503:
                self.fail('Service Not Available')
            self.assertEqual(403, int(resp['status']))

        def test_tenant_group_create_disabled_token_xml(self):
            h = httplib2.Http(".cache")
            resp, content = create_tenant_xml("test_tenant", str(self.auth_token))
            content = etree.fromstring(content)
            if int(resp['status']) == 200:
                self.tenant = content.get('id')

            url = '%stenant/%s/groups' % (URL, self.tenant)
            body = '<?xml version="1.0" encoding="UTF-8"?> \
                <group xmlns="http://docs.openstack.org/idm/api/v1.0" \
                id="%s"> \
                <description>A description...</description> \
                </group>' % self.tenant_group
            resp, content = h.request(url, "POST", body=body,\
                                    headers={"Content-Type": "application/xml",
                                             "X-Auth-Token": self.disabled_token,
                                             "ACCEPT": "application/xml"})

            if int(resp['status']) == 500:
                self.fail('IDM fault')
            elif int(resp['status']) == 503:
                self.fail('Service Not Available')
            self.assertEqual(403, int(resp['status']))

        def test_tenant_group_create_invalid_token(self):
            h = httplib2.Http(".cache")
            resp, content = create_tenant("test_tenant", str(self.auth_token))
            if int(resp['status']) == 200:
                self.tenant = content['tenant']['id']

            url = '%stenant/%s/groups' % (URL, self.tenant)
            body = '{"group": { "id": "%s", \
                    "description": "A description ..." } }' % self.tenant
            resp, content = h.request(url, "POST", body=body,\
                                    headers={"Content-Type": "application/json",\
                                             "X-Auth-Token": 'nonexsitingtoken'})

            if int(resp['status']) == 500:
                self.fail('IDM fault')
            elif int(resp['status']) == 503:
                self.fail('Service Not Available')
            self.assertEqual(401, int(resp['status']))

        def test_tenant_group_create_invalid_token_xml(self):
            h = httplib2.Http(".cache")
            resp, content = create_tenant_xml("test_tenant", str(self.auth_token))
            content = etree.fromstring(content)
            if int(resp['status']) == 200:
                self.tenant = content.get('id')

            url = '%stenant/%s/groups' % (URL, self.tenant)
            body = '<?xml version="1.0" encoding="UTF-8"?> \
                <group xmlns="http://docs.openstack.org/idm/api/v1.0" \
                 id="%s"> \
                <description>A description...</description> \
                </group>' % self.tenant_group
            resp, content = h.request(url, "POST", body=body,\
                                    headers={"Content-Type": "application/xml",\
                                             "X-Auth-Token": 'nonexsitingtoken',
                                             "ACCEPT": "application/xml"})

            if int(resp['status']) == 500:
                self.fail('IDM fault')
            elif int(resp['status']) == 503:
                self.fail('Service Not Available')
            self.assertEqual(401, int(resp['status']))


    class get_tenant_groups_test(tenant_group_test):

        def test_get_tenant_groups(self):
            h = httplib2.Http(".cache")
            resp, content = create_tenant(self.tenant, str(self.auth_token))

            respG, contentG = create_tenant_group(self.tenant_group,\
                                            self.tenant, str(self.auth_token))

            url = '%stenant/%s/groups' % (URL,self.tenant)

            resp, content = h.request(url, "GET", body='{}',\
                                    headers={"Content-Type": "application/json",\
                                             "X-Auth-Token": self.auth_token})
            if int(resp['status']) == 500:
                self.fail('IDM fault')
            elif int(resp['status']) == 503:
                self.fail('Service Not Available')
            self.assertEqual(200, int(resp['status']))

        def test_get_tenant_groups_xml(self):
            h = httplib2.Http(".cache")
            resp, content = create_tenant(self.tenant, str(self.auth_token))

            respG, contentG = create_tenant_group_xml(self.tenant_group,\
                                            self.tenant, str(self.auth_token))

            url = '%stenant/%s/groups' % (URL,self.tenant)

            resp, content = h.request(url, "GET", body='',\
                                    headers={"Content-Type": "application/xml",\
                                             "X-Auth-Token": self.auth_token,
                                             "ACCEPT": "application/xml"})
            if int(resp['status']) == 500:
                self.fail('IDM fault')
            elif int(resp['status']) == 503:
                self.fail('Service Not Available')
            self.assertEqual(200, int(resp['status']))

        def test_get_tenant_groups_forbidden_token(self):
            h = httplib2.Http(".cache")
            resp, content = create_tenant(self.tenant, str(self.auth_token))

            respG, contentG = create_tenant_group(self.tenant_group,\
                                            self.tenant, str(self.auth_token))
            url = '%stenant/%s/groups' % (URL,self.tenant)
            #test for Content-Type = application/json
            resp, content = h.request(url, "GET", body='{}',\
                                    headers={"Content-Type": "application/json",\
                                             "X-Auth-Token": self.token})
            if int(resp['status']) == 500:
                self.fail('IDM fault')
            elif int(resp['status']) == 503:
                self.fail('Service Not Available')
            self.assertEqual(403, int(resp['status']))

        def test_get_tenant_groups_forbidden_token_xml(self):
            h = httplib2.Http(".cache")
            resp, content = create_tenant(self.tenant, str(self.auth_token))
            respG, contentG = create_tenant_group(self.tenant_group,\
                                            self.tenant, str(self.auth_token))
            url = '%stenant/%s/groups' % (URL,self.tenant)
            #test for Content-Type = application/json
            resp, content = h.request(url, "GET", body='',\
                                    headers={"Content-Type": "application/xml",\
                                             "X-Auth-Token": self.token,
                                             "ACCEPT": "application/xml"})
            if int(resp['status']) == 500:
                self.fail('IDM fault')
            elif int(resp['status']) == 503:
                self.fail('Service Not Available')
            self.assertEqual(403, int(resp['status']))

        def test_get_tenant_groups_exp_token(self):
            h = httplib2.Http(".cache")
            resp, content = create_tenant(self.tenant, str(self.auth_token))
            respG, contentG = create_tenant_group(self.tenant_group,\
                                            self.tenant, str(self.auth_token))
            url = '%stenant/%s/groups' % (URL,self.tenant)
            #test for Content-Type = application/json
            resp, content = h.request(url, "GET", body='{}',\
                                    headers={"Content-Type": "application/json",\
                                             "X-Auth-Token": self.exp_auth_token})
            if int(resp['status']) == 500:
                self.fail('IDM fault')
            elif int(resp['status']) == 503:
                self.fail('Service Not Available')
            self.assertEqual(401, int(resp['status']))

        def test_get_tenant_groups_exp_token_xml(self):
            h = httplib2.Http(".cache")
            resp, content = create_tenant(self.tenant, str(self.auth_token))
            respG, contentG = create_tenant_group(self.tenant_group,\
                                            self.tenant, str(self.auth_token))
            url = '%stenant/%s/groups' % (URL,self.tenant)
            #test for Content-Type = application/json
            resp, content = h.request(url, "GET", body='',\
                                    headers={"Content-Type": "application/xml",\
                                             "X-Auth-Token": self.exp_auth_token,
                                             "ACCEPT": "application/xml"})
            if int(resp['status']) == 500:
                self.fail('IDM fault')
            elif int(resp['status']) == 503:
                self.fail('Service Not Available')
            self.assertEqual(401, int(resp['status']))


    class get_tenant_group_test(tenant_group_test):

        def test_get_tenant_group(self):
            h = httplib2.Http(".cache")
            resp, content = create_tenant(self.tenant, str(self.auth_token))
            respG, contentG = create_tenant_group(self.tenant_group,\
                                            self.tenant, str(self.auth_token))
            url = '%stenant/%s/groups/%s' % (URL,self.tenant,self.tenant_group)
            #test for Content-Type = application/json
            resp, content = h.request(url, "GET", body='{}',\
                                    headers={"Content-Type": "application/json",\
                                             "X-Auth-Token": self.auth_token})
            if int(resp['status']) == 500:
                self.fail('IDM fault')
            elif int(resp['status']) == 503:
                self.fail('Service Not Available')
            self.assertEqual(200, int(resp['status']))

        def test_get_tenant_group_xml(self):
            h = httplib2.Http(".cache")
            resp, content = create_tenant(self.tenant, str(self.auth_token))
            respG, contentG = create_tenant_group_xml(self.tenant_group,\
                                            self.tenant, str(self.auth_token))
            url = '%stenant/%s/groups/%s' % (URL,self.tenant,self.tenant_group)
            #test for Content-Type = application/json
            resp, content = h.request(url, "GET", body='',\
                                    headers={"Content-Type": "application/xml",\
                                             "X-Auth-Token": self.auth_token,
                                             "ACCEPT": "application/xml"})
            if int(resp['status']) == 500:
                self.fail('IDM fault')
            elif int(resp['status']) == 503:
                self.fail('Service Not Available')
            self.assertEqual(200, int(resp['status']))

        def test_get_tenant_group_bad(self):
            h = httplib2.Http(".cache")
            resp, content = create_tenant(self.tenant, str(self.auth_token))
            respG, contentG = create_tenant_group(self.tenant_group,\
                                            self.tenant, str(self.auth_token))
            url = '%stenant/%s/groups/%s' % (URL,'tenant_bad',self.tenant_group)

            #test for Content-Type = application/json
            resp, content = h.request(url, "GET", body='{',\
                                    headers={"Content-Type": "application/json",\
                                             "X-Auth-Token": self.auth_token})
            if int(resp['status']) == 500:
                self.fail('IDM fault')
            elif int(resp['status']) == 503:
                self.fail('Service Not Available')
            self.assertEqual(404, int(resp['status']))

        def test_get_tenant_group_bad_xml(self):
            h = httplib2.Http(".cache")
            resp, content = create_tenant(self.tenant, str(self.auth_token))
            respG, contentG = create_tenant_group(self.tenant_group,\
                                            self.tenant, str(self.auth_token))
            url = '%stenant/%s/groups/%s' % (URL,'tenant_bad',self.tenant_group)
            #test for Content-Type = application/json
            resp, content = h.request(url, "GET", body='{',\
                                    headers={"Content-Type": "application/xml",\
                                             "X-Auth-Token": self.auth_token,
                                             "ACCEPT": "application/xml"})
            if int(resp['status']) == 500:
                self.fail('IDM fault')
            elif int(resp['status']) == 503:
                self.fail('Service Not Available')
            self.assertEqual(404, int(resp['status']))

        def test_get_tenant_group_not_found(self):
            h = httplib2.Http(".cache")
            resp, content = create_tenant(self.tenant, str(self.auth_token))
            respG, contentG = create_tenant_group(self.tenant_group,\
                                            self.tenant, str(self.auth_token))
            url = '%stenant/%s/groups/%s' % (URL,self.tenant,'nonexistinggroup')
            #test for Content-Type = application/json
            resp, content = h.request(url, "GET", body='{}',\
                                    headers={"Content-Type": "application/json",\
                                             "X-Auth-Token": self.auth_token})
            if int(resp['status']) == 500:
                self.fail('IDM fault')
            elif int(resp['status']) == 503:
                self.fail('Service Not Available')
            self.assertEqual(404, int(resp['status']))

        def test_get_tenant_group_not_found_xml(self):
            h = httplib2.Http(".cache")
            resp, content = create_tenant(self.tenant, str(self.auth_token))
            respG, contentG = create_tenant_group(self.tenant_group,\
                                            self.tenant, str(self.auth_token))
            url = '%stenant/%s/groups/%s' % (URL,self.tenant,'nonexistinggroup')

            #test for Content-Type = application/json
            resp, content = h.request(url, "GET", body='',\
                                    headers={"Content-Type": "application/xml",\
                                             "X-Auth-Token": self.auth_token,
                                             "ACCEPT": "application/xml"})
            if int(resp['status']) == 500:
                self.fail('IDM fault')
            elif int(resp['status']) == 503:
                self.fail('Service Not Available')
            self.assertEqual(404, int(resp['status']))


    class update_tenant_group_test(tenant_group_test):

        def test_update_tenant_group(self):
            h = httplib2.Http(".cache")
            resp, content = create_tenant(self.tenant, str(self.auth_token))
            respG, contentG = create_tenant_group(self.tenant_group,\
                                            self.tenant, str(self.auth_token))
            url = '%stenant/%s/groups/%s' % (URL,self.tenant,self.tenant_group)

            data = '{"group": { "id":"%s","description": "A NEW description..." ,\
                    "tenantId":"%s" }}' % (self.tenant_group,self.tenant)
            #test for Content-Type = application/json
            resp, content = h.request(url, "PUT", body=data,\
                                    headers={"Content-Type": "application/json",\
                                             "X-Auth-Token": self.auth_token})
            body = json.loads(content)
            if int(resp['status']) == 500:
                self.fail('IDM fault')
            elif int(resp['status']) == 503:
                self.fail('Service Not Available')
            self.assertEqual(200, int(resp['status']))
            self.assertEqual(self.tenant_group, body['group']['id'])
            self.assertEqual('A NEW description...', \
                             body['group']['description'])

        def test_update_tenant_group_xml(self):
            h = httplib2.Http(".cache")
            resp, content = create_tenant_xml(self.tenant, str(self.auth_token))
            respG, contentG = create_tenant_group(self.tenant_group,\
                                            self.tenant, str(self.auth_token))
            url = '%stenant/%s/groups/%s' % (URL, self.tenant ,self.tenant_group)
            data = '<?xml version="1.0" encoding="UTF-8"?> \
                 <group xmlns="http://docs.openstack.org/idm/api/v1.0" \
                 tenantId="%s" id="%s"> \
                 <description>A NEW description...</description> \
                 </group>' % (self.tenant, self.tenant_group)

            #test for Content-Type = application/json
            resp, content = h.request(url, "PUT", body=data,\
                                    headers={"Content-Type": "application/xml",\
                                             "X-Auth-Token": self.auth_token,
                                             "ACCEPT": "application/xml"})

            body = etree.fromstring(content)
            desc = body.find("{http://docs.openstack.org/idm/api/v1.0}description")
            if int(resp['status']) == 500:
                self.fail('IDM fault')
            elif int(resp['status']) == 503:
                self.fail('Service Not Available')
            self.assertEqual(200, int(resp['status']))
            self.assertEqual(str(self.tenant_group), str(body.get('id')))
            self.assertEqual('A NEW description...', \
                             desc.text)

        def test_update_tenant_group_bad(self):
            h = httplib2.Http(".cache")
            resp, content = create_tenant(self.tenant, str(self.auth_token))
            respG, contentG = create_tenant_group(self.tenant_group,\
                                            self.tenant, str(self.auth_token))
            url = '%stenant/%s/groups/%s' % (URL,self.tenant,self.tenant_group)
            data = '{"group": { "description_bad": "A NEW description...",\
                    "id":"%s","tenantId":"%s"  }}' % (self.tenant_group,self.tenant)
            #test for Content-Type = application/json

            resp, content = h.request(url, "PUT", body=data,\
                                    headers={"Content-Type": "application/json",\
                                             "X-Auth-Token": self.auth_token})
            if int(resp['status']) == 500:
                self.fail('IDM fault')
            elif int(resp['status']) == 503:
                self.fail('Service Not Available')
            self.assertEqual(400, int(resp['status']))

        def test_update_tenant_group_bad_xml(self):
            h = httplib2.Http(".cache")
            resp, content = create_tenant(self.tenant, str(self.auth_token))
            respG, contentG = create_tenant_group(self.tenant_group,\
                                            self.tenant, str(self.auth_token))
            url = '%stenant/%s/groups/%s' % (URL,self.tenant,self.tenant_group)
            data = '<?xml version="1.0" encoding="UTF-8"?> \
                 <group xmlns="http://docs.openstack.org/idm/api/v1.0" \
                 tenantId="%s" id="%s"> \
                 <description_bad>A NEW description...</description> \
                 </group>' % (self.tenant, self.tenant_group)
            #test for Content-Type = application/json
            resp, content = h.request(url, "PUT", body=data,\
                                    headers={"Content-Type": "application/xml",\
                                             "X-Auth-Token": self.auth_token,
                                             "ACCEPT": "application/xml"})
            if int(resp['status']) == 500:
                self.fail('IDM fault')
            elif int(resp['status']) == 503:
                self.fail('Service Not Available')
            self.assertEqual(400, int(resp['status']))

        def test_update_tenant_group_not_found(self):
            h = httplib2.Http(".cache")
            resp, content = create_tenant(self.tenant, str(self.auth_token))
            respG, contentG = create_tenant_group(self.tenant_group,\
                                            self.tenant, str(self.auth_token))
            url = '%stenant/%s/groups/NonexistingID' % (URL, self.tenant)

            data = '{"group": { "description": "A NEW description...",\
                    "id":"NonexistingID", "tenantId"="test_tenant"  }}'
            #test for Content-Type = application/json
            resp, content = h.request(url, "GET", body=data,\
                                    headers={"Content-Type": "application/json",\
                                             "X-Auth-Token": self.auth_token})
            if int(resp['status']) == 500:
                self.fail('IDM fault')
            elif int(resp['status']) == 503:
                self.fail('Service Not Available')
            self.assertEqual(404, int(resp['status']))

        def test_update_tenant_group_not_found_xml(self):
            h = httplib2.Http(".cache")
            resp, content = create_tenant(self.tenant, str(self.auth_token))
            url = '%stenant/%s/groups/NonexistingID' % (URL, self.tenant)
            data = '<?xml version="1.0" encoding="UTF-8"?> \
             <group xmlns="http://docs.openstack.org/idm/api/v1.0" \
             id="NonexistingID", "tenant_id"="test_tenant"> \
             <description_bad>A NEW description...</description> \
             </group>'
            #test for Content-Type = application/json
            resp, content = h.request(url, "GET", body=data,\
                                headers={"Content-Type": "application/xml",\
                                         "X-Auth-Token": self.auth_token,
                                         "ACCEPT": "application/xml"})
            if int(resp['status']) == 500:
                self.fail('IDM fault')
            elif int(resp['status']) == 503:
             self.fail('Service Not Available')
            self.assertEqual(404, int(resp['status']))


    class delete_tenant_group_test(tenant_group_test):

        def test_delete_tenant_group_not_found(self):
            #resp,content=create_tenant("test_tenant_delete", str(self.auth_token))
            resp, content = delete_tenant_group("test_tenant_delete111", \
                                        "test_tenant", str(self.auth_token))
            self.assertEqual(404, int(resp['status']))

        def test_delete_tenant_group_not_found_xml(self):
            #resp,content=create_tenant("test_tenant_delete", str(self.auth_token))
            resp, content = delete_tenant_group_xml("test_tenant_delete111", \
                                            "test_tenant", str(self.auth_token))
            self.assertEqual(404, int(resp['status']))

        def test_delete_tenant_group(self):
            resp, content = create_tenant("test_tenant_delete", \
                                    str(self.auth_token))
            respG, contentG = create_tenant_group('test_tenant_group_delete', \
                                        "test_tenant_delete", str(self.auth_token))
            respG, contentG = delete_tenant_group('test_tenant_group_delete', \
                                        "test_tenant_delete", str(self.auth_token))
            resp, content = delete_tenant("test_tenant_delete", \
                                        str(self.auth_token))
            self.assertEqual(204, int(respG['status']))

        def test_delete_tenant_group_xml(self):
            resp, content = create_tenant_xml("test_tenant_delete", \
                                          str(self.auth_token))
            respG, contentG = create_tenant_group_xml('test_tenant_group_delete', \
                                        "test_tenant_delete", str(self.auth_token))
            respG, contentG = delete_tenant_group_xml('test_tenant_group_delete', \
                                        "test_tenant_delete", str(self.auth_token))
            resp, content = delete_tenant_xml("test_tenant_delete", \
                                            str(self.auth_token))
            self.assertEqual(204, int(respG['status']))

        def test_tenant_group_create_forbidden_token(self):
            h = httplib2.Http(".cache")
            resp, content = create_tenant("test_tenant", str(self.auth_token))
            respG, contentG = create_tenant_group_xml('test_tenant_group', \
                                        "test_tenant", str(self.auth_token))
            if int(resp['status']) == 200:
                self.tenant = content['tenant']['id']

            if int(respG['status']) == 200:
                self.tenant_group = respG['group']['id']

            url = '%stenant/%s/groups' % (URL, self.tenant)
            body = {"group": {"id": self.tenant_group,
                           "description": "A description ..."\
                           }}
            resp, content = h.request(url, "POST", body=json.dumps(body),
                                  headers={"Content-Type": "application/json",
                                         "X-Auth-Token": self.token})

            if int(resp['status']) == 500:
                self.fail('IDM fault')
            elif int(resp['status']) == 503:
                self.fail('Service Not Available')
            self.assertEqual(403, int(resp['status']))

        def test_tenant_group_create_expired_token(self):
            h = httplib2.Http(".cache")
            resp, content = create_tenant("test_tenant", str(self.auth_token))
            if int(resp['status']) == 200:
                self.tenant = content['tenant']['id']

            url = '%stenant/%s/groups' % (URL, self.tenant)
            body = {"group": {"id": self.tenant_group,
                           "description": "A description ..."
                           }}
            resp, content = h.request(url, "POST", body=json.dumps(body),
                                headers={"Content-Type": "application/json",
                                         "X-Auth-Token": self.exp_auth_token})
            if int(resp['status']) == 500:
                self.fail('IDM fault')
            elif int(resp['status']) == 503:
                self.fail('Service Not Available')
            self.assertEqual(401, int(resp['status']))

        def test_tenant_group_create_missing_token(self):
            h = httplib2.Http(".cache")
            resp, content = create_tenant("test_tenant", str(self.auth_token))
            if int(resp['status']) == 200:
                self.tenant = content['tenant']['id']

            url = '%stenant/%s/groups' % (URL, self.tenant)
            body = {"group": {"id": self.tenant_group,
                           "description": "A description ..."}}
            resp, content = h.request(url, "POST", body=json.dumps(body),
                                headers={"Content-Type": "application/json"})

            if int(resp['status']) == 500:
                self.fail('IDM fault')
            elif int(resp['status']) == 503:
                self.fail('Service Not Available')
            self.assertEqual(401, int(resp['status']))

        def test_tenant_group_create_disabled_token(self):
            h = httplib2.Http(".cache")
            resp, content = create_tenant("test_tenant", str(self.auth_token))
            respG, contentG = create_tenant_group('test_tenant_group', \
                                            'test_tenant', str(self.auth_token))
            if int(resp['status']) == 200:
                self.tenant = content['tenant']['id']

            url = '%stenant/%s/groups' % (URL, self.tenant)
            body = '{"group": { "id": "%s", \
                    "description": "A description ..." } }' % self.tenant_group
            resp, content = h.request(url, "POST", body=body,\
                                headers={"Content-Type": "application/json",\
                                         "X-Auth-Token": self.disabled_token})

            if int(resp['status']) == 500:
                self.fail('IDM fault')
            elif int(resp['status']) == 503:
                self.fail('Service Not Available')
            self.assertEqual(403, int(resp['status']))

        def test_tenant_group_create_invalid_token(self):
            h = httplib2.Http(".cache")
            resp, content = create_tenant("test_tenant", str(self.auth_token))
            if int(resp['status']) == 200:
                self.tenant = content['tenant']['id']

            url = '%stenant/%s/groups' % (URL, self.tenant)
            body = '{"group": { "id": "%s", \
                    "description": "A description ..." } }' % self.tenant
            resp, content = h.request(url, "POST", body=body,\
                                headers={"Content-Type": "application/json",\
                                         "X-Auth-Token": 'nonexsitingtoken'})

            if int(resp['status']) == 500:
                self.fail('IDM fault')
            elif int(resp['status']) == 503:
                self.fail('Service Not Available')
            self.assertEqual(401, int(resp['status']))

        def test_tenant_group_create_xml(self):
             resp, content = delete_tenant_xml('test_tenant', str(self.auth_token))
             resp, content = create_tenant_xml('test_tenant', str(self.auth_token))
             respG, contentG = delete_tenant_group_xml('test_tenant_group', \
                                            "test_tenant", str(self.auth_token))
             respG, contentG = create_tenant_group_xml('test_tenant_group', \
                                            "test_tenant", str(self.auth_token))

             self.tenant = 'test_tenant'
             self.tenant_group = 'test_tenant_group'
             content = etree.fromstring(content)
             if int(resp['status']) == 500:
                 self.fail('IDM fault')
             elif int(resp['status']) == 503:
                 self.fail('Service Not Available')

             if int(respG['status']) not in (200, 201):

                 self.fail('Failed due to %d' % int(respG['status']))

        def test_tenant_group_create_again_xml(self):

            resp, content = create_tenant_xml("test_tenant", str(self.auth_token))

            respG, contentG = create_tenant_group_xml('test_tenant_group', \
                                        "test_tenant", str(self.auth_token))
            respG, contentG = create_tenant_group_xml('test_tenant_group', \
                                        "test_tenant", str(self.auth_token))

            content = etree.fromstring(content)
            contentG = etree.fromstring(contentG)
            if int(respG['status']) == 200:
                self.tenant = content.get("id")
                self.tenant_group = contentG.get("id")

            if int(respG['status']) == 500:
                self.fail('IDM fault')
            elif int(respG['status']) == 503:
                self.fail('Service Not Available')
            self.assertEqual(409, int(respG['status']))
            if int(respG['status']) == 200:
                self.tenant = content.get("id")
                self.tenant_group = contentG.get("id")

        def test_tenant_group_create_forbidden_token_xml(self):
            h = httplib2.Http(".cache")
            resp, content = create_tenant("test_tenant", str(self.auth_token))
            if int(resp['status']) == 200:
                self.tenant = content['tenant']['id']

            url = '%stenant/%s/groups' % (URL, self.tenant)
            body = '<?xml version="1.0" encoding="UTF-8"?> \
                <group xmlns="http://docs.openstack.org/idm/api/v1.0" \
                 id="%s"> \
                <description>A description...</description> \
                </group>' % self.tenant_group
            resp, content = h.request(url, "POST", body=body,\
                                headers={"Content-Type": "application/xml", \
                                         "X-Auth-Token": self.token,
                                         "ACCEPT": "application/xml"})

            if int(resp['status']) == 500:
                self.fail('IDM fault')
            elif int(resp['status']) == 503:
                self.fail('Service Not Available')

            self.assertEqual(403, int(resp['status']))

        def test_tenant_group_create_expired_token_xml(self):
            h = httplib2.Http(".cache")
            resp, content = create_tenant_xml("test_tenant", str(self.auth_token))
            content = etree.fromstring(content)
            if int(resp['status']) == 200:
                self.tenant = content.get('id')

            url = '%stenant/%s/groups' % (URL, self.tenant)
            body = '<?xml version="1.0" encoding="UTF-8"?> \
                <group xmlns="http://docs.openstack.org/idm/api/v1.0" \
                 id="%s"> \
                <description>A description...</description> \
                </group>' % self.tenant

            resp, content = h.request(url, "POST", body=body,\
                                headers={"Content-Type": "application/xml", \
                                         "X-Auth-Token": self.exp_auth_token,
                                         "ACCEPT": "application/xml"})

            if int(resp['status']) == 500:
                self.fail('IDM fault')
            elif int(resp['status']) == 503:
                self.fail('Service Not Available')
            self.assertEqual(401, int(resp['status']))

        def test_tenant_group_create_missing_token_xml(self):
            h = httplib2.Http(".cache")
            resp, content = create_tenant_xml("test_tenant", str(self.auth_token))
            content = etree.fromstring(content)
            if int(resp['status']) == 200:
                self.tenant = content.get('id')

            url = '%stenant/%s/groups' % (URL, self.tenant)

            body = '<?xml version="1.0" encoding="UTF-8"?> \
                <group xmlns="http://docs.openstack.org/idm/api/v1.0" \
                id="%s"> \
                <description>A description...</description> \
                </group>' % self.tenant_group
            resp, content = h.request(url, "POST", body=body,\
                                headers={"Content-Type": "application/xml",
                                         "ACCEPT": "application/xml"})

            if int(resp['status']) == 500:
                self.fail('IDM fault')
            elif int(resp['status']) == 503:
                self.fail('Service Not Available')
            self.assertEqual(401, int(resp['status']))

        def test_tenant_group_create_disabled_token_xml(self):
            h = httplib2.Http(".cache")
            resp, content = create_tenant_xml("test_tenant", str(self.auth_token))
            content = etree.fromstring(content)
            if int(resp['status']) == 200:
                self.tenant = content.get('id')

            url = '%stenant/%s/groups' % (URL, self.tenant)
            body = '<?xml version="1.0" encoding="UTF-8"?> \
                    <group xmlns="http://docs.openstack.org/idm/api/v1.0" \
                id="%s"> \
                <description>A description...</description> \
                </group>' % self.tenant_group
            resp, content = h.request(url, "POST", body=body,\
                                headers={"Content-Type": "application/xml",
                                         "X-Auth-Token": self.disabled_token,
                                         "ACCEPT": "application/xml"})

            if int(resp['status']) == 500:
                self.fail('IDM fault')
            elif int(resp['status']) == 503:
                self.fail('Service Not Available')
            self.assertEqual(403, int(resp['status']))

        def test_tenant_group_create_invalid_token_xml(self):
            h = httplib2.Http(".cache")
            resp, content = create_tenant_xml("test_tenant", str(self.auth_token))
            content = etree.fromstring(content)
            if int(resp['status']) == 200:
                self.tenant = content.get('id')

            url = '%stenant/%s/groups' % (URL, self.tenant)
            body = '<?xml version="1.0" encoding="UTF-8"?> \
                <group xmlns="http://docs.openstack.org/idm/api/v1.0" \
                 id="%s"> \
                <description>A description...</description> \
                </group>' % self.tenant_group
            resp, content = h.request(url, "POST", body=body,\
                                headers={"Content-Type": "application/xml",\
                                         "X-Auth-Token": 'nonexsitingtoken',
                                         "ACCEPT": "application/xml"})

            if int(resp['status']) == 500:
                self.fail('IDM fault')
            elif int(resp['status']) == 503:
                self.fail('Service Not Available')
            self.assertEqual(401, int(resp['status']))

def setup():
    pass


def teardown():
    pass


if __name__ == '__main__':
    setup()
    try:
        unittest.main()
    finally:
        teardown()
