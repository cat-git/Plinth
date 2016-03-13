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
    backups = get_backups()

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
                             'backups': backups,
                             'form': form})


def get_status():
    """Get the current settings from server."""
    return {'enabled': snapper.is_enabled(),
            'is_running': snapper.is_running()}

def get_backups():
    """Get the list of backups from snapper."""
    snapshots = []

    try:
        output = subprocess.check_output(['snapper', '-q', '--iso', 'ls', '-t', 'single'])
        for line in output.decode().splitlines():
            parts = line.split('|')
            if not parts[0].startswith('-') and not parts[0].startswith('#'):
                snapshots.append({'number': parts[0], 'date': parts[1]})

        return snapshots
    except subprocess.CalledProcessError:
        return False
   

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
