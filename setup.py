# vim: filetype=python3 tabstop=2 expandtab

# itv
# Copyright (C) 2015 Jashandeep Sohi <jashandeep.s.sohi@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from itv import __version__, __doc__ as docstring
from distutils.core import setup

if __name__ == "__main__":    
  setup(
    name = "itv",
    version = __version__,
    description = docstring,
    long_description  = open("./README.rst", "r").read(),
    author = "Jashandeep Sohi",
    author_email = "jashandeep.s.sohi@gmail.com",
    url = "https://github.com/jashandeep-sohi/itv",
    license = "GPLv3",
    scripts = ["itv.py"],
    classifiers = [
     "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
     "Programming Language :: Python :: 3.4",
     "Programming Language :: Python :: 3 :: Only",
     "Development Status :: 4 - Beta",
     "Environment :: Console",
     "Intended Audience :: End Users/Desktop",
     "Operating System :: OS Independent",
    ],
  )
