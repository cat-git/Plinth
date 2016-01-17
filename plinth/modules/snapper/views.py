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
Plinth module for configuring date and time
"""

from django.contrib import messages
from django.template.response import TemplateResponse
from django.utils.translation import ugettext as _
import logging

from .forms import SnapperForm
from plinth import actions
from plinth import package
from plinth.modules import snapper

logger = logging.getLogger(__name__)


def on_install():
    """Notify that the service is now enabled."""
    snapper.service.notify_enabled(None, True)


@package.required(['snapper'], on_install=on_install)
def index(request):
    """Serve configuration page."""
    status = get_status()

    form = None

    if request.method == 'POST':
        form = SnapperForm(request.POST, prefix='snapper')
        # pylint: disable=E1101
        if form.is_valid():
            _apply_changes(request, status, form.cleaned_data)
            status = get_status()
            form = SnapperForm(initial=status, prefix='snapper')
    else:
        form = SnapperForm(initial=status, prefix='snapper')

    return TemplateResponse(request, 'snapper.html',
                            {'title': _('Backup Freedombox'),
                             'status': status,
                             'form': form})


def get_status():
    """Get the current settings from server."""
    return {'enabled': snapper.is_enabled(),
            'is_running': snapper.is_running(),
            'time_zone': get_current_time_zone()}


def get_current_time_zone():
    """Get current time zone."""
    time_zone = open('/etc/timezone').read().rstrip()
    return time_zone or 'none'


def _apply_changes(request, old_status, new_status):
    """Apply the changes."""
    modified = False

    if old_status['enabled'] != new_status['enabled']:
        sub_command = 'enable' if new_status['enabled'] else 'disable'
        modified = True
        actions.superuser_run('snapper', [sub_command])
        snapper.service.notify_enabled(None, new_status['enabled'])
        messages.success(request, _('Configuration updated'))

    if old_status['time_zone'] != new_status['time_zone'] and \
       new_status['time_zone'] != 'none':
        modified = True
        try:
            actions.superuser_run('timezone-change', [new_status['time_zone']])
        except Exception as exception:
            messages.error(request, _('Error setting time zone: {exception}')
                           .format(exception=exception))
        else:
            messages.success(request, _('Time zone set'))

    if not modified:
        messages.info(request, _('Setting unchanged'))
