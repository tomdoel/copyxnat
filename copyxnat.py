#!/usr/bin/python
#  -*- coding: utf-8 -*-
import sys

from copyxnat.ui.copyxnat_command_line import run_command_line

if __name__ == "__main__":
    sys.exit(run_command_line(sys.argv[1:]))
