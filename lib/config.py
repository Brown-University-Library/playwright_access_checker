"""
Reads and validates settings for one Studio browsing trial.
"""

import argparse
import ipaddress
import math
import os
import re
import secrets
import tempfile
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo

from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parent.parent
EASTERN = ZoneInfo('America/New_York')


@dataclass
class Settings:
    collection_id: str = ''
    workflow: str = ''
    open_interval_seconds: float = 1.0
    open_jitter_seconds: float = 0.1
    view_seconds: float = 5.0
    view_jitter_seconds: float = 0.5
    selection_start: int = 1
    seed: int = 0
    max_duration_seconds: float = 300.0
    max_items: int = 20
    max_scroll_actions: int = 20
    navigation_timeout_seconds: float = 30.0
    cf_settings_label: str = ''
    cf_settings_notes: str = ''
    cf_settings_since: str = 'unknown'
    network_label: str = 'unknown'
    public_ip: str = 'unknown'
    ip_notes: str = 'Public IP and its recent use have not been verified.'
    proxy_server: str = ''
    output_dir: str = '../runs'
    bdr_hosts: str = 'repository.library.brown.edu'
    proxy_username: str = field(default='', repr=False)
    proxy_password: str = field(default='', repr=False)
    sources: dict[str, str] = field(default_factory=dict)
    unused: dict[str, object] = field(default_factory=dict)

    @property
    def collection_url(self) -> str:
        """
        Constructs the first visit without visiting the default listing.
        Called by: browser_flow.run_trial(), public_settings()
        """
        return f'https://repository.library.brown.edu/studio/collections/{self.collection_id}/?page=1&per_page=50'

    @property
    def hosts(self) -> set[str]:
        """
        Lists exact hostnames whose requests belong to the measurement.
        Called by: browser_flow.Observer
        """
        return {host.strip().lower() for host in self.bdr_hosts.split(',')}


def make_parser() -> argparse.ArgumentParser:
    """
    Defines trial options and the offline preview and report commands.
    Called by: read_settings()
    """
    parser = argparse.ArgumentParser(description='Runs one visible Studio browsing trial and saves local evidence.')
    parser.add_argument('collection_id', nargs='?', help='Studio PID, for example bdr:nz9qn2kb.')
    defaults = Settings()
    for name, value in asdict(defaults).items():
        if name not in {'collection_id', 'sources', 'unused', 'proxy_username', 'proxy_password'}:
            parser.add_argument('--' + name.replace('_', '-'), type=type(value), default=None)
    parser.add_argument('--preview', action='store_true', help='Validates and prints settings without network requests.')
    parser.add_argument('--rebuild-report', metavar='TRIAL_DIR', help='Rebuilds a saved report without opening a browser.')
    return parser


def read_settings(
    argv: list[str] | None = None, environ: dict[str, str] | None = None, root: Path = ROOT
) -> tuple[Settings, argparse.Namespace]:
    """
    Chooses CLI, environment, explicit outer .env, then default values.
    Called by: main.main()
    """
    parser = make_parser()
    args = parser.parse_args(argv)
    settings = Settings()
    if not args.rebuild_report:
        environment = dict(os.environ) if environ is None else environ
        file_values = dotenv_values(root.parent / '.env', interpolate=False)
        for name, default in asdict(settings).items():
            if name in {'sources', 'unused'}:
                continue
            cli_value = getattr(args, name, None)
            env_name = name.upper()
            source = 'default'
            value = default
            if cli_value is not None:
                value, source = cli_value, 'command line'
            elif env_name in environment:
                value, source = environment[env_name], 'environment'
            elif file_values.get(env_name) is not None:
                value, source = file_values[env_name], '../.env'
            try:
                setattr(settings, name, type(default)(value))
            except (TypeError, ValueError):
                parser.error(f'{env_name} has an invalid {type(default).__name__} value.')
            if name not in {'proxy_username', 'proxy_password'}:
                settings.sources[name] = source
        if settings.sources['seed'] == 'default':
            settings.seed = secrets.randbits(63)
            settings.sources['seed'] = 'generated'
        try:
            validate(settings, args, root)
        except (ValueError, OSError) as exc:
            parser.error(str(exc) if isinstance(exc, ValueError) else 'Cannot write to OUTPUT_DIR.')
    return settings, args


