from .canvas import canvas
from .pad import pad
from .histo import histo
from . import loader
from .legend import legend

import ROOT
from ROOT import TGraphAsymmErrors
from typing import List, Optional
import copy

import logging
import ctypes

log = logging.getLogger(__name__)


class simple:
    def __init__(
        self,
        plotName: str = "",
        xTitle: Optional[str] = None,
        yTitle: Optional[str] = "Events",
        isTH1: bool = True,
        autoY=True,
    ):
        self.canvas = canvas(plotName)

        self.mainPad = pad(
            "main",
            configPath=loader.path() + "configs/pad.json",
            isTH1=isTH1,
            autoY=autoY,
        )
        self.canvas.add_pad(self.mainPad)
        self.mainPad.set_title(xTitle, yTitle)

    def add_and_plot(self, hs: List[histo]):
        if len(hs) == 0:
            log.error("List of MC histograms is empty")
            raise RuntimeError

        self.hs = hs

        self.mainPad.add_histos(self.hs)
        self.mainPad.plot_histos()

        self.canvas.tcan.cd()
        self.leg = legend()
        self.leg.add_histos(self.hs)
        self.leg.create_and_draw()

    def logx(self, doLog=True):
        self.mainPad.logx(doLog)

    def set_xrange(self, min, max):
        self.mainPad.set_xrange(min, max)

    def set_yrange(self, min, max):
        self.mainPad.set_yrange(min, max)

    def save(self, plotName: str, verbose=False):
        self.canvas.save(plotName, verbose)


class dataMC:
    def __init__(
        self,
        plotName: str = "",
        xTitle: Optional[str] = None,
        yTitle: Optional[str] = "Events",
        ratioTitle: str = "Ratio",
        fraction: float = 0.3,
        ratio_limits=(0.701, 1.299),
        nonEmpty=True,
    ):
        self.custom_xrange = False
        self.nonEmpty = nonEmpty

        self.canvas = canvas(plotName)

        self.mainPad = pad(
            "main", yl=fraction, configPath=loader.path() + "configs/pad_dm.json"
        )
        self.canvas.add_pad(self.mainPad)
        self.mainPad.set_title(xTitle, yTitle)
        self.mainPad.margins(down=0)

        self.ratioPad = pad(
            "ratio", yh=fraction, configPath=loader.path() + "configs/pad_dm.json"
        )
        self.canvas.add_pad(self.ratioPad)
        if ratio_limits is not None:
            low, high = ratio_limits
            self.ratioPad.set_yrange(low, high)

        self.ratioPad.margins(up=0)
        self.ratioPad.set_title(xTitle, ratioTitle)

    def add_and_plot(
        self, hData: histo, _hMCs: List[histo], _hShapes: List[histo] = []
    ):

        if len(_hMCs) == 0:
            log.error("List of MC histograms is empty")
            raise RuntimeError

        self.hData = hData

        # stack the MC
        self.hMCs: List[histo] = []
        for _hMC in _hMCs:
            hMC = _hMC.clone("stack")
            hMC.linewidth = 0  # do not show stat of individual stack components
            for hOther in self.hMCs:
                hOther.th.Add(hMC.th)
            self.hMCs.append(hMC)

        # MC stat uncertainty
        if len(self.hMCs):
            hMC_stat = self.hMCs[0].clone("Stack MC stat")
            hMC_stat.color = ROOT.kGray + 1
            hMC_stat.linecolor = "blue"
            hMC_stat.linewidth = 3
            hMC_stat.inlegend = False

            # todo custom config
            cfgErr = loader.load_config(loader.path() + "configs/err.json")
            hMC_stat.style_histo(cfgErr)
            hMC_stat.drawoption = "e2"

            hMC_stat_line = hMC_stat.clone("Stack MC stat line")
            hMC_stat_line.drawoption = "hist"
            hMC_stat_line.fillstyle = "hollow"
            hMC_stat_line.linecolor = "darkblue"
            hMC_stat_line.linewidth = 2
            hMC_stat_line.inlegend = False

            self.hMCs.append(hMC_stat)
            self.hMCs.append(hMC_stat_line)

        self.mainPad.add_histos(self.hMCs)

        self.hShapes = _hShapes
        if self.hShapes != []:
            self.mainPad.add_histos(self.hShapes)
        self.mainPad.add_histo(hData)
        self.mainPad.plot_histos()

        if self.hShapes != []:
            self.hErr = self.hData.get_ratio(self.hData)
            self.hErr.title = "Data Stat. Unc."
            self.hRatio = self.hMCs[0].get_ratio(self.hData, fillToLine=True)
            self.hRatioShapes = [h.get_ratio(self.hData) for h in self.hShapes]
            self.ratioPad.add_histos([self.hErr, self.hRatio])
            self.ratioPad.add_histos(self.hRatioShapes)
        else:
            self.hErr = self.hMCs[0].get_ratio(self.hMCs[0])
            self.hErr.title = "MC Stat. Unc."
            self.hRatio = hData.get_ratio(self.hMCs[0], fillToLine=False)
            self.ratioPad.add_histos([self.hErr, self.hRatio])

        self.hErr.color = ROOT.kGray + 1
        # TODO: custom config
        cfgErr = loader.load_config(loader.path() + "configs/err.json")
        self.hErr.style_histo(cfgErr)

        self.ratioPad.plot_histos()

        self.update_ranges()

    def update_ranges(self):

        if self.nonEmpty and not self.custom_xrange:
            (xmin, xmax) = self._xrange_emptysupressed()
            self.mainPad.set_xrange(xmin, xmax)
            self.ratioPad.set_xrange(xmin, xmax)

        self.mainPad.update_range()
        self.ratioPad.update_range()

    def _xrange_emptysupressed(self):
        """Determine x range containing nonzero"""  # TODO REVIEW
        xMin = self.hData.th.GetBinLowEdge(1)
        xMax = self.hData.th.GetBinLowEdge(self.hData.th.GetNbinsX() + 1)
        prevCont = False
        minDone = False
        maxDone = False
        for i in range(self.hData.th.GetNbinsX()):
            iBin = i + 1
            if (
                self.hData.th.GetBinContent(iBin) != 0
                or self.hMCs[0].th.GetBinContent(iBin) != 0
            ):
                minDone = True
                prevCont = True
                continue

            if not minDone:
                xMin = self.hData.th.GetBinLowEdge(iBin + 1)
            if prevCont:
                xMax = self.hData.th.GetBinLowEdge(iBin)
                maxDone = True
            prevCont = False
        if not maxDone:
            xMax = self.hData.th.GetBinLowEdge(self.hData.th.GetNbinsX() + 1)

        return (xMin, xMax)

    def set_xrange(self, min, max):
        self.custom_xrange = True
        self.mainPad.set_xrange(min, max)
        self.ratioPad.set_xrange(min, max)

    def logx(self, doLog=True):
        self.mainPad.logx(doLog)
        self.ratioPad.logx(doLog)

    def save(self, plotName: str, verbose=False):
        self.canvas.tcan.cd()
        self.leg = legend()
        self.leg.add_histo(self.hData)
        self.leg.add_histos(self.hMCs)
        self.leg.add_histo(self.hErr)
        if self.hShapes != []:
            self.leg.add_histos(self.hShapes)
        self.leg.create_and_draw()
        if verbose:
            print(plotName)
        self.canvas.save(plotName)


