from __future__ import absolute_import
from __future__ import unicode_literals

import logging
import os
import re

import six

from . import verbose_proxy
from .. import config
from ..const import API_VERSIONS
from ..project import Project
from .docker_client import docker_client
from .docker_client import tls_config_from_options
from .utils import get_version_info

log = logging.getLogger(__name__)


def project_from_options(project_dir, options):
    return get_project(
        project_dir,
        get_config_path_from_options(options),
        project_name=options.get('--project-name'),
        verbose=options.get('--verbose'),
        host=options.get('--host'),
        tls_config=tls_config_from_options(options),
    )


def get_config_path_from_options(options):
    file_option = options.get('--file')
    if file_option:
        return file_option

    config_files = os.environ.get('COMPOSE_FILE')
    if config_files:
        return config_files.split(os.pathsep)
    return None


def get_client(verbose=False, version=None, tls_config=None, host=None):
    client = docker_client(version=version, tls_config=tls_config, host=host)
    if verbose:
        version_info = six.iteritems(client.version())
        log.info(get_version_info('full'))
        log.info("Docker base_url: %s", client.base_url)
        log.info("Docker version: %s",
                 ", ".join("%s=%s" % item for item in version_info))
        return verbose_proxy.VerboseProxy('docker', client)
    return client


def get_project(project_dir, config_path=None, project_name=None, verbose=False,
                host=None, tls_config=None):
    config_details = config.find(project_dir, config_path)
    project_name = get_project_name(config_details.working_dir, project_name)
    config_data = config.load(config_details)

    api_version = os.environ.get(
        'COMPOSE_API_VERSION',
        API_VERSIONS[config_data.version])
    client = get_client(
        verbose=verbose, version=api_version, tls_config=tls_config,
        host=host
    )

    return Project.from_config(project_name, config_data, client)


def get_project_name(working_dir, project_name=None):
    def normalize_name(name):
        return re.sub(r'[^a-z0-9]', '', name.lower())

    project_name = project_name or os.environ.get('COMPOSE_PROJECT_NAME')
    if project_name:
        return normalize_name(project_name)

    project = os.path.basename(os.path.abspath(working_dir))
    if project:
        return normalize_name(project)

    return 'default'