def validate(settings: Settings, args: argparse.Namespace, root: Path = ROOT) -> None:
    """
    Rejects invalid settings before a browser can contact Studio.
    Called by: read_settings()
    """
    if not re.fullmatch(r'bdr:[A-Za-z0-9]+', settings.collection_id):
        raise ValueError('COLLECTION_ID must be a Studio PID such as bdr:nz9qn2kb.')
    if settings.workflow not in {'tabs', 'return'}:
        raise ValueError('WORKFLOW must be tabs or return.')
    if not settings.cf_settings_label.strip() or not settings.cf_settings_notes.strip():
        raise ValueError('CF_SETTINGS_LABEL and CF_SETTINGS_NOTES are required; use unknown where appropriate.')
    if settings.selection_start not in {1, 2} or not 1 <= settings.max_items <= 20:
        raise ValueError('SELECTION_START must be 1 or 2; MAX_ITEMS must be between 1 and 20.')
    for name in ('max_duration_seconds', 'navigation_timeout_seconds', 'max_scroll_actions'):
        value = getattr(settings, name)
        if not math.isfinite(value) or value <= 0:
            raise ValueError(f'{name.upper()} must be finite and greater than zero.')
    timing_names = ['view', 'open']
    if settings.workflow == 'return':
        for name in ('open_interval_seconds', 'open_jitter_seconds'):
            if getattr(args, name, None) is not None:
                raise ValueError('Opening timing command-line options are not used by the return workflow.')
            settings.unused[name] = {'value': getattr(settings, name), 'source': settings.sources.get(name, 'default')}
    for prefix in timing_names:
        target = settings.view_seconds if prefix == 'view' else settings.open_interval_seconds
        jitter = getattr(settings, prefix + '_jitter_seconds')
        if not math.isfinite(target) or not math.isfinite(jitter) or not (target > 0 and 0 <= jitter < target):
            raise ValueError(f'{prefix} timing requires finite values: target > 0 and 0 <= jitter < target.')
    if settings.public_ip != 'unknown':
        try:
            ipaddress.ip_address(settings.public_ip)
        except ValueError:
            raise ValueError('PUBLIC_IP must be an IP address or unknown.') from None
    if settings.cf_settings_since != 'unknown':
        try:
            since = datetime.fromisoformat(settings.cf_settings_since)
            if since.tzinfo is None:
                raise ValueError
            settings.cf_settings_since = since.astimezone(EASTERN).strftime('%Y-%m-%dT%H:%M:%S%z %Z')
        except ValueError:
            raise ValueError('CF_SETTINGS_SINCE must be an ISO date/time with a UTC offset, or unknown.') from None
    if settings.proxy_server:
        try:
            proxy = urlsplit(settings.proxy_server)
            valid = (
                proxy.scheme in {'http', 'https', 'socks5'}
                and proxy.hostname
                and proxy.port
                and not proxy.username
                and not proxy.password
                and proxy.path in {'', '/'}
                and not proxy.query
                and not proxy.fragment
            )
        except ValueError:
            valid = False
        if not valid:
            raise ValueError('PROXY_SERVER must contain an http, https, or socks5 host and port without login details.')
        if proxy.scheme == 'socks5' and (settings.proxy_username or settings.proxy_password):
            raise ValueError('Chromium does not support SOCKS5 proxy authentication; use a prepared unauthenticated proxy.')
    elif settings.proxy_username or settings.proxy_password:
        raise ValueError('Proxy credentials require PROXY_SERVER.')
    if any(not re.fullmatch(r'[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?', host) for host in settings.hosts):
        raise ValueError('BDR_HOSTS must be a comma-separated list of exact hostnames.')
    if 'repository.library.brown.edu' not in settings.hosts:
        raise ValueError('BDR_HOSTS must include repository.library.brown.edu.')
    output = (root / settings.output_dir).resolve()
    if output == root.resolve() or root.resolve() in output.parents:
        raise ValueError('OUTPUT_DIR must be outside the Git repository.')
    parent = output
    while not parent.exists():
        parent = parent.parent
    with tempfile.TemporaryFile(dir=parent):
        pass
    if output.exists() and not output.is_dir():
        raise ValueError('OUTPUT_DIR must be a directory.')


def public_settings(settings: Settings) -> dict[str, object]:
    """
    Includes only intended settings, with proxy credentials omitted.
    Called by: main.main(), results.Recorder.__init__()
    """
    values = asdict(settings)
    for name in ('proxy_username', 'proxy_password'):
        values.pop(name)
    values.update(collection_url=settings.collection_url, page=1, per_page=50, timezone='America/New_York')
    values.update(scroll_fraction=0.8, pause_seconds=1.0, cf_settings_source='user supplied')
    values['output_dir'] = os.path.relpath((ROOT / settings.output_dir).resolve(), ROOT)
    return values
