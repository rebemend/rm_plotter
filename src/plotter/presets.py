from .canvas import canvas
from .pad import pad
from .histo import histo
from . import loader
from .legend import legend

import ROOT
from typing import List
import copy

import logging
logging.basicConfig(
    level=logging.INFO, format="%(levelname)s (%(name)s): %(message)s"
)
log = logging.getLogger(__name__)


class dataMC:
    def __init__(self, plotName: str = "", xTitle: str = "",
                 yTitle: str = "Events", ratioTitle: str = "Data/MC",
                 fraction: float = 0.4):
        self.canvas = canvas(plotName)

        self.mainPad = pad("main", yl=fraction)
        self.canvas.add_pad(self.mainPad)
        self.mainPad.set_title(xTitle, yTitle)
        self.mainPad.margins(down=0)

        self.ratioPad = pad("ratio", yh=fraction)
        self.canvas.add_pad(self.ratioPad)
        self.ratioPad.set_yrange(0.701, 1.299)
        self.ratioPad.margins(up=0)

    def add_and_plot(self, hData: histo, _hMCs: List[histo]):

        if len(_hMCs) == 0:
            log.error("List of MC histograms is empty")
            raise RuntimeError

        self.hData = hData
        # stack the MC
        self.hMCs: List[histo] = []
        for _hMC in _hMCs:
            # TODO: this should be mainly implemented in histo?
            # copy function which makes clone
            # or maybe deepcopy would work directly?
            hMC = copy.copy(_hMC)
            hMC.th = _hMC.th.Clone("stack")
            for hOther in self.hMCs:
                hOther.th.Add(hMC.th)
            self.hMCs.append(hMC)

        self.mainPad.add_histos(self.hMCs)
        self.mainPad.add_histo(hData)
        self.mainPad.plot_histos()

        self.hErr = self.hMCs[0].get_ratio(self.hMCs[0])
        self.hErr.set_fillColor(ROOT.kGray+1)
        self.hErr.set_lineColor(ROOT.kGray+1)
        # TODO: custom config
        cfgErr = loader.load_config("configs/err.json")
        self.hErr.style_histo(cfgErr)

        self.hRatio = hData.get_ratio(self.hMCs[0], fillToLine=True)
        self.ratioPad.add_histos([self.hErr, self.hRatio])
        self.ratioPad.plot_histos()

        self.canvas.tcan.cd()
        self.leg = legend()
        self.leg.add_histo(self.hData)
        self.leg.add_histos(self.hMCs)
        self.leg.create_and_draw()

    def save(self, plotName: str):
        self.canvas.save(plotName)
