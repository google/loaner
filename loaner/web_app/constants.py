# Copyright 2018 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""App constants to be set before deployment."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import jinja2

from google.appengine.api import app_identity

import endpoints

from loaner.web_app.backend.models import template_model


# The application id for this project otherwise known as the Google Cloud
# Project ID.
APPLICATION_ID = os.environ.get('APPLICATION_ID', None)

# Whether or not the application is running on the dev_appserver.
ON_LOCAL = (
    os.getenv('SERVER_SOFTWARE') and
    os.getenv('SERVER_SOFTWARE').startswith('Development/'))

# Whether or not the application is running on Google App Engine.
ON_GAE = (
    os.getenv('SERVER_SOFTWARE') and
    os.getenv('SERVER_SOFTWARE').startswith('Google App Engine/'))


################################################################################
# Everything in this comment block must be configured before the app can be
# built and deployed, see the developer docs for more detail.

# This is the friendly name of the application that will be displayed to users
# of this application as the title of the Web App.
APP_NAME = 'Grab n Go'

# The top level domain for the GSuite accounts used in this application.
APP_DOMAINS = ['example.com']

# The GSuite Customer ID this application will interact with, if nothing is
# provided it will default to the helper string 'my_customer'.
# NOTE: using my_customer is an approved method for the used APIs.
CUSTOMER_ID = ('' or 'my_customer')

# The absolute path to config_defaults.yaml.
CONFIG_DEFAULTS_PATH = (
    os.path.join(os.path.dirname(__file__), 'config_defaults.yaml'))

# Setup of Jinja2 Enviorment for serving backend/static_content templates.
JINJA = jinja2.Environment(
    autoescape=True, loader=jinja2.FileSystemLoader(
        os.path.join(os.path.dirname(__file__), 'backend/static_content')))

# Variables defining different deployment environments, place the Google Cloud
# Project ID for each environment on the appropriate line.
# NOTE: These must match the Google Cloud Project ID's in the
# //loaner/deployments/deploy.sh file for DEV, QA, and PROD respectively.
ON_PROD = ON_GAE and ('prod-app-engine-project' in APPLICATION_ID)

# If you are using a QA server fill out the Google Cloud Project ID below.
ON_QA = ON_GAE and ('qa-app-engine-project' in APPLICATION_ID)

# If you are using a DEV server fill out the Google Cloud Project ID below.
ON_DEV = ON_GAE and ('dev-app-engine-project' in APPLICATION_ID)

# Maintenance mode, serves a splash page when the app is under maintenance.
MAINTENANCE = False

# The email address of the GSuite Admin to use for Domain Wide Delegated
# Authority for access to the Google Admin SDK Directory API.
# NOTE: The account used here must at least have access to the OAuth2 Scopes
# listed below in the DIRECTORY_SCOPES variable.
ADMIN_EMAIL = '{ADMIN_EMAIL}'

# The email address application emails will come from.
SEND_EMAIL_AS = 'noreply@example.com'

# superadmins_group: str, The name of the Google Group that governs who is
# a superadmin. Superadmins have all permissions by default.
SUPERADMINS_GROUP = 'technical-admins@example.com'

# The PROD server specific configurations.
if ON_PROD:
  # The OAuth2 Client ID for the Chrome Application.
  CHROME_CLIENT_ID = ''
  # The OAuth2 Client ID for the Web Application Frontend.
  WEB_CLIENT_ID = ''
  # The location of the Client Secrets file relative to the Bazel WORKSPACE for
  # the Directory API Service Account with Domain Wide Delegated privilage.
  # i.e. loaner/web_app/client-secret.json
  SECRETS_FILE = ''
  # The parent Org Unit this application will use to move devices within. This
  # Org Unit should contain the configuration specific to ALL Grab n Go Loaner
  # devices.
  PARENT_ORG_UNIT = 'Grab n Go/Prod'
elif ON_QA:
  CHROME_CLIENT_ID = ''
  WEB_CLIENT_ID = ''
  SECRETS_FILE = ''
  PARENT_ORG_UNIT = 'Grab n Go/QA'
# The DEV server specific configurations.
elif ON_DEV:
  CHROME_CLIENT_ID = ''
  WEB_CLIENT_ID = ''
  SECRETS_FILE = ''
  PARENT_ORG_UNIT = 'Grab n Go/Dev'
