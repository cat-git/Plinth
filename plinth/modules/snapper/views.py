#
# This file is part of Plinth.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

"""
Plinth module for configuring Snapper
"""

from django.contrib import messages
from django.template.response import TemplateResponse
from django.utils.translation import ugettext as _
import logging
import subprocess

from .forms import SnapperForm
from plinth import actions
from plinth import views
from plinth import package
from plinth.modules import snapper

logger = logging.getLogger(__name__)

class ConfigurationView(views.ConfigurationView):
	"""Serve configuration page."""
	form_class = SnapperForm

	def _apply_changes(request, old_status, new_status):
	    """Apply the changes."""
	    modified = False

	    if old_status['enabled'] != new_status['enabled']:
	        sub_command = 'enable' if new_status['enabled'] else 'disable'
	        modified = True
	        actions.superuser_run('snapper', [sub_command])
	        snapper.service.notify_enabled(None, new_status['enabled'])
	        messages.success(request, _('Configuration updated'))

	    if old_status['snapper'] != new_status['snapper'] and \
	       new_status['snapper'] != 'none':
	        modified = True
	        try:
	            actions.superuser_run('snapper', [new_status['snapper']])
	        except Exception as exception:
	            messages.error(request, _('Error setting Snapper status: {exception}')
	                           .format(exception=exception))
	        else:
	            messages.success(request, _('Snapper status set'))

	    if not modified:
	        messages.info(request, _('Setting unchanged'))