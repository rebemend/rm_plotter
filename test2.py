from plotter import histo, atlas, presets
from plotter import normalizationHelper
import ROOT
from typing import List
from yyWW import yyWW_samples

import logging
logging.basicConfig(
    level=logging.INFO, format="%(levelname)s (%(name)s): %(message)s"
)
log = logging.getLogger(__name__)

atlas.SetAtlasStyle()

yyWW = yyWW_samples()


def plot_hist(histoName: str, plotName: str, axisName: str, rebin: int = 1):

    log.info(f"Working on histogram {histoName}")
    hD: histo
    if "MassZ" in histoName:
        hD = histo("Data DRAW", yyWW.collections["dataDraw"].get_th(histoName), configPath="configs/data.json")
    else:
        hD = histo("Data Pick", yyWW.collections["dataPick"].get_th(histoName), configPath="configs/data.json")
    hD.th.Rebin(rebin)

    mcs = {
        "DY_PP8_filt2": ROOT.kBlue,
        "yymumu_SD_LPAIR": ROOT.kRed,
        "yymumu_excl_HW7": ROOT.kOrange
    }
    hMCs: List[histo] = []
    for mc, col in mcs.items():
        norm = normalizationHelper(normByLumi=True, normBySoW=True, normByXS=True)
        h = histo(yyWW.collections[mc].title,
                  yyWW.collections[mc].get_th(histoName, norm=norm),
                  fillColor=col, configPath="configs/mc.json")
        h.th.Rebin(rebin)
        hMCs.append(h)

    dm = presets.dataMC(plotName, xTitle=axisName)
    # p.logx()
    dm.ratioPad.set_yrange(0.701, 1.199)
    dm.add_and_plot(hD, hMCs)

    dm.canvas.tcan.cd()
    atlas.ATLASLabel(0.22, 0.9, "Internal")
    dm.canvas.add_text("test", 0.22, 0.84)

    dm.save("test/"+plotName+".png")
    dm.mainPad.logy()
    dm.save("test/"+plotName+"_log.png")


def main():
    yyWW_samples()
    histoNameBase = "nominal/mumuOS/"
    cuts = ["EWW/MassZ_Ntrk10/", "EWW/Excl/", "EWW/ZMassVetoExclComb/"]
    for cut in cuts:
        histoName = histoNameBase + cut
        plot_hist(histoName+"ll/hDiLeptonPt", "Out/"+cut+"ptll", "p_{T}^{ll}", rebin=5)
        plot_hist(histoName+"ll/hDiLeptonLogAco", "Out/"+cut+"aco", "Acoplanarity")
        plot_hist(histoName+"NX/hNtrkPV", "Out/"+cut+"ntrkH", "n_{trk}^{high-pt}")
        plot_hist(histoName+"Trk/hNtrkComb_Ntrk10", "Out/"+cut+"ntrkC", "n_{trk}^{comb}")
        plot_hist(histoName+"ll/hDiLeptonMass", "Out/"+cut+"mll", "m_{ll}", rebin=10)
        plot_hist(histoName+"Trk/hNtrkComb_WCW_Ntrk10", "Out/"+cut+"ntrkC_WCW", "n_{trk}^{comb}")
        plot_hist(histoName+"Trk/hNtrkComb_WCWall_Ntrk10", "Out/"+cut+"ntrkC_WCWall", "n_{trk}^{comb}")


if __name__ == "__main__":
    main()
