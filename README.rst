.. image:: https://badge.fury.io/py/maildirwatch.svg
    :target: https://badge.fury.io/py/maildirwatch

=====================================================================
 maildirwatch - Watch Maildir for new mail and display notifications
=====================================================================

This program allows you to watch a Maildir_ for incoming email and display
notifications when new messages arrive.

The displayed notifications are interactive - programs can be run when the user
clicks on them.

Installation
============

Installation from PyPI::

  pip3 install --user maildirwatch

Python3 is required.

**Note**: PyGObject_ is a dependency of this program.  To install it, you might
have to install GObject development libraries on your system.  On Debian, the
packages ``libgirepository1.0-dev`` and ``gir1.2-notify-0.7`` provide these
libraries.

Usage
=====

Use the ``maildirwatch`` command, or::

  python3 -m maildirwatch

The program will run forever or until you interrupt it with `Ctrl-C`.

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

* ``whitelist``

  Comma-separated list of maildir patterns to watch, even if they're matched by
  ``ignore``.

  You can explicitly select maildirs to watch by setting ``ignore`` to
  ``**/**`` and ``whitelist`` to patterns that you want to watch,
  e.g. ``*Inbox*,*Important*``.

* ``inhibit-command``

  Command to run to check if notifications should be inhibited.  If the command
  exits with 0, the notification is NOT displayed and only a message is logged.
  Otherwise the notification is displayed.

  If this is undefined, notifications are always displayed.

Actions
-------

Each action is a path to a program and a list of arguments.  Every action also
has a name that is displayed to the user.

Actions are typically displayed as text buttons below the notification body.
When the user clicks on the action button, the action program is started.

Action definitions must be put in ``[actions]`` section.  Each action is
defined like this::

  action name = /path/to/program arg1 arg2 arg3...

One action name is special - the ``default`` action.  The default action's
value should be the name of another action instead of path to a program.  The
program associated with default action is run when the user clicks on the
notification itself, not an action button.

Example configuration
---------------------

Below is an example configuration file that modifies path to the Maildir,
ignores spam folder, defines two actions and disables notifications if VLC is
running::

  [global]
  maildir = ~/mail
  ignore = *Spam,*foo/bar*
  inhibit-command = pgrep vlc

  [actions]
  default = Show mu4e
  Show mu4e = emacs -f mu4e
  Start thunderbird = thunderbird


License
=======

::

   Copyright (C) 2019-2024 Michał Krzywkowski

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

.. _Maildir: https://en.wikipedia.org/wiki/Maildir
.. _PyGObject: https://pypi.org/project/PyGObject/
.. _fnmatch: https://docs.python.org/3/library/fnmatch.html

..
   Local Variables:
   coding: utf-8
   fill-column: 79
   End:
