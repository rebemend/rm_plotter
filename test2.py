#!/usr/bin/env python3

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

version = "v46h/"
yyWW = yyWW_samples("../ExclWW_Offline/test3/Output_"+version)
sufD = ""
sufMC = ""



def plot_hist(histoName: str, plotName: str, axisName: str, rebin: int = 1, extraTitles: str = []):

    log.info(f"Working on histogram {histoName}")
    hD: histo
    if "MassZ" in histoName:
        hD = histo("Data DRAW "+sufD, yyWW.collections["dataDrawzmumu"+sufD].get_th(histoName), configPath="configs/data.json")
    else:
        hD = histo("Data Pick "+sufD, yyWW.collections["dataEvt1pick"+sufD].get_th(histoName), configPath="configs/data.json")
    hD.th.Rebin(rebin)

    mcs = {
        "DY_PP8_filt2"+sufMC: ROOT.kBlue,
        "yymumu_SD_LPAIR"+sufMC: ROOT.kRed,
        "yymumu_excl_HW7"+sufMC: ROOT.kOrange,
    }
    if "ZMassVetoExclComb" in histoName:
        mcs = {
            "yymumu_SD_LPAIR"+sufMC: ROOT.kRed,
            "yymumu_excl_HW7"+sufMC: ROOT.kOrange,
            "DY_PP8_filt2"+sufMC: ROOT.kBlue,
        }
    hMCs: List[histo] = []
    for mc, col in mcs.items():
        norm = normalizationHelper(normByLumi=True, normBySoW=True, normByXS=True)
        h = histo(yyWW.collections[mc].title,
                  yyWW.collections[mc].get_th(histoName, norm=norm),
                  fillColor=col, configPath="configs/mc.json")
        h.th.Rebin(rebin)
        if "yymumu" in mc:
            h.th.Scale(0.8)
        hMCs.append(h)

    dm = presets.dataMC(plotName, xTitle=axisName)
    # p.logx()
    dm.ratioPad.set_yrange(0.501, 1.199)
    dm.add_and_plot(hD, hMCs)
    if "DiLeptonPt" in histoName:
        dm.set_xrange(0, 50)

    dm.canvas.tcan.cd()
    atlas.ATLASLabel(0.22, 0.9, "Internal")
    if extraTitles != []:
        yPosition = 0.85
        for title in extraTitles:
            dm.canvas.add_text(title, 0.22, yPosition)
            yPosition -= 0.05

    dm.save("test/"+version+sufD+"/"+plotName+".png")
    dm.mainPad.logy()
    dm.save("test/"+version+sufD+"/"+plotName+"_log.png")


