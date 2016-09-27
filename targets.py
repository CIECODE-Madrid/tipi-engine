import luigi

class VoidTarget(luigi.Target):

    def exists(self):
        return True
