from typing import Dict, Any
from plotter import pad, histo

import logging
log = logging.getLogger(__name__)


def pad_margin(p : pad, style: Dict[str, Any]):
    log.info("Updating margin style")
    if "margin_up" in style:
        p.tpad.SetTopMargin(style["margin_up"])
    if "margin_down" in style:
        p.tpad.SetTopMargin(style["margin_down"])
    if "margin_left" in style:
        p.tpad.SetLeftMargin(style["margin_left"])
    if "margin_right" in style:
        p.tpad.SetRightMargin(style["margin_right"])

def pad_basis(p : pad, style: Dict[str, Any]):

    if p.basis is None:
        log.error("Called pad style but no basis yet!")
        raise RuntimeError
    log.info("Updating basis style")

    if "x_titleOffset" in style:
        p.basis.th.GetXaxis().SetTitleOffset(style["x_titleOffset"])
    if "x_titleSize" in style:
        p.basis.th.GetXaxis().SetTitleSize(style["x_titleSize"])
    if "x_titleFont" in style:
        p.basis.th.GetXaxis().SetTitleFont(style["x_titleFont"])
    if "x_labelSize" in style:
        p.basis.th.GetXaxis().SetLabelSize(style["x_labelSize"])
    if "x_labelFont" in style:
        p.basis.th.GetXaxis().SetLabelFont(style["x_labelFont"])

    if "y_titleOffset" in style:
        p.basis.th.GetYaxis().SetTitleOffset(style["y_titleOffset"])
    if "y_titleSize" in style:
        p.basis.th.GetYaxis().SetTitleSize(style["y_titleSize"])
    if "y_titleFont" in style:
        p.basis.th.GetYaxis().SetTitleFont(style["y_titleFont"])
    if "y_labelSize" in style:
        p.basis.th.GetYaxis().SetLabelSize(style["y_labelSize"])
    if "y_labelFont" in style:
        p.basis.th.GetYaxis().SetLabelFont(style["y_labelFont"])

    if "n_div" in style:
        if len(style["n_div"]) != 2:
            log.error("n_div option in wrong format, need two items")
        p.basis.th.SetNdivisions(style["n_div"][0], style["n_div"][1])