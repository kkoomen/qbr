#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: fenc=utf-8 ts=4 sw=4 et


"""
Handle all config-related logic.
"""

import os
import json

CUBE_PALETTE = 'cube_palette'

class Config:

    def __init__(self):
        self.config_dir = os.path.expanduser('~/.config/qbr')
        self.settings_file = os.path.join(self.config_dir, 'settings.json')
        self.settings = self.get_settings()

        if not os.path.exists(self.config_dir):
            os.mkdir(self.config_dir)

    def get_settings(self, key=None, default_value=None):
        """Get user settings."""
        try:
            settings = self.settings
            if not isinstance(settings, dict):
                settings = json.loads(open(self.settings_file, 'r').read())
            if key in settings:
                return settings[key]
            if not default_value is None:
                return default_value
            return None
        except Exception as e:
            return {}

    def set_setting(self, key, value):
        """Set a specific setting and save it."""
        self.settings[key] = value
        with open(self.settings_file, 'w') as f:
            json.dump(self.settings, f)
            f.close()

config = Config()
