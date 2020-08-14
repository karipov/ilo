"""
Module to expose all config-related files
"""
import logging
import json
from pathlib import Path

CONFIG = json.load(open(Path.cwd().joinpath('src/config/config.json')))
REPLIES = json.load(open(Path.cwd().joinpath('src/config/replies.json')))


__all__ = ['CONFIG', 'REPLIES']