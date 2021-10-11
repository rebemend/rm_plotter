from plotter import collection, dataset
from plotter import xsReader
from plotter import sumOfWeightHelper, atlas
from typing import Dict, List
import glob
import os

import logging
log = logging.getLogger(__name__)


class yyWW_samples:
    def __init__(self, dirName: str):

        if not os.path.exists(dirName):
            log.error("Invalid path provided:")
            log.error(f"{dirName}")

        collections: Dict[str, collection] = {}
        datasets: Dict[str, dataset] = {}

        self.collections = collections
        self.datasets = datasets

        for flName in glob.glob(dirName+"/yy2ww.data*.root"):
            dataName = flName.split("/")[-1].split(".")[1]
            if dataName in datasets.keys():
                log.warning(f"Data {dataName} already exists, keeping old!")
                log.debug(f"Old: {datasets[dataName].path}")
                log.debug(f"New: {flName}")
                continue
            datasets[dataName] = dataset(dataName, flName)
            collections[dataName] = collection(dataName)
            collections[dataName].add_dataset(datasets[dataName])

        sow = sumOfWeightHelper("nominal/sumOfWeight_nominal", 2)
        xs = xsReader()
        xs.add_files(["test/xsection/XS_dibtt_mc16.csv",
                      "test/xsection/XS_DY_mc16.csv",
                      "test/xsection/XS_filt_mc16.csv"])

        self.sow = sow
        self.xs = xs

        for mc16x, lumi in atlas.get_lumi().items():
            for flName in glob.glob(dirName+"/yy2ww.*"+mc16x+"*.root"):
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

        collections["dataDrawzmumu1516"] = collection("DataDraw1516")
        collections["dataDrawzmumu1516"].add_datasets(["dataDrawzmumu15", "dataDrawzmumu16"])

        collections["dataEvt1pick1516"] = collection("DataPick1516")
        collections["dataEvt1pick1516"].add_datasets(["dataEvt1pick15", "dataEvt1pick16"])

        collections["dataDrawzmumu"] = collection("DataDraw")
        collections["dataDrawzmumu"].add_datasets(["dataDrawzmumu15", "dataDrawzmumu16", "dataDrawzmumu17", "dataDrawzmumu18"])

        collections["dataEvt1pick"] = collection("DataPick")
        collections["dataEvt1pick"].add_datasets(["dataEvt1pick15", "dataEvt1pick16", "dataEvt1pick17", "dataEvt1pick18"])

        self.make_collection("DY_PP8_filt2", "Drell-Yan PP8", ["600702", "600703", "600704"])
        self.make_collection("yymumu_excl_HW7", "yy#mu#mu excl. HW7", ["363753", "363754", "363755", "363756"])
        self.make_collection("yymumu_SD_LPAIR", "yy#mu#mu SD LPAIR", ["363699", "363700"])

    def make_collection(self, name: str, title: str, dsids: List[str]):
        self.collections[name] = collection(title, self.sow)
        for mc16x in atlas.get_lumi().keys():
            self.collections[f"{name}.{mc16x}"] = collection(title, self.sow)
            for _dsid in dsids:
                dsid = _dsid+"."+mc16x
                if dsid not in self.datasets:
                    log.error(f"Trying to add dataset {dsid} to a collection,")
                    log.error("but the dataset does not exist! Probably missing files.")
                self.collections[name].add_dataset(self.datasets[dsid])
                self.collections[f"{name}.{mc16x}"].add_dataset(self.datasets[dsid])
