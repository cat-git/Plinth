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
Plinth module to configure snapper backups
"""

from django.utils.translation import ugettext_lazy as _

from plinth import action_utils
from plinth import cfg
from plinth import service as service_module

version = 1

depends = ['system']

title = _('System Snapshots')

description = [
    _('Things about snapper and that')
]

service = None


def init():
    """Intialize the Snapper module."""
    menu = cfg.main_menu.get('system:index')
    menu.add_urlname(_('System Snapshots'), 'glyphicon-save',
                     'snapper:index', 980)

    global service
    service = service_module.Service(
        'snapper', title, is_external=False, enabled=is_enabled())


def setup(helper, old_version=None):
    """Install and configure the module."""
    helper.install(['snapper'])
    helper.call('post', serice.notify_enabled, None, True)


def get_status():
    """Get the current settings from server."""
    return {
        'enabled': is_enabled(),
        'is_running': is_running()
    }


def is_enabled():
    """Return whether the module is enabled."""
    return action_utils.service_is_enabled('snapper')


def is_running():
    """Return whether the service is running."""
    return action_utils.service_is_running('snapper')

def diagnose():
    """Run diagnostics and return the results."""
    results = []
    results.append(_diagnose_volumes())

    return results

def _diagnose_volumes():
    return['not implemented']
