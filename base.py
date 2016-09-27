#! /usr/bin/env python

import luigi
from stats.stats import GenerateStatsTask


if __name__ == '__main__':
    luigi.run(
        ['stats.GenerateStatsTask', '--workers', '1', '--local-scheduler']
    )
