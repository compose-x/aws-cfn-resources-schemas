"""
Pytest path config
"""

from __future__ import absolute_import

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../aws_cfn_resources_schemas/")))
