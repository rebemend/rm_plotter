#!/usr/bin/env python3

from plotter import collection, dataset
from plotter import histo, atlas, presets
import ROOT

import logging
logging.basicConfig(
    level=logging.INFO, format="%(levelname)s (%(name)s): %(message)s"
)
log = logging.getLogger(__name__)

atlas.SetAtlasStyle()

cData = collection("Data")
cData.add_dataset(dataset("Data", "test/Nominal2/data.root"))

cBkg = collection("Bkg")
cBkg.add_dataset(dataset("Bkg", "test/Nominal2/background.root"))

cHis = collection("Hists")
cHis.add_dataset(dataset("Hists", "test/Nominal2/hists.root"))

def plot_dm(var: str = "ptll", varTitle: str = "p_{T}^{ll}", suffix: str = ""):

    hD = histo("Data", cData.get_th(var+"_data"+suffix), configPath="configs/data.json")

    hS = histo("Z", cHis.get_th(var+"_Z"+suffix), fillColor=ROOT.kBlue,
           configPath="configs/mc.json")

    hNF = histo("nonFid", cHis.get_th(var+"_nonFid"+suffix), fillColor=ROOT.kRed,
               configPath="configs/mc.json")

    hB = histo("Top+EW", cBkg.get_th(var+"_topew"+suffix), fillColor=ROOT.kGreen,
               configPath="configs/mc.json")

    dm = presets.dataMC("test"+suffix, xTitle=varTitle)
    dm.ratioPad.set_yrange(0.701, 1.199)
    dm.add_and_plot(hD, [hS, hNF, hB])
   # dm.mainPad.basis.th.GetXaxis().SetRangeUser(0, 100)
   # dm.ratioPad.basis.th.GetXaxis().SetRangeUser(0, 100)

    dm.canvas.tcan.cd()
    atlas.ATLASLabel(0.22, 0.9, "Internal")
    extraTitles = []
    if extraTitles != []:
        yPosition = 0.85
        for title in extraTitles:
            dm.canvas.add_text(title, 0.22, yPosition)
            yPosition -= 0.05
    plotName = var+"_"+suffix
    dm.save("AI/dm/"+plotName+".png")
    dm.mainPad.logy()
    dm.save("AI/dm/"+plotName+"_log.png")

def plot_frac(var: str = "ptll", varTitle: str = "p_{T}^{ll}", suffix: str = ""):

    hS = histo("Z", cHis.get_th(var+"_Z"+suffix), lineColor=ROOT.kBlue,
           configPath="configs/mc.json")

    hNF = histo("nonFid", cHis.get_th(var+"_nonFid"+suffix), lineColor=ROOT.kRed,
               configPath="configs/mc.json")

    hB = histo("Top+EW", cBkg.get_th(var+"_topew"+suffix), lineColor=ROOT.kGreen,
               configPath="configs/mc.json")

    frac = presets.fraction("frac"+suffix, xTitle=varTitle)
    frac.add_and_plot([hS, hNF, hB], [hNF, hB])
   # frac.mainPad.basis.th.GetXaxis().SetRangeUser(0, 100)

    frac.canvas.tcan.cd()
    atlas.ATLASLabel(0.22, 0.9, "Internal")
    extraTitles = []
    if extraTitles != []:
        yPosition = 0.85
        for title in extraTitles:
            frac.canvas.add_text(title, 0.22, yPosition)
            yPosition -= 0.05
    plotName = var+"_"+suffix
    frac.save("AI/frac/"+plotName+".png")
    frac.mainPad.logy()
    frac.save("AI/frac/"+plotName+"_log.png")

plot_dm()
plot_frac()
nPt = 25
nY = 8

for y in range(nY):
    suf = f"_M0_Y{y}"
    log.info(f"Working on {suf}")
    plot_dm(suffix=suf)
    plot_frac(suffix=suf)
    # for pt in range(nPt):
        # suf = f"_PT{pt}_M0_Y{y}"
        # log.info(f"Working on {suf}")
        # plot(suffix=suf)

for pt in range(nPt):
    suf = f"_PT{pt}_M0"
    log.info(f"Working on {suf}")
    plot_dm("yll", "y_{ll}", suffix=suf)
    plot_frac("yll", "y_{ll}", suffix=suf)