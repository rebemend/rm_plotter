from ROOT import TLegend, TH1
from typing import List, Generic
from plotter import histo

import logging
log = logging.getLogger(__name__)

class legend:
    """ Wrapper around TLegend"""
    def __init__(self, xMin: float = 0.58, xMax: float = 0.96,
                 height: float = 0.04, yMax: float = 0.96, nColumns: int = 1) -> None:


        self.xMin = xMin
        self.xMax = xMax
        self.yMax = yMax
        self.height = height
        self.nCol = nColumns
    
        self.histos: List[histo] = []

    def add_histo(self, h: histo):
        self.histos.append(h)

    def add_histos(self, hs: List[histo]):
        self.histos.extend(hs)

    def create_and_draw(self):
        self.yMin = self.yMax - self.height*len(self.histos)/self.nCol
        self.tlegend = TLegend(self.xMin, self.yMin, self.xMax, self.yMax)

        for h in self.histos:
            if "p" in h.option:
                self.tlegend.AddEntry(h.th, h.title, "p")
            elif h.fillColor:
                self.tlegend.AddEntry(h.th, h.title, "f")
            else:
                self.tlegend.AddEntry(h.th, h.title, "l")

        # TODO: config?
        self.tlegend.SetBorderSize(0)
        self.tlegend.SetFillStyle(0)
        self.tlegend.SetNColumns(self.nCol)
        self.tlegend.Draw()
