#! /usr/bin/env python

from os import environ as env

import luigi
import sentry_sdk

from stats.stats import GenerateStatsTask


SENTRY_DSN = env.get('SENTRY_DSN', None)
if SENTRY_DSN:
    sentry_sdk.init(dsn=SENTRY_DSN)


if __name__ == '__main__':
    luigi.run(
        ['stats.GenerateStatsTask', '--workers', '1', '--local-scheduler']
    )