# The LOCAL server specific configurations.
else:
  CHROME_CLIENT_ID = ''
  WEB_CLIENT_ID = ''
  SECRETS_FILE = ''
  PARENT_ORG_UNIT = 'Grab n Go/Dev'

# When set to True the Application will Bootstrap, performing initialization of
# the application. On first deployment this should be set to True, for all
# following deployments this should be set to False.
BOOTSTRAP_ENABLED = True
################################################################################

if ON_LOCAL:
  ORIGIN = 'localhost:8080'
  ENDPOINTS_HOSTNAME = 'localhost:8081'
elif ON_PROD or ON_DEV or ON_QA:
  ORIGIN = app_identity.get_default_version_hostname()
  ENDPOINTS_HOSTNAME = 'endpoints-dot-{}'.format(ORIGIN)
else:
  ORIGIN = ''
  ENDPOINTS_HOSTNAME = ''

PROJECT_ROOT = os.path.dirname(__file__)
FRONTEND_ROOT = os.path.join(PROJECT_ROOT, 'frontend', 'src')
ANGULAR_TEMPLATE = 'index.html'
ANGULAR_TEMPLATE_PATH = os.path.join(FRONTEND_ROOT, ANGULAR_TEMPLATE)
COMPILED_JS_PATH = os.path.join(FRONTEND_ROOT, 'application.js')

# The OAuth2 Client ID's that are allowed to access the Endpoints API's
# configured in the endpoints.py and chrome.py files.
ALLOWED_CLIENT_IDS = (
    CHROME_CLIENT_ID, WEB_CLIENT_ID, endpoints.API_EXPLORER_CLIENT_ID,
)

# OAuth2 Scopes to request when an application user authenticates to the web
# frontend.
ROOT_SCOPES = (
    'https://www.googleapis.com/auth/userinfo.email',
)

# OAuth2 Scopes for the Directory API client and the configured admin account.
DIRECTORY_SCOPES = (
    'https://www.googleapis.com/auth/admin.directory.device.chromeos',
    'https://www.googleapis.com/auth/admin.directory.group.member.readonly',
    'https://www.googleapis.com/auth/admin.directory.orgunit',
    'https://www.googleapis.com/auth/admin.directory.user.readonly',
)

# Dictionary defining where Grab n Go Loaner devices will be moved to enable and
# disable guest mode if guest mode is permitted for this version.
# NOTE: whether Guest Mode is allowed is configured in config_defaults.yaml.
ORG_UNIT_DICT = {
    'DEFAULT': PARENT_ORG_UNIT + '/Default',
    'GUEST': PARENT_ORG_UNIT + '/Guest Enabled',
}

CHROME_FIELDS_MASK = 'deviceId,serialNumber,model,orgUnitPath'
CHROME_LIST_FIELDS_MASK = (
    'chromeosdevices(deviceId,serialNumber,model,orgUnitPath)')
GROUP_MEMBER_FIELDS_MASK = 'members/email,nextPageToken'
USER_NAME_FIELDS_MASK = 'name/givenName'
ORG_UNIT_FIELDS_MASK = 'name'

XSRF_TOKEN_TIMEOUT = 8 * 60 * 60 * 10**6  # 8 hours in microseconds.
XSRF_ACTION_ID = ''
XSRF_HEADER = 'X-XSRF-TOKEN'
XSRF_COOKIE_NAME = 'XSRF-TOKEN'
XSRF_PARAM = 'xsrf_token'
XSRF_EXEMPT_METHODS = frozenset(['GET', 'HEAD'])

BIGQUERY_DATASET_NAME = 'loaner'
BIGQUERY_DEVICE_TABLE = 'Device'
BIGQUERY_SHELF_TABLE = 'Shelf'
BIGQUERY_SURVEY_TABLE = 'Question'
BIGQUERY_ROW_TIME_THRESHOLD = 15  # Minutes.
BIGQUERY_ROW_SIZE_THRESHOLD = 50  # Rows.
BIGQUERY_ROW_MAX_BATCH_SIZE = 500  # Rows.

DEFAULT_ACTING_USER = 'Loaner Role'

TEMPLATE_LOADER = template_model.TemplateLoader()

# Search constants.
DEVICE_INDEX_NAME = 'device_index'
SHELF_INDEX_NAME = 'shelf_index'
