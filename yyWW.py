from plotter import collection, dataset
from plotter import xsReader
from plotter import sumOfWeightHelper, atlas
from typing import Dict, List
import glob

import logging
logging.basicConfig(
    level=logging.INFO, format="%(levelname)s (%(name)s): %(message)s"
)
log = logging.getLogger(__name__)


class yyWW_samples:
    def __init__(self):
        collections: Dict[str, collection] = {}
        datasets: Dict[str, dataset] = {}

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

        collections["dataDraw"] = collection("DataDraw")
        collections["dataDraw"].add_datasets(["dataDrawzmumu15", "dataDrawzmumu16", "dataDrawzmumu17", "dataDrawzmumu18"])

        collections["dataPick"] = collection("DataPick")
        collections["dataPick"].add_datasets(["data15", "data16", "data17", "data18"])

        collections["DY_PP8_filt2"] = collection("Drell-Yan PP8", sow)
        collections["yymumu_excl_HW7"] = collection("yy#mu#mu excl. HW7", sow)
        collections["yymumu_SD_LPAIR"] = collection("yy#mu#mu SD LPAIR", sow)
        for mc16x in atlas.get_lumi().keys():
            collections["DY_PP8_filt2"].add_datasets(["600702."+mc16x, "600703."+mc16x, "600704."+mc16x])
            collections["yymumu_excl_HW7"].add_datasets(["363753."+mc16x, "363754."+mc16x, "363755."+mc16x, "363756."+mc16x])
            collections["yymumu_SD_LPAIR"].add_datasets(["363699."+mc16x, "363700."+mc16x])
            # collections["yymumu_SD_LPAIR"].add_datasets(["363698."+mc16x, "363699."+mc16x, "363700."+mc16x])

        self.collections = collections
        self.datasets = datasets