class fraction:
    """E.g. to display fraction of background/signal"""

    def __init__(
        self,
        plotName: str = "",
        xTitle: Optional[str] = None,
        yTitle: Optional[str] = "Fraction",
    ):
        self.canvas = canvas(plotName)

        self.mainPad = pad("fraction")
        self.canvas.add_pad(self.mainPad)
        self.mainPad.set_title(xTitle, yTitle)

    def add_and_plot(self, hToAll: List[histo], hToFrac: List[histo]):
        """Combine all from hToAll, display fraction of all in hToFrac."""

        if len(hToAll) == 0 or len(hToFrac) == 0:
            log.error("List of MC histograms is empty")
            raise RuntimeError

        # stack the MC
        self.hFrac: List[histo] = []
        self.hAll: histo
        first = True
        for h in hToAll:
            if first:
                self.hAll = copy.copy(h)
                self.hAll.th = h.th.Clone("stack")
                first = False
            else:
                self.hAll.th.Add(h.th)

        for h in hToFrac:
            hF = h.clone("stack")
            hF.th.Divide(self.hAll.th)
            self.hFrac.append(hF)

        self.mainPad.add_histos(self.hFrac)
        self.mainPad.plot_histos()

        self.canvas.tcan.cd()
        self.leg = legend()
        self.leg.add_histos(self.hFrac)
        self.leg.create_and_draw()

    def set_xrange(self, min, max):
        self.mainPad.set_xrange(min, max)

    def logx(self, doLog=True):
        self.mainPad.logx(doLog)

    def save(self, plotName: str, verbose=False):
        self.canvas.save(plotName, verbose)


