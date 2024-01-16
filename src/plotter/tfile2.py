from ROOT import TFile
import ROOT


class TFile2(TFile):
    """TFile with some better functionalities
    to enter file/dirs with context manager
    https://docs.python.org/3/library/stdtypes.html#typecontextmanager

    'If TFile is so good, why is there no TFile2?'
    """

    def __init__(self, *args, **kwargs):
        super(TFile2, self).__init__(*args, **kwargs)

    def mkdir(self, dirName: str):
        """Create directory with context manager
        to enter it.
        """
        return _MkdirContext(self, dirName)

    # __enter__ and __exit__ are available
    # since version 6.28 in ROOT but since lot
    # of codes still use 6.26, adding them
    # as backup here as well
    def _enter(self):
        return self

    def _exit(self, exc_type, exc_val, exc_tb):
        self.Close()
        return False


class _MkdirContext:
    """Context manager for TFile.mkdir.

    Arguments:
        tFile (`TFile`): TFile
        dirName (`str`): directory name
    """

    def __init__(self, tFile: TFile, dirName: str):
        self.tFile = tFile
        self.dirName = dirName
        self._dir = self.tFile.GetDirectory(self.dirName)
        if not self._dir:
            self._dir = self.tFile.mkdir(self.dirName)

        self.old_dir = None

    def __enter__(self):
        self.old_dir = ROOT.gDirectory
        self._dir.cd()
        return self._dir

    def __exit__(self, type, value, traceback):
        if self.old_dir:
            self.old_dir.cd()
        return False
