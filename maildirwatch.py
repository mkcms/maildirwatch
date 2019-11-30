#!/usr/bin/env python3
# maildirwatch.py --- get notified when new mail arrives in maildir  -*- coding: utf-8; -*-
#
# Copyright (C) 2019 Michał Krzywkowski
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
"""Watch Maildir for new mail and display notifications.

This program allows you to watch a Maildir_ for incoming email and display
notifications when new messages arrive.

The displayed notifications are interactive - programs can be run when the user
clicks on them.

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
ignores spam folder and defines two actions::

  [global]
  maildir = ~/mail
  ignore = *Spam,*foo/bar*

  [actions]
  default = Show mu4e
  Show mu4e = emacs -f mu4e
  Start thunderbird = thunderbird

"""

__version__ = '0.1.1'

import argparse
import configparser
import email
import email.policy
import hashlib
import html
import logging
import os
import signal
import sys
from fnmatch import fnmatch
from functools import partial

if True:  # pylint: disable=using-constant-test
    # Keep this in an if block to keep isort from touching these lines.  isort
    # reorders the statements and puts imports first, but we need the call to
    # `require_version' before importing from gi.repository.
    import gi
    gi.require_version('Gtk', '3.0')
    gi.require_version('Gio', '2.0')
    gi.require_version('Notify', '0.7')
    from gi.repository import GLib, Gtk, Gio, Notify

config = configparser.ConfigParser()
config.add_section('global')
config.add_section('actions')
config['global']['ignore'] = ''
config['global']['maildir'] = '~/Maildir'

logger = logging.getLogger(__name__)


def hash_message(message):
    """Return a unique identifier for parsed email message.

    The identifier is used to compare messages for equality.

    `message` should be a dict-like object with keys named after email
    headers (e.g. ``From`, ``Subject``).

    """
    hasher = hashlib.sha1()
    hasher.update(message.get('Date', '').encode())
    hasher.update(message.get('From', '').encode())
    hasher.update(message.get('Message-Id', '').encode())
    hasher.update(message.get('Subject', '').encode())
    hasher.update(message.get('To', '').encode())
    return hasher.digest()


def iter_maildirs(directory):
    """Yield all maildirs in `directory`, recursively."""
    # Check if DIRECTORY is a maildir.
    newdir = os.path.join(directory, 'new')
    tmpdir = os.path.join(directory, 'tmp')
    curdir = os.path.join(directory, 'cur')
    if all(map(os.path.exists, (newdir, tmpdir, curdir))):
        yield directory

    # Scan recursively.
    for subdir in os.listdir(directory):
        subdirpath = os.path.join(directory, subdir)
        if os.path.isdir(subdirpath):
            yield from iter_maildirs(subdirpath)


def maildir_is_ignored(directory):
    """Check if `directory` is ignored in the config."""
    return any(
        map(
            partial(fnmatch, directory),
            config['global']['ignore'].split(',')))


def invoke_action(_notification, name):
    """Invoke action with `name`."""
    if name == 'default':
        action = config['actions']['default']
        command = config['actions'][action]
    else:
        command = config['actions'][name]

    logger.info('Action "%s" invoked by user, running command: %s', name,
                command)
    GLib.spawn_command_line_async(command)