def DM():
    histoNameBase = "nominal/mumuOS/"
    cuts = {
        "EWW/MassZ_Ntrk10/":  ["#mu#mu, Z-peak", "n_{trk}^{H}<=10"],
        "EWW/MassZ_Ptll0_5_Ntrk10/":  ["#mu#mu, Z-peak", "n_{trk}^{H}<=10, p_{T}^{ll} [0,5]"],
        "EWW/MassZ_Ptll5_10_Ntrk10/":  ["#mu#mu, Z-peak", "n_{trk}^{H}<=10, p_{T}^{ll} [5,10]"],
        "EWW/MassZ_Ptll10_15_Ntrk10/":  ["#mu#mu, Z-peak", "n_{trk}^{H}<=10, p_{T}^{ll} [10,15]"],
        "EWW/MassZ_Ptll15_20_Ntrk10/":  ["#mu#mu, Z-peak", "n_{trk}^{H}<=10, p_{T}^{ll} [15,20]"],
        "EWW/MassZ_Ptll10_Ntrk10/":  ["#mu#mu, Z-peak", "n_{trk}^{H}<=10, p_{T}^{ll} [10,]"],
        "EWW/MassZ_Ptll20_Ntrk10/":  ["#mu#mu, Z-peak", "n_{trk}^{H}<=10, p_{T}^{ll} [20,]"],
        "EWW/ZMassVetoExclComb/": ["#mu#mu, Z-veto", "n_{trk}^{Comb}=0"],
        "EWW/MassZExclComb/": ["#mu#mu, Z-peak", "n_{trk}^{Comb}=0"],
        "EWW/MassZCR1_4Comb/": ["#mu#mu, Z-peak", "n_{trk}^{Comb}=1-4"],
        "EWW/MassZCR1_2Comb/": ["#mu#mu, Z-peak", "n_{trk}^{Comb}=1-2"],
        "EWW/MassZCR3_6Comb/": ["#mu#mu, Z-peak", "n_{trk}^{Comb}=3-6"],
        "EWW/MassZCR5_6Comb/": ["#mu#mu, Z-peak", "n_{trk}^{Comb}=5-6"],
    }
    for cut, extraTitles in cuts.items():
        rebin_mll = 5 if "MassZ" in cut else 100
        histoName = histoNameBase + cut
        plot_hist(histoName+"ll/hDiLeptonPt", "Out/"+cut+"ptll", "p_{T}^{ll}", rebin=5, extraTitles=extraTitles)
        plot_hist(histoName+"ll/hDiLeptonPt_Wcp", "Out/"+cut+"ptll_Wcp",
                  "p_{T}^{ll}", rebin=5, extraTitles=extraTitles+["no nch/pu weight"])
        plot_hist(histoName+"ll/hDiLeptonPt_WCW", "Out/"+cut+"ptll_WCW",
                  "p_{T}^{ll}", rebin=5, extraTitles=extraTitles+["comb. nch weight"])
        plot_hist(histoName+"ll/hDiLeptonPt_WCWall", "Out/"+cut+"ptll_WCWall",
                  "p_{T}^{ll}", rebin=5, extraTitles=extraTitles+["comb. nch+pu weight"])
        plot_hist(histoName+"ll/hDiLeptonLogAco", "Out/"+cut+"aco", "Acoplanarity", extraTitles=extraTitles, rebin=4)
        plot_hist(histoName+"ll/hDiLeptonLogAco_WCW", "Out/"+cut+"aco_WCW",
                  "Acoplanarity", extraTitles=extraTitles+["comb. nch weight"])
        plot_hist(histoName+"ll/hDiLeptonAco_Wcp", "Out/"+cut+"aco_Wcp",
                  "Acoplanarity", extraTitles=extraTitles+["no nch/pu weight"])
        plot_hist(histoName+"ll/hDiLeptonLogAco_WCWall", "Out/"+cut+"aco_WCWall",
                  "Acoplanarity", extraTitles=extraTitles+["comb. nch+pu weight"])
        plot_hist(histoName+"ll/hDiLeptonMass", "Out/"+cut+"mll", "m_{ll}", rebin=rebin_mll, extraTitles=extraTitles)
        plot_hist(histoName+"ll/hDiLeptonMass_Wcp", "Out/"+cut+"mll_Wcp",
                  "m_{ll}", rebin=rebin_mll, extraTitles=extraTitles+["no nch/pu weight"])
        plot_hist(histoName+"ll/hDiLeptonMass_WCW", "Out/"+cut+"mll_WCW",
                  "m_{ll}", rebin=rebin_mll, extraTitles=extraTitles+["comb. nch weight"])
        plot_hist(histoName+"ll/hDiLeptonMass_WCWall", "Out/"+cut+"mll_WCWall",
                  "m_{ll}", rebin=rebin_mll, extraTitles=extraTitles+["comb. nch+pu weight"])
        plot_hist(histoName+"NX/hNtrkPV", "Out/"+cut+"ntrkH", "n_{trk}^{high-pt}", extraTitles=extraTitles)
        plot_hist(histoName+"Trk/hNtrkComb_Ntrk10", "Out/"+cut+"ntrkC", "n_{trk}^{comb}", extraTitles=extraTitles)
        plot_hist(histoName+"Trk/hNtrkComb_WCW_Ntrk10", "Out/"+cut+"ntrkC_WCW", "n_{trk}^{comb}", extraTitles=extraTitles)
        plot_hist(histoName+"Trk/hNtrkComb_WCWall_Ntrk10",
                  "Out/"+cut+"ntrkC_WCWall", "n_{trk}^{comb}", extraTitles=extraTitles)


def main():
    global yyWW
    global version
    global sufD
    global sufMC
    yyWW = yyWW_samples("../noNtrkH_ExclWW_Offline/test3/Output_"+version)
    version = "v46h_opt1/"
    DM()
    sufD = "1516"
    sufMC = ".mc16a"
    DM()
    sufD = "17"
    sufMC = ".mc16d"
    DM()
    sufD = "18"
    sufMC = ".mc16e"
    DM()


if __name__ == "__main__":
    main()