class Comparison:
    def __init__(
        self,
        plotName: str = "",
        xTitle: Optional[str] = "",
        yTitle: Optional[str] = "Events",
        ratioTitle: str = "Ratio",
        fraction: float = 0.3,
        show_nonEmptyOnly: bool = True,
    ):
        self.canvas = canvas(plotName)

        self.mainPad = pad(
            "main", yl=fraction, configPath=loader.path() + "configs/pad_dm.json"
        )
        self.canvas.add_pad(self.mainPad)
        self.mainPad.set_title(xTitle, yTitle)
        self.mainPad.margins(down=0)

        self.ratioPad = pad(
            "ratio", yh=fraction, configPath=loader.path() + "configs/pad_dm.json"
        )
        self.canvas.add_pad(self.ratioPad)
        self.ratioPad.set_yrange(0.701, 1.299)
        self.ratioPad.margins(up=0)
        self.ratioPad.set_title(xTitle, ratioTitle)

        self.nonEmpty = show_nonEmptyOnly

    def add_and_plot(self, histos: List[histo]):
        if len(histos) == 0:
            log.error("List of MC histograms is empty")
            raise RuntimeError

        # stack the MC
        self.histos = histos

        # get xmin, xmin, empty bins are cut away
        if self.nonEmpty:
            xMin = histos[0].th.GetBinLowEdge(1)
            xMax = histos[0].th.GetBinLowEdge(histos[0].th.GetNbinsX() + 1)
            prevCont = False
            minDone = False
            maxDone = False
            for i in range(histos[0].th.GetNbinsX()):
                iBin = i + 1
                if (
                    histos[0].th.GetBinContent(iBin) == 0
                    and self.histos[0].th.GetBinContent(iBin) == 0
                ):
                    if not minDone:
                        xMin = histos[0].th.GetBinLowEdge(iBin + 1)
                    if prevCont:
                        xMax = histos[0].th.GetBinLowEdge(iBin)
                        maxDone = True
                    prevCont = False
                else:
                    minDone = True
                    prevCont = True
            if not maxDone:
                xMax = histos[0].th.GetBinLowEdge(self.histos[0].th.GetNbinsX() + 1)
            self.mainPad.set_xrange(xMin, xMax)
            self.ratioPad.set_xrange(xMin, xMax)

        self.mainPad.add_histos(self.histos)
        self.mainPad.plot_histos()

        self.hErr = self.histos[0].get_ratio(self.histos[0])
        self.hErr.color = ROOT.kGray + 1
        # TODO: custom config
        cfgErr = loader.load_config(loader.path() + "configs/err.json")
        self.hErr.style_histo(cfgErr)

        self.hRatios = []
        first = True
        for h in self.histos:
            if first:
                first = False
                continue
            hR = h.get_ratio(self.histos[0], fillToLine=False)
            self.hRatios.append(hR)
        self.ratioPad.add_histos([self.hErr] + self.hRatios)
        self.ratioPad.plot_histos()

        self.canvas.tcan.cd()
        self.leg = legend()
        self.leg.add_histos(self.histos)
        self.leg.create_and_draw()

    def set_xrange(self, min, max):
        self.mainPad.set_xrange(min, max)
        self.ratioPad.set_xrange(min, max)

    def logx(self, doLog=True):
        self.mainPad.logx(doLog)
        self.ratioPad.logx(doLog)

    def save(self, plotName: str, verbose=False):
        self.canvas.save(plotName, verbose)