class App:
    def __init__(self):
        self._queue = []
        self._notifications = []
        self._monitors = []
        self._timer = None

    def stop(self):
        """Cancel all directory monitors and the timer."""
        for monitor in self._monitors:
            monitor.cancel()
        self._monitors.clear()

        if self._timer is not None:
            GLib.source_remove(self._timer)
            self._timer = None

    def start(self):
        """Find maildirs, start watching them."""
        self.stop()

        directory = os.path.expanduser(config['global']['maildir'])
        for maildir in iter_maildirs(directory):
            if maildir_is_ignored(maildir):
                logger.info('Ignoring maildir %s', maildir)
                continue
            new_msg_dir = os.path.join(maildir, 'new')
            gfile = Gio.File.new_for_path(new_msg_dir)
            monitor = gfile.monitor_directory(Gio.FileMonitorFlags.WATCH_MOVES)
            self._monitors.append(monitor)
            monitor.connect('changed', self._handle_file_event)

            logger.info('Watching maildir %s', maildir)

    def _handle_file_event(self, _file_monitor, file, _other_file, event_type):
        if event_type not in (Gio.FileMonitorEvent.CREATED,
                              Gio.FileMonitorEvent.MOVED_IN):
            return

        path = file.get_path()
        logger.debug('Got file event file=%s, type=%s', path, event_type)

        try:
            with open(path) as inputfile:
                message = email.message_from_file(
                    inputfile, policy=email.policy.SMTP)
                self._queue.append(message)
        except FileNotFoundError:
            logger.error('Message file not found: %s', path)
            return

        if self._timer is not None:
            GLib.source_remove(self._timer)
        self._timer = GLib.timeout_add_seconds(60.0, self._handle_messages)

    def _handle_messages(self):
        logger.debug('dequeuing; queue size=%d', len(self._queue))
        if not self._queue:
            return True

        # Remove duplicate messages.
        messages = {hash_message(m): m for m in self._queue}.values()
        self._queue.clear()

        logger.info('Received %d new messages', len(messages))
        self._show_notification(messages)

        # Return False to stop the timer.
        self._timer = None
        return False

    def _show_notification(self, messages):
        summary = '{} new mail {} received'.format(
            len(messages), 'messages' if len(messages) != 1 else 'message')
        body = ''
        server_capabilities = Notify.get_server_caps()

        for message in messages:
            if body:
                body += '\n--\n'

            subject = message['Subject']
            sender = message['From']

            logger.info('From %s, Subject: %s', sender, subject)

            if 'body-markup' in server_capabilities:
                # Escape the notification body - needed for xfce4-notifyd which
                # fails to render body markup, because it thinks that
                # <email@email> is a tag.
                subject = html.escape(subject)
                sender = html.escape(sender)
                subject = '<b>{}</b>'.format(subject)
                sender = '<i>{}</i>'.format(sender)
            body += '{} from {}'.format(subject, sender)

        notification = Notify.Notification.new(
            summary=summary, body=body, icon='mail-unread')

        if 'actions' in server_capabilities:
            for action in config['actions']:
                notification.add_action(action, action, invoke_action)

        notification.connect('closed', self._on_notification_closed)
        self._notifications.append(notification)

        notification.show()

    def _on_notification_closed(self, notification):
        logger.debug('Notification %s closed', notification.props.id)
        self._notifications.remove(notification)


def main():
    logging.basicConfig(
        level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

    argv = Gtk.init(sys.argv)

    config_path = os.path.join(
        os.environ.get('XDG_CONFIG_HOME', '~/.config'), 'maildirwatch.conf')

    epilog = (
        'In addition to these arguments, you can also specify GTK options,\n'
        'see man page gtk-options(7) for details.')

    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog=epilog,
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        '-c',
        '--config',
        metavar='PATH',
        help='path to configuration file \n(default {})'.format(config_path),
        default=config_path)
    parser.add_argument(
        '-d', '--debug', action='store_true', help='set debug logging level')
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s {}'.format(__version__))

    args = parser.parse_args(argv[1:])

    if args.debug:
        logger.setLevel(logging.DEBUG)

    user_config_path = os.path.expanduser(args.config)
    logger.info('Loading config file %s', user_config_path)
    config.read(user_config_path)

    if not Notify.init('maildir-watch'):
        logger.critical('Could not init Notify')
        sys.exit(1)
    else:
        logger.debug('Notify server info: %s', Notify.get_server_info())
        logger.debug('Notify server capabilities: %s',
                     Notify.get_server_caps())

    app = App()
    app.start()

    success = True

    try:
        GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGINT,
                             Gtk.main_quit)

        def unhandled_exception_hook(etype, value, traceback):
            logger.exception(
                'Unhandled exception, exiting',
                exc_info=(etype, value, traceback))
            Gtk.main_quit()

            nonlocal success
            success = False

        # Install an unhandled exception handler which stops GTK event loop.
        sys.excepthook = unhandled_exception_hook

        Gtk.main()
    finally:
        logger.debug('About to exit, cleaning up')
        app.stop()
        Notify.uninit()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

# Local Variables:
# fill-column: 79
# End:
