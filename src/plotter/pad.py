from plotter import histo
from plotter import loader
from plotter import styler
import ROOT
from ROOT import TPad, TCanvas
from typing import List, Dict, Optional

import logging
log = logging.getLogger(__name__)


class canvas:
    """ Wrapper around TCanvas

    Automates few thinks which need to be done every time
    (e.g. drawin pads)"""
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


class pad:
    """ Wrapper around TPad
    """
    def __init__(self, name: str, xl: int = 0, xh: int = 1,
                 yl: int = 0, yh: int = 1, configPath = "configs/pad.json") -> None:
        """
        Arguments:
            name (``str``): name of the pad
            xl (``int``): fraction of x-axis of the canvas the pad starts at
            xh (``int``): fraction of x-axis of the canvas the pad ends at
            yl (``int``): fraction of y-axis of the canvas the pad starts at
            yh (``int``): fraction of y-axis of the canvas the pad ends at
            config (``str``): path to config of pad
        """
        self.tpad = TPad(name, name, xl, yl, xh, yh)
        self.name = name

        self.config = loader.load_config(configPath)
        # set default margins
        self.margins()

        # if margins in config, update:
        if "margins" in self.config:
            styler.pad_margin(self, self.config["margins"])

        self.histos: List[histo] = []
        self.xTitle = ""
        self.yTitle = ""

        self.yMin = 0.
        self.yMax = 1.
        # the logarithm of the y-axis is saved, as it affects the y-range
        self.isLogY = False
        # if user specifies y-range, we do not want to derive it automatically
        self.customYrange = False

        self.basis: Optional[histo] = None

    def margins(self, up: float = 0.04, down: float = 0.25,
                left: float = 0.18, right: float = 0.05) -> None:
        """ Set margins of the pad with default values,
        which work for the atlas style.

        Arguments:
            up (``float``): upper margin
            down (``float``): bottom margin
            left (``float``): left margin
            right (``float``): right margin
        """
        self.tpad.SetTopMargin(up)
        self.tpad.SetBottomMargin(down)
        self.tpad.SetLeftMargin(left)
        self.tpad.SetRightMargin(right)

    def logx(self, doLog: bool = True) -> None:
        """ Sets the X-axis to log/lin

        Arguments:
            doLog (``bool``): if true, set logarithmic
        """
        self.tpad.SetLogx(doLog)

    def logy(self, doLog: bool = True) -> None:
        """ Sets the Y-axis to log/lin

        Arguments:
            doLog (``bool``): if true, set logarithmic
        """
        self.tpad.SetLogy(doLog)
        self.isLogY = doLog

    def add_histos(self, histos: List[histo]) -> None:
        """ Adds list of histograms to the pad

        Arguments:
            histos (``List[hist]``): list of histos to be added
        """
        for h in histos:
            self.add_histo(h)

    def add_histo(self, h: histo) -> None:
        """ Adds histogram to the pad and update min/max y value

        Arguments:
            h (``histo``): added histogram
        """

        # if custom range defined, skip the automatic derivation
        if not self.customYrange:
            if self.histos == []:
                self.yMin = h.th.GetMinimum(0)
                self.yMax = h.th.GetMaximum()
            else:
                if self.yMin > h.th.GetMinimum(0):
                    self.yMin = h.th.GetMinimum(0)
                if self.yMax < h.th.GetMaximum():
                    self.yMin = h.th.GetMaximum()
        self.histos.append(h)

    def plot_histos(self) -> None:
        """ Plots histograms, including creation of basis,
            which handles some properties of the plot,
            ike the axis title or range
        """

        if len(self.histos) == 0:
            log.error("Pad does not contain any histograms!")
            # not sure that IndexError is the best one
            raise IndexError

        self.tpad.cd()
        # now lets clone the first histogram to manipulate axis and such
        # this is done because we do not want to modify any externally provided
        # histograms
        # TODO: add histo.clone??
        self.basis = histo("", self.histos[0].th.Clone("basis"),
                           lineColor=ROOT.kWhite, option="hist")
        self.basis.th.Reset()
        self._set_basis_axis_title()
        if not self.customYrange:
            self._set_basis_yrange(margin=1.3)
        else:
            self._set_basis_yrange(margin=1)

        # if margins in config, update:
        if "basis" in self.config:
            styler.pad_basis(self, self.config["basis"])
        # TODO: style config!!!
        # self.basis.th.GetXaxis().SetTitleOffset(2.2)
        # self.basis.th.GetYaxis().SetTitleOffset(2.2)
        # self.basis.th.GetXaxis().SetTitleSize(30)
        # self.basis.th.GetYaxis().SetTitleSize(30)
        # self.basis.th.GetXaxis().SetTitleFont(43)
        # self.basis.th.GetYaxis().SetTitleFont(43)
        # self.basis.th.GetXaxis().SetLabelSize(30)
        # self.basis.th.GetYaxis().SetLabelSize(30)
        # self.basis.th.GetXaxis().SetLabelFont(43)
        # self.basis.th.GetYaxis().SetLabelFont(43)
        # self.basis.th.SetNdivisions(505, "Y")

        self.basis.draw()

        for h in self.histos:
            h.draw(suffix="same")

    def _set_basis_axis_title(self) -> None:
        """ Sets titles of the axis through the basis histogram"""
        if self.basis is None:
            log.error("Called basis function but no basis yet!")
            raise RuntimeError

        self.basis.th.GetXaxis().SetTitle(self.xTitle)
        self.basis.th.GetYaxis().SetTitle(self.yTitle)

    def set_title(self, xTitle: str = "", yTitle: str = "") -> None:
        """ Saves the axis titles, applies to the basis if already exists

        Arguments:
            xTitle (``str``): title of the x-axis
            yTitle (``str``): title of the y-axis
        """
        self.xTitle = xTitle
        self.yTitle = yTitle

        if self.basis is not None:
            self._set_basis_axis_title()

    def _set_basis_yrange(self, margin=1) -> None:
        """ Sets rangeof the y-axis through the basis histogram"""
        if self.basis is None:
            log.error("Called basis function but no basis yet!")
            raise RuntimeError

        # for the maximum you alway want to have some margin
        # TODO: margin as class variable?
        
        if not self.isLogY:
            self.basis.th.GetYaxis().SetRangeUser(self.yMin, self.yMax*margin)
        # for log it is little bit more complicated
        # but this usually ends up looking nice
        else:
            fPlot = 1./margin  # plot takes 1/margin of the plot vertically
            fBot = 0.02  # little bit space on the bottom
            fLeg = 1-fPlot-0.02  # legend takes most of therest
            yMinLog = pow(self.yMin, (fPlot+fBot)/fPlot)/pow(self.yMax, fBot/fPlot)
            yMaxLog = pow(self.yMax, (1.-fBot)/fPlot)/pow(self.yMin, fLeg/fPlot)
            self.basis.th.GetYaxis().SetRangeUser(yMinLog, yMaxLog)

    def set_yrange(self, yMin: float = 0, yMax: float = 1) -> None:
        """ Saves the y-axis range, applies to the basis if already exists

        Arguments:
            yMin (``float``): lower range of the y-axis
            yMax (``float``): upper range of the y-axis
        """
        self.yMin = yMin
        self.yMax = yMax
        self.customYrange = True

        if self.basis is not None:
            self._set_basis_yrange()
