#! /usr/bin/env python

import luigi
import stats


if __name__ == '__main__':
    luigi.run(['stats.GenerateStatsTask', '--workers', '1', '--local-scheduler'])
