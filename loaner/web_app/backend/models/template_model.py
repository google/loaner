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

"""A model representing a Jinja2 template and helper functions."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import re
import jinja2

from google.appengine.api import memcache
from google.appengine.ext import ndb


_CACHED_TITLE_NAME = 'template:title:%s'
_CACHED_BODY_NAME = 'template:body:%s'
_NAME_RE = re.compile(r'^template:(\w+):(\w+)$')


class Error(Exception):
  """Base class for exceptions."""


class NoTemplateError(Error):
  """Error raised when a requested template does not exist."""


class Template(ndb.Model):
  """Model representing a template."""
  title = ndb.StringProperty()
  body = ndb.TextProperty()

  @property
  def name(self):
    """Pseudo-property for name, from the ID."""
    return self.key.id()

  @classmethod
  def create(cls, name, title=None, body=None):
    """Creates a model and entity."""
    entity = cls.get_or_insert(name)
    entity.title = title
    entity.body = body
    entity.put()
    return entity


class TemplateLoader(object):
  """Loader for Jinja2 templates."""

  def __init__(self):
    self.jinja = jinja2.Environment(
        loader=jinja2.FunctionLoader(self._get_subtemplate), autoescape=True)
    self.templates_cached = False

  def _cache_template(self, template):
    """Caches the title and body of a Template separately in memcache."""
    memcache.set(_CACHED_TITLE_NAME % template.name, template.title)
    memcache.set(_CACHED_BODY_NAME % template.name, template.body)

  def _cache_all_templates(self):
    """Fetches and caches all Template entities."""
    for template in Template.query().fetch():
      self._cache_template(template)

  def _get_subtemplate(self, sub_name):
    """Gets a template from memcache or datastore for the Jinja2 environment.

    This gets either a sub-component of a Template entity (title or body).

    Args:
      sub_name: str, the name of the subcomponent of the Template (e.g.,
          'template:title:device_due' for the title property of the device_due
          template. If the sub_name is 'base' it gets the body of the base
          template, which has no title.

    Returns:
      The pre-rendered Jinja2-formatted template string.

    Raises:
      NoTemplateError: if the template with that sub-name does not exist.
    """
    if not self.templates_cached:
      self._cache_all_templates()
    if sub_name.endswith('_base'):
      sub_name = _CACHED_BODY_NAME % sub_name
    cached_template = memcache.get(sub_name)
    if cached_template:
      return cached_template
    else:
      match = _NAME_RE.match(sub_name)
      template_name = match.group(2)  # Stripped template name.
      stored_template = Template.get_by_id(template_name)
      if not stored_template:
        raise NoTemplateError(
            'Template named {} does not exist.'.format(sub_name))
      self._cache_template(stored_template)
      return getattr(stored_template, match.group(1))  # 'title' or 'body'.

  def render(self, name, config_dict):
    """Fetches and renders the title and body of a Template entity.

    Args:
      name: str, the template name.
      config_dict: dict, the configuration for populating the template.

    Returns:
      A tuple consisting of (rendered title, rendered body).
    """
    return (
        self.jinja.get_template(_CACHED_TITLE_NAME % name).render(config_dict),
        self.jinja.get_template(_CACHED_BODY_NAME % name).render(config_dict))
