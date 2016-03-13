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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

"""
Forms for configuring snapper backups
"""

from django import forms
from django.utils.translation import ugettext_lazy as _
import glob
import re


class SnapperForm(forms.Form):
    """Snapper configuration form."""
    enabled = forms.BooleanField(
        label=_('Enable System Snapshots'),
        required=False)

    volume = forms.ChoiceField(
        label=_('Volumes'),
        help_text=_('Choose a volume to backup.'))

    def __init__(self, *args, **kwargs):
        """Initialize the snapper form."""
        forms.Form.__init__(self, *args, **kwargs)

        self.fields['volume'].choices = [('/', 'root'), ('/home', 'home')]
