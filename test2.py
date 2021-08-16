from plotter import collection, dataset, sumOfWeightHelper
from plotter import histo, pad, canvas, atlas, legend
from plotter import loader, xsReader, normalizationHelper
import ROOT
import glob
from typing import Dict, List

import logging
logging.basicConfig(
    level=logging.INFO, format="%(levelname)s (%(name)s): %(message)s"
)
log = logging.getLogger(__name__)

atlas.SetAtlasStyle()

collections: Dict[str, collection] = {}
datasets: Dict[str, dataset] = {}


def yyWW_samples():

    for flName in glob.glob("../ExclWW_Offline/test3/Output_v46a/yy2ww.data*.root"):
        dataName = flName.split("/")[-1].split(".")[1]
        if dataName in datasets.keys():
            log.warning(f"Data {dataName} already exists, keeping old!")
            log.debug(f"Old: {datasets[dataName].path}")
            log.debug(f"New: {flName}")
            continue
        datasets[dataName] = dataset(dataName, flName)

    sow = sumOfWeightHelper("nominal/sumOfWeight_nominal", 2)
    xs = xsReader()
    xs.add_files(["test/xsection/XS_dibtt_mc16.csv",
                  "test/xsection/XS_DY_mc16.csv",
                  "test/xsection/XS_filt_mc16.csv"])

    for mc16x, lumi in atlas.get_lumi().items():
        for flName in glob.glob("../ExclWW_Offline/test3/Output_v46a/yy2ww.*"+mc16x+"*.root"):
            if "data" in flName or "Rdo" in flName:
                continue
            dsid = flName.split("/")[-1].split(".")[1]
            if dsid+"."+mc16x in datasets.keys() and "Unskim" not in flName:
                log.warning(f"dsid/mc16x combination {dsid}/{mc16x} already exists, keeping old!")
                log.debug(f"Old: {datasets[dsid+'.'+mc16x].path}")
                log.debug(f"New: {flName}")
                continue
            datasets[dsid+"."+mc16x] = dataset(dsid+"."+mc16x, flName, XS=xs.get_xs(dsid, oneIfMissing=True), lumi=lumi)

    def add_datasets(self, names: List[str]):
        for name in names:
            self.add_dataset(datasets[name])
    collection.add_datasets = add_datasets

    collections["dataDraw"] = collection("Data")
    collections["dataDraw"].add_datasets(["dataDrawzmumu15", "dataDrawzmumu16", "dataDrawzmumu17", "dataDrawzmumu18"])

    collections["DY_PP8_filt2"] = collection("Drell-Yan PP8", sow)
    collections["yymumu_excl_HW7"] = collection("yy#mu#mu excl. HW7", sow)
    collections["yymumu_SD_LPAIR"] = collection("yy#mu#mu SD LPAIR", sow)
    for mc16x in atlas.get_lumi().keys():
        collections["DY_PP8_filt2"].add_datasets(["600702."+mc16x, "600703."+mc16x, "600704."+mc16x])
        collections["yymumu_excl_HW7"].add_datasets(["363753."+mc16x, "363754."+mc16x, "363755."+mc16x, "363756."+mc16x])
        collections["yymumu_SD_LPAIR"].add_datasets(["363699."+mc16x, "363700."+mc16x])
        #collections["yymumu_SD_LPAIR"].add_datasets(["363698."+mc16x, "363699."+mc16x, "363700."+mc16x])



def plot_hist(histoName, plotName, axisName, rebin=1):

    hD = histo("Data", collections["dataDraw"].get_th(histoName), configPath="configs/data.json")
    hD.th.Rebin(rebin)

    mcs = {
        "DY_PP8_filt2": ROOT.kBlue,
        "yymumu_SD_LPAIR": ROOT.kRed,
        "yymumu_excl_HW7": ROOT.kOrange
    }
    hMCs: List[histo] = []
    for mc, col in mcs.items():
        norm = normalizationHelper(normByLumi=True, normBySoW=True, normByXS=True)
        h = histo(collections[mc].title,
                  collections[mc].get_th(histoName, norm=norm),
                  fillColor=col, configPath="configs/mc.json")
        h.th.Rebin(rebin)

        for hOther in hMCs:
            hOther.th.Add(h.th)
        hMCs.append(h)

    c = canvas(plotName)

    p = pad("main", yl=0.4)
    c.add_pad(p)
    p.add_histos(hMCs)
    p.add_histo(hD)
    p.set_title(axisName, "Events")
    # p.logx()
    p.logy()
    p.margins(down=0)
    p.plot_histos()

    hR = hMCs[0].get_ratio(hMCs[0])
    hR.set_fillColor(ROOT.kGray+1)
    hR.set_lineColor(ROOT.kGray+1)
    cfgErr = loader.load_config("configs/err.json")
    hR.style_histo(cfgErr)

    hR2 = hD.get_ratio(hMCs[0], fillToLine=True)

    pR2 = pad("ratio", yh=0.4)
    c.add_pad(pR2)
    pR2.set_yrange(0.501, 1.099)
    pR2.add_histos([hR, hR2])
    # pR2.logx()
    pR2.set_title(axisName, "Data/MC")
    pR2.margins(up=0)
    pR2.plot_histos()

    c.tcan.cd()
    atlas.ATLASLabel(0.22, 0.9, "Internal")

    leg = legend()
    leg.add_histo(hD)
    leg.add_histos(hMCs)
    leg.create_and_draw()

    c.save("test/"+plotName+".png")


def main():
    yyWW_samples()
    histoName = "nominal/mumuOS/EWW/MassZ_Ntrk10/"
    plot_hist(histoName+"ll/hDiLeptonPt", "yyww_ptll", "p_{T}^{ll}", rebin=5)
    plot_hist(histoName+"ll/hDiLeptonLogAco", "yyww_aco", "Acoplanarity")
    plot_hist(histoName+"NX/hNtrkPV", "yyww_ntrkH", "n_{trk}^{high-pt}")
    histoName = "nominal/mumuOS/EWW/Excl/"
    plot_hist(histoName+"ll/hDiLeptonPt", "yyww_ptll_excl", "p_{T}^{ll}", rebin=5)
    plot_hist(histoName+"ll/hDiLeptonLogAco", "yyww_aco_excl", "Acoplanarity")


if __name__ == "__main__":
    main()
