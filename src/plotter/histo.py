import ROOT
from ROOT import TH1
from plotter import thHelper
from typing import Optional

import logging
log = logging.getLogger(__name__)

ROOT.TH1.AddDirectory(False)


class histo:
    """ Wrapper class around TH1, setups the main properties
        + contains few usefull function (e.g. divide_ratio)

        The idea is that the rather short constructor holds
        all properties needed for plotting, all the others
        are handled by other classes
    """
    def __init__(self, title: str, th: TH1, lineColor: int = ROOT.kBlack,
                 fillColor: Optional[int] = None, option: str = "histe") -> None:
        """
        Arguments:
            th (``TH1``): ROOT histogram
            lineColor (``int``): color of the histogram line
            fillColor (``int/None``): color of the histogram fill,
                can be None
        """
        self.th = th
        self.title = title
        self.lineColor = lineColor
        self.fillColor = fillColor
        self.option = option

        th.SetTitle(title)
        th.SetLineColor(lineColor)
        if fillColor is not None:
            th.SetFillColor(fillColor)

    def draw(self, suffix: str = "", option: Optional[str] = None) -> None:
        """ TH1.Draw wrapper,

        Arguments
            option (``str``): if want to overwrite self.option
            suffix (``str``): suffix afteert option, mainly for "same"
        """
        if option is None:
            option = self.option
        self.th.Draw(option+suffix)

    def divide(self, otherHisto: "histo", option: str = "") -> bool:
        """ Add ROOT::TH1::Divide to histo level

        Arguments:
            otherHist (``histo``): histogram to divide by
            option (``str``): if B then binomial errors """
        return self.th.Divide(self.th, otherHisto.th, 1, 1, option)

    def divide_ratio(self, otherHisto: "histo"):
        """ For ratio, we do not to take into account
        errors of otherHisto!

        Uses function from thHelper

        Arguments:
            otherHisto (``histo``): histo to be divided by
        """
        thHelper.divide_ratio(self.th, otherHisto.th)

    def get_ratio(self, otherHisto: "histo", suffix: str = "ratio") -> TH1:
        """ Returns clone of the saved histogram and divides by otherHist.
        All the other properties are copied.

        Arguments:
            otherHist (``histo``): histogram to divide by
        """
        th = self.th.Clone(suffix)
        thHelper.divide_ratio(th, otherHisto.th)
        return histo(self.title+"_"+suffix, th, lineColor=self.lineColor,
                     fillColor=self.fillColor, option=self.option)
