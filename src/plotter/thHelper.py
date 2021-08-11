from ROOT import TH1

import logging
log = logging.getLogger(__name__)

""" This file contains number of helper function for ROOT.TH1.

divide_ratio: divide function where error of the denominator
    is not takein into account.
"""


def divide_ratio(numTH: TH1, denTH: TH1):
    """ For ratio, we do not to take into account
    errors of the denominator!

    Arguments:
        numTH (``TH1``): histogram to be divided
            (numerator, modified)
        denTH (``TH1``): histogram to be divided by
            (denominator, unchanged)
    """

    # TODO: check compability of histogram!
    # for now only bin number
    if numTH.GetNbinsX() != denTH.GetNbinsX():
        log.error("Incompatible histograms!")
        raise ValueError

    for i in range(numTH.GetNbinsX()):
        iBin = i+1
        otherVal = denTH.GetBinContent(iBin)

        # to divide the value has to be non-zero:
        if otherVal:
            newVal = numTH.GetBinContent(iBin)/otherVal
            newErr = numTH.GetBinError(iBin)/otherVal
        # otherwise we set content to 0
        # TODO: issue a warning? debug?
        else:
            newVal = 0
            newErr = 0

        numTH.SetBinContent(iBin, newVal)
        numTH.SetBinError(iBin, newErr)
