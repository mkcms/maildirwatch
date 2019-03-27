.. image:: https://badge.fury.io/py/maildirwatch.svg
    :target: https://badge.fury.io/py/maildirwatch

=====================================================================
 maildirwatch - Watch Maildir for new mail and display notifications
=====================================================================

The program scans a single directory recursively, looking for Maildirs_.  When
a Maildir is found, the program starts watching it for new email messages.
When email messages arrive to the ``new`` directory, a notification is
displayed with GTK.  The directory to scan can be set in a configuration file,
and it defaults to ``~/Maildir``.

A separate notification is **not** displayed for each email message that
arrives.  Instead, a single notification is displayed for a bunch of new
messages.

The displayed notification is interactive - actions can be performed when user
clicks on the notification.  By default, no actions are defined.  Actions can
be defined in the configuration file.

Installation
============

Installation from PyPI_::

  pip3 install --user maildirwatch

Python3 is required.

**Note**: PyGObject_ is a dependency of this program.  To successfully install it,
you might have to install GObject development libraries on your system.  On
Debian, the package ``libgirepository1.0-dev`` might have to be installed.

Usage
=====

Use the ``maildirwatch`` command to start the program, or::

  python3 -m maildirwatch

To list available options, run::

  maildirwatch --help

Configuration
=============

The program looks for the configuration file in
``$XDG_CONFIG_HOME/maildirwatch.conf`` or ``~/.config/maildirwatch.conf`` if
``XDG_CONFIG_HOME`` is not defined.

The configuration file is in Python's standard config format (understood by the
``configparser`` module).

Global options
--------------

These options should be put in the ``[global]`` section.

* ``maildir``

  The directory to scan for maildirs.  Default value: ``~/Maildir``.

* ``ignore``

  Comma-separated list of maildir patterns to ignore.  Each pattern must be in
  fnmatch_ style.  By default, no maildirs are ignored.

Actions
-------

Each action is a path to a program (and an optional list of arguments).  Every
action also has a unique name that is displayed to the user.  When an action
within a notification is clicked on, the action program is started.

Action definitions must be put in ``[actions]`` section.  Actions are defined
like this::

  action name = /path/to/program arg1 arg2 arg3...

Action names can contain spaces.

One action name is special - the ``default`` action.  The default action's
value should be the name of another action instead of path to a program.  The
default action is invoked when the user clicks on the notification itself, not
any other action.

Example configuration
---------------------

Here is an example configuration file that modifies path to the Maildir,
ignores spam folder and defines two actions::

  [global]
  maildir = ~/mail
  ignore = *Spam,*foo/bar*

  [actions]
  default = Show mu4e
  Show mu4e = emacs -f mu4e
  Start thunderbird = thunderbird


License
=======

::

   Copyright (C) 2019 Michał Krzywkowski

   This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program.  If not, see <https://www.gnu.org/licenses/>.

.. _Maildirs: https://cr.yp.to/proto/maildir.html
.. _PyPI: https://pypi.org/
.. _PyGObject: https://pypi.org/project/PyGObject/
.. _fnmatch: https://docs.python.org/3/library/fnmatch.html
..

   Local Variables:
   coding: utf-8
   fill-column: 79
   End:
