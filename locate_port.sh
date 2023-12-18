#!/usr/bin/env bash
v4l2-ctl --list-devices
v4l2-ctl --list-formats-ext -d /dev/video0
