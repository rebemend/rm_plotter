from .pad import pad
import ROOT
from ROOT import TCanvas
from typing import Dict

import logging
log = logging.getLogger(__name__)


class canvas:
    """ Wrapper around TCanvas

    Automates few thinks which need to be done every time
    (e.g. drawin pads)
    """

    def __init__(self, name: str, x: int = 800, y: int = 800) -> None:
        """
        Arguments:
            name (``str``): name of canvas, used also as title
            x (``int``): x width of the canvas
            y (``int``): y width of the canvas
        """
        self.tcan = TCanvas(name, name, x, y)
        # TODO: still not 100% convinced we need a Dict and not just List
        self.pads: Dict[str, pad] = {}

        ROOT.gStyle.SetErrorX(0.5)

    def add_pad(self, p: "pad"):
        """ Adds pad to the canvas

        Arguments:
            p (``pad``): pad to be added to the canvas
        """
        self.pads[p.name] = p
        self.tcan.cd()
        p.tpad.Draw()

    def save(self, path: str):
        """ Simply calls SaveAs from TCanvas

        Arguments:
            path (``str``): path to target file
        """
        # TODO: maybe add automatic saving with multiple suffixes or something?
        self.tcan.SaveAs(path)