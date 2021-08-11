from typing import Dict, Any
from .pad import pad

import logging
log = logging.getLogger(__name__)

""" Class that applies style (in form of dicts

Currently on for:

pad
    * margins
    * basis
"""


def pad_margin(p: pad, style: Dict[str, Any]) -> None:

    log.info("Updating margin style")

    for opt, set in style.items():
        if "margin_up" in opt:
            p.tpad.SetTopMargin(set)
        elif "margin_down" in opt:
            p.tpad.SetTopMargin(set)
        elif "margin_left" in opt:
            p.tpad.SetLeftMargin(set)
        elif "margin_right" in opt:
            p.tpad.SetRightMargin(set)
        else:
            log.error(f"Unknown option {opt}")
            raise RuntimeError


def pad_basis(p: pad, style: Dict[str, Any]) -> None:

    if p.basis is None:
        log.error("Called pad style but no basis yet!")
        raise RuntimeError
    log.info("Updating basis style")

    for opt, set in style.items():
        if "x_" in opt:
            axis = p.basis.th.GetXaxis()
        else:
            axis = p.basis.th.GetYaxis()

        if "titleOffset" in style:
            axis.SetTitleOffset(set)
        elif "titleSize" in style:
            axis.SetTitleSize(set)
        elif "titleFont" in style:
            axis.SetTitleFont(set)
        elif "labelSize" in style:
            axis.SetLabelSize(set)
        elif "labelFont" in style:
            axis.SetLabelFont(set)
        elif opt is "n_div":
            if len(set) != 2:
                log.error("n_div option in wrong format, need two items")
            p.basis.th.SetNdivisions(set[0], set[1])
        else:
            log.error(f"Unknown option {opt}")
            raise RuntimeError
