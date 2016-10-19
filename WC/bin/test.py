#!/usr/bin/env python

from __future__ import with_statement
import contextlib
import os
import sys 

with contextlib.closing(open('/etc/mtab')) as fp: 
  for m in fp: 
    fs_spec, fs_file, fs_vfstype, fs_mntops, fs_freq, fs_passno = m.split()
    if fs_spec.startswith('/'):
      r = os.statvfs(fs_file)
      block_usage_pct = 100.0 - (float(r.f_bavail) / float(r.f_blocks) * 100)
      inode_usage_pct = 100.0 - (float(r.f_favail) / float(r.f_files) * 100)
      print "%d%%" % (block_usage_pct)

