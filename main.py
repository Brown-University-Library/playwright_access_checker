"""
Runs one configured access trial or previews and rebuilds local results.
"""

import json
import sys

from lib.config import ROOT, public_settings, read_settings
from lib.results import rebuild_report


def main() -> None:
    """
    Parses options and calls settings, browser, or offline reporting helpers.
    Called by: module guard
    """
    settings, args = read_settings()
    if args.rebuild_report:
        rebuild_report((ROOT / args.rebuild_report).resolve())
        print('Rebuilt run.json and summary.md from saved events.')
    elif args.preview:
        print(json.dumps(public_settings(settings), indent=2, allow_nan=False))
    else:
        from lib.browser_flow import run_trial

        recorder = run_trial(settings)
        print(f'Trial {recorder.trial_id}: {recorder.metadata["stop_reason"]}')
        print(f'Results: {settings.output_dir}/{recorder.trial_id}/summary.md')
        reason = recorder.metadata['stop_reason']
        sys.exit(0 if reason == 'workflow_complete' else 130 if reason == 'user_interrupted' else 1)


if __name__ == '__main__':
    main()