class Comparison_systematics:
    def __init__(
        self,
        plotName: str = "",
        xTitle: Optional[str] = "",
        yTitle: Optional[str] = "Events",
        ratioTitle: str = "Ratio",
        fraction: float = 0.3,
        show_nonEmptyOnly: bool = True,
    ):
        self.canvas = canvas(plotName)

        self.mainPad = pad(
            "main", yl=fraction, configPath=loader.path() + "configs/pad_dm.json"
        )
        self.canvas.add_pad(self.mainPad)
        self.mainPad.set_title(xTitle, yTitle)
        self.mainPad.margins(down=0)

        self.ratioPad = pad(
            "ratio", yh=fraction, configPath=loader.path() + "configs/pad_dm.json"
        )
        self.canvas.add_pad(self.ratioPad)
        self.ratioPad.set_yrange(0.701, 1.299)
        self.ratioPad.margins(up=0)
        self.ratioPad.set_title(xTitle, ratioTitle)

        self.nonEmpty = show_nonEmptyOnly

    def add_and_plot(self, histos: List[histo], bands: List[TGraphAsymmErrors]):
        if len(histos) == 0:
            log.error("List of MC histograms is empty")
            raise RuntimeError

        # stack the MC
        self.histos = histos

        # get xmin, xmin, empty bins are cut away
        if self.nonEmpty:
            xMin = histos[0].th.GetBinLowEdge(1)
            xMax = histos[0].th.GetBinLowEdge(histos[0].th.GetNbinsX() + 1)
            prevCont = False
            minDone = False
            maxDone = False
            for i in range(histos[0].th.GetNbinsX()):
                iBin = i + 1
                if (
                    histos[0].th.GetBinContent(iBin) == 0
                    and self.histos[0].th.GetBinContent(iBin) == 0
                ):
                    if not minDone:
                        xMin = histos[0].th.GetBinLowEdge(iBin + 1)
                    if prevCont:
                        xMax = histos[0].th.GetBinLowEdge(iBin)
                        maxDone = True
                    prevCont = False
                else:
                    minDone = True
                    prevCont = True
            if not maxDone:
                xMax = histos[0].th.GetBinLowEdge(self.histos[0].th.GetNbinsX() + 1)
            self.mainPad.set_xrange(xMin, xMax)
            self.ratioPad.set_xrange(xMin, xMax)

        self.mainPad.add_histos(self.histos)
        self.mainPad.plot_histos()

        #REBECA: ADDED
        self.canvas.tcan.cd()  # Go to the canvas
        self.mainPad.tpad.cd()
        
        if bands != []:
            bands[1].Draw("E2 SAME")
            bands[0].SetFillColor(ROOT.kCyan-10)    
            bands[0].SetFillStyle(1001)
            bands[0].SetLineWidth(0)
            bands[0].Draw("2 SAME")  

        histos[0].th.Draw("HIST SAME")
        histos[1].th.Draw("P SAME")

        self.hErr = self.histos[0].get_ratio(self.histos[0])
        self.hErr.color = ROOT.kGray + 1
        # TODO: custom config
        cfgErr = loader.load_config(loader.path() + "configs/err.json")
        self.hErr.style_histo(cfgErr)

        self.hRatios = []
        #REBECA: RATIOS, dont need to get ratio for everything
        first = True
        for h in self.histos:
            if first:
                first = False
                continue
        #REBECA: change bands != for a variable to reduce repetitivness
            hR = h.get_ratio(histos[0], fillToLine=False)
            self.hRatios.append(hR)

        self.ratioPad.add_histos([self.hErr] + self.hRatios)
        self.ratioPad.plot_histos()

        ratio_1 = histos[0].th.Clone()

        #REBECA: Clean up
        if bands != []:
            self.canvas.tcan.cd()  # Go to the canvas
            self.ratioPad.tpad.cd()
            ratio_1 = self.get_ratio_band(bands[1], histos[0])
            ratio_1.Draw("HIST SAME")
            self.canvas.tcan.Update()
            print("Ratios plotted")


            print("ratio_1:", ratio_1)
            print("denominator:", histos[0].th)
            print("ratio_1 class:", type(ratio_1))
            print("ratio_1 entries:", ratio_1.GetEntries())

            c = ROOT.TCanvas("c", "", 800, 600)
            ratio_1.Draw("HIST")
            c.Update() 
            c.Print("debug_output.pdf")

        self.canvas.tcan.cd()
        self.leg = legend()
        self.leg.add_histos(self.histos)
        self.leg.create_and_draw()
        if bands != []:
            self.leg.tlegend.AddEntry(bands[0], 'Systematic Uncertainty', "f")
            self.leg.tlegend.AddEntry(bands[1], 'Statistical Uncertainty', "f")

    def set_xrange(self, min, max):
        self.mainPad.set_xrange(min, max)
        self.ratioPad.set_xrange(min, max)

    def logx(self, doLog=True):
        self.mainPad.logx(doLog)
        self.ratioPad.logx(doLog)

    def save(self, plotName: str, verbose=False):
        self.canvas.save(plotName, verbose)

    def get_ratio_band(self, numerator, denominator, suffix="_errRatio"):
        #if isinstance(numerator, ROOT.TH1):
        h_ratio = denominator.th.Clone()

        if numerator.GetNbinsX() != denominator.th.GetNbinsX():
            log.error("Incompatible histograms!")
            raise ValueError

        for i in range(1, denominator.th.GetNbinsX()+1):
            if denominator.th.GetBinContent(i) != 0:
                temp = numerator.GetBinContent(i)/denominator.th.GetBinContent(i)
                h_ratio.SetBinContent(i, 1.1)
                print("Temp: " + str(temp))
                print("Bin:  " + str(h_ratio.GetBinContent(i)))
                print("x: " + str(h_ratio.GetBinCenter(i)))
                print("x: " + str(denominator.th.GetBinCenter(i)))

        h_ratio.SetFillColor(ROOT.kCyan)
        h_ratio.SetFillStyle(0)
        h_ratio.SetLineColor(ROOT.kCyan)
        h_ratio.SetMarkerSize(0)

        return h_ratio