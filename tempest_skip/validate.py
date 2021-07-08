#!/usr/bin/python
# Copyright 2020 Red Hat, Inc.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import logging

from cliff.command import Command
import voluptuous as v
import yaml


class Validate(Command):
    "Command to validate the yaml file parsed to tempest skiplist"

    log = logging.getLogger(__name__)

    validate_skipped = v.Schema({
        'known_failures': [{
            v.Required('test'): str,
            v.Optional('bz'): v.Url(),
            v.Optional('lp'): v.Url(),
            v.Required('deployment'): [v.Any('undercloud', 'overcloud')],
            v.Optional('reason'): str,
            v.Required('releases'): [
                v.Schema({
                    v.Required('name'): str,
                    v.Required(v.SomeOf(
                        validators=[v.Any('lp', 'bz')], min_valid=1)): v.Url(),
                    v.Required('reason'): str,
                    v.Optional('installers'): [str]
                })
            ],
            v.Optional('jobs'): [str]
        }]
    })

    validate_allowed = v.Schema({
        'groups': [{
            v.Required('name'): str,
            v.Required('tests'): [str],
            v.Required('releases'): [str]
        }],
        'jobs': [{
            v.Required('name'): str,
            v.Required('tests'): [str],
            v.Required('releases'): [str]
        }]
    })

    def take_action(self, parsed_args):
        self.log.debug('Running validate command')
        yaml_file = yaml.safe_load(open(parsed_args.filename))
        if parsed_args.skipped:
            self.validate_skipped(yaml_file)
        if parsed_args.allowed:
            self.validate_allowed(yaml_file)

    def get_parser(self, prog_name):
        parser = super(Validate, self).get_parser(prog_name)
        parser.add_argument('--file', dest='filename',
                            help='Path to the YAML file to be validate',
                            required=True)

        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument('--skipped', dest='skipped', action='store_true',
                           default=False, help='Validate skipped schema')
        group.add_argument('--allowed', dest='allowed', action='store_true',
                           default=False, help='Validate allowed schema')
        return parser
