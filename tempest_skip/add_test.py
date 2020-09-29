
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
import os
import tempfile
from argparse import ArgumentTypeError

import inquirer
import ruamel.yaml as yaml
import validators
from cliff.command import Command
from stestr import config_file
from tempest.cmd.init import TempestInit
from tempest.cmd.run import TempestRun


class AddTest(Command):
    """Command to add a test into the skiplist"""

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        self.log.debug('Running add_test command')
        self.abs_path = os.path.abspath(parsed_args.file)
        self.yaml_file = yaml.round_trip_load(open(self.abs_path),
                                              preserve_quotes=True)
        test_list = self._get_tests_list()
        filter_tests = list(filter(lambda x: parsed_args.test in x, test_list))
        if len(filter_tests) > 1:
            question = [inquirer.Checkbox('list_tests',
                                          'These are the tests available on '
                                          'the namespace, choose which ones '
                                          'you want to add. Press space to '
                                          'select',
                                          choices=filter_tests)]
            answers = inquirer.prompt(question)
            for test in answers.get('list_tests', []):
                self._add_test_in_yaml(test, parsed_args.deployment,
                                       parsed_args.release,
                                       parsed_args.reason, lp=parsed_args.lp,
                                       bz=parsed_args.bz, job=parsed_args.job)
        else:
            self._add_test_in_yaml(parsed_args.test, parsed_args.deployment,
                                   parsed_args.release,
                                   parsed_args.reason, lp=parsed_args.lp,
                                   bz=parsed_args.bz, job=parsed_args.job)

        with open(self.abs_path, 'w') as f:
            yaml.round_trip_dump(self.yaml_file, f,
                                 Dumper=yaml.RoundTripDumper,
                                 indent=4, block_seq_indent=2)

    def _add_test_in_yaml(self, test_name, deployment, release, reason,
                          lp=None, bz=None, job=None):
        was_inserted = False
        release_exist = False
        deployment_exist = False
        job_exist = False
        jobs = []
        for test in self.yaml_file.get('known_failures'):
            if test.get('test') == test_name:
                # Test already exist
                for d in test.get('deployment'):
                    if d == deployment:
                        deployment_exist = True

                for r in test.get('releases'):
                    if r.get('name') == release:
                        was_inserted = True
                        release_exist = True

                for j in test.get('jobs'):
                    if j == job:
                        job_exist = True

                if not release_exist:
                    entry = {'name': release,
                             'reason': reason}
                    if lp:
                        entry['lp'] = lp
                    if bz:
                        entry['bz'] = bz
                    test.get('releases').append(entry)
                    was_inserted = True
                if not deployment_exist:
                    test.get('deployment').append(deployment)
                if not job_exist:
                    test.get('jobs').append(job)

        if not was_inserted:
            release = {'name': release, 'reason': reason}
            if lp:
                release['lp'] = lp
            if bz:
                release['bz'] = bz
            if job:
                jobs = [job]
            entry = {'test': test_name, 'deployment': [deployment],
                     'releases': [release],
                     'jobs': jobs}
            self.yaml_file.get('known_failures').append(entry)
            self.log.debug('Test {} added with release {}'.format(
                test_name, release))
        else:
            self.log.warning(
                'Test {} already exist for release {}, doing nothing'.format(
                    test_name, release))

    def _get_tests_list(self):
        tempest_run = TempestRun(__name__, [])
        tempest_init = TempestInit(__name__, [])

        path = tempfile.mkdtemp(dir='/tmp')

        parser = tempest_init.get_parser(__name__)
        parser.workspace_path = None
        parser.name = path.split(os.path.sep)[-1]
        parser.config_dir = None
        parser.dir = path
        parser.show_global_dir = False

        tempest_init.take_action(parser)

        parser = tempest_run.get_parser('tempest')
        parser.list_tests = True
        parser.config_file = None
        parser.workspace = path.split(os.path.sep)[-1]
        parser.state = None
        parser.smoke = False
        parser.regex = ''
        parser.whitelist_file = None
        parser.blacklist_file = None
        parser.black_regex = None
        parser.workspace_path = None
        tempest_run._create_stestr_conf()

        #  config = os.path.join(path, '.stestr.conf')
        os.chdir(path)
        conf = config_file.TestrConf('.stestr.conf')
        cmd = conf.get_run_command()
        try:
            cmd.setUp()
            ids = cmd.list_tests()
        finally:
            cmd.cleanUp()

        return [i.split('[')[0] for i in ids]

    def _validate_url(self, url):
        if not validators.url(url):
            raise ArgumentTypeError('{} is not a valid url'.format(url))
        return url

    def get_parser(self, prog_name):
        parser = super(AddTest, self).get_parser(prog_name)
        parser.add_argument('--file', dest='file', required=True,
                            help='Skiplist config file')
        parser.add_argument('--release', dest='release', default='master',
                            help='Release where the test will be added')
        parser.add_argument('--job', dest='job',
                            help='Specify in which job this test will be '
                                 'skipped')
        parser.add_argument('--test', dest='test', required=True,
                            help='Test to be skipped')
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument('--lp', dest='lp',
                           help='Launchpad bug', type=self._validate_url)
        group.add_argument('--bz', dest='bz',
                           help='Bugzilla bug', type=self._validate_url)
        parser.add_argument('--reason', dest='reason', required=True,
                            help='Reason to test be skipped')
        parser.add_argument('--deployment', dest='deployment', required=False,
                            default='overcloud',
                            choices=['overcloud', 'undercloud'])
        return parser
