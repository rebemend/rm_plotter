from typing import Optional, List
from ROOT import TH1
from .dataset import dataset, sumOfWeightHelper

import logging
log = logging.getLogger(__name__)


class normalizationHelper:
    """ Small helper class to define normalization.

    Type of normalization is something which will be quite often shared
    and repatadly used, so this is better than to pass
    multiple arguments.
    """

    def __init__(self, normToOne=False, normByLumi=False,
                 normByXS=False, normBySoW=False) -> None:
        """
        Arguments:
            normToOne (``bool``): if True: after all steps,
                normalize by Integral
            normbyLumi (``bool``): if True:luminosity of given collection
                is applied
            normbyXSX (``bool``): if True: cross-section of given dataset
                is applied
            normbySoW (``bool``): if True: each dataset is normalized
                by sum of weights
        """

        self.toOne = normToOne
        self.byLumi = normByLumi
        self.byXS = normByXS
        self.bySoW = normBySoW

        if normToOne and normByLumi:
            log.warning("Both norm. to one and norm. by lumi are active.")
            log.warning("Norm to one takes precedence, so lumi does not have effect!")


class collection:
    """ Manages collection of datasets
    and correct normalization of individual
    and combined histogram. """

    # TODO: need to rethink how sumOfWeightHelper is handled
    # both within collection and dataset
    def __init__(self, title: str, lumi: float,
                 sow: Optional[sumOfWeightHelper] = None) -> None:
        """
        Arguments:
            title (``str``): title of the sample,
                used e.g. in plotting
            lumi (``float``): used to normalize the whole collection
            sow (``sumOfWeightHelper```): defines where the sumOfWeight factor
                can be found, see the sumOfWeightHelper class in dataset.py
        """
        self.title = title
        self.lumi = lumi
        self.sow = sow

        # list of samples in the collection
        self.datasets: List[dataset] = []

    def add_dataset(self, ds: dataset) -> None:
        """ Adds dataset to the collection."""
        self.datasets.append(ds)

    def add_collection(self, coll: "collection") -> None:
        """ Adds all datasets from another collection."""
        self.datasets.extend(coll.datasets)

    def get_th(self, histoName: str, norm: Optional[normalizationHelper] = None, skipBad: bool = False) -> Optional[TH1]:
        """ Gets histograms from all datasets
        and correctly combines and normalizes them

        Arguments:
            histoName (``str``): name/path of histogram in given file
            norm (``normalizationHelper``): defines normalization of the
                collection, see normalizationHelper class for details
            skipBad (``bool``): if histogram or file does not exist,
                or is corrupted, it is skipped instead of raising error

        Returns:
            Combined histogram (``TH1``)
        """

        # if the user does not specify normalization helper
        # just use default (all flags false)
        if norm is None:
            norm = normalizationHelper()

        collTH: Optional[TH1] = None
        for ds in self.datasets:
            dsTH = ds.get_th(histoName, skipBad)
            if dsTH is None:
                if not skipBad:
                    log.error("Got bad histogram from the dataset.")
                    raise RuntimeError
                continue

            if norm.byXS:
                dsTH.Scale(ds.XS)
            if norm.bySoW:
                if self.sow is None:
                    log.error("Trying to normalize by sum of weights,\n but none was provided!.")
                    raise RuntimeError
                dsTH.Scale(ds.get_sumOfWeights(self.sow))

            if collTH:
                collTH.Add(dsTH)
            else:
                collTH = dsTH

        if collTH is None:
            return None

        if norm.toOne:
            collTH.Scale(1./collTH.Integral())
        elif norm.byLumi:
            collTH.Scale(self.lumi)

        return collTH
