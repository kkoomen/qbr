#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: fenc=utf-8 ts=4 sw=4 et

import os

# Global
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# i18n
LOCALES = {
    'en': 'English',
    'nl': 'Nederlands',
    'zh': '简体中文',
}

# Camera interface
STICKER_AREA_TILE_SIZE = 30
STICKER_AREA_TILE_GAP = 4
STICKER_AREA_OFFSET = 20
STICKER_CONTOUR_COLOR = (36, 255, 12)
CALIBRATE_MODE_KEY = 'c'
SWITCH_LANGUAGE_KEY = 'l'
TEXT_SIZE = 18

# Config
CUBE_PALETTE = 'cube_palette'
