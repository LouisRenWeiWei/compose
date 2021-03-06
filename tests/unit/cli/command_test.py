from __future__ import absolute_import
from __future__ import unicode_literals

import os

import pytest

from compose.cli.command import get_config_path_from_options
from compose.const import IS_WINDOWS_PLATFORM
from tests import mock


class TestGetConfigPathFromOptions(object):

    def test_path_from_options(self):
        paths = ['one.yml', 'two.yml']
        opts = {'--file': paths}
        assert get_config_path_from_options(opts) == paths

    def test_single_path_from_env(self):
        with mock.patch.dict(os.environ):
            os.environ['COMPOSE_FILE'] = 'one.yml'
            assert get_config_path_from_options({}) == ['one.yml']

    @pytest.mark.skipif(IS_WINDOWS_PLATFORM, reason='posix separator')
    def test_multiple_path_from_env(self):
        with mock.patch.dict(os.environ):
            os.environ['COMPOSE_FILE'] = 'one.yml:two.yml'
            assert get_config_path_from_options({}) == ['one.yml', 'two.yml']

    @pytest.mark.skipif(not IS_WINDOWS_PLATFORM, reason='windows separator')
    def test_multiple_path_from_env_windows(self):
        with mock.patch.dict(os.environ):
            os.environ['COMPOSE_FILE'] = 'one.yml;two.yml'
            assert get_config_path_from_options({}) == ['one.yml', 'two.yml']

    def test_no_path(self):
        assert not get_config_path_from_options({})
