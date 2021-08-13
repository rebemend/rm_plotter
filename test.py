from plotter import collection, dataset
from plotter import histo, pad, canvas, atlas, legend
from plotter import loader
import ROOT

import logging
logging.basicConfig(
    level=logging.INFO, format="%(levelname)s (%(name)s): %(message)s"
)
log = logging.getLogger(__name__)

atlas.SetAtlasStyle()

cData = collection("Data")
cData.add_dataset(dataset("Data", "test/Nominal/data.root"))

cBkg = collection("Bkg")
cBkg.add_dataset(dataset("Bkg", "test/Nominal/background.root"))

hD = histo("Data", cData.get_th("ptll_data"), configPath="configs/data.json")
hB = histo("Top+EW", cBkg.get_th("ptll_topew"), fillColor=ROOT.kRed,
           configPath="configs/mc.json")

c = canvas("canvas")

p = pad("main", yl=0.5)
c.add_pad(p)
p.add_histos([hD, hB])
p.set_title("p_{T}^{ll}", "Events")
p.logx()
p.logy()
p.margins(down=0)
p.plot_histos()

hR = hD.get_ratio(hD)
hR.set_fillColor(ROOT.kGray+1)
hR.set_lineColor(ROOT.kGray+1)
cfgErr = loader.load_config("configs/err.json")
hR.style_histo(cfgErr)

pR = pad("ratio", yl=0.3, yh=0.5)
c.add_pad(pR)
pR.set_yrange(0.701, 1.299)
pR.add_histos([hR])
pR.logx()
pR.set_title("p_{T}^{ll}", "Ratio")
pR.margins(up=0, down=0)
pR.plot_histos()

hR2 = hB.get_ratio(hD, fillToLine=True)

pR2 = pad("ratio", yh=0.3)
c.add_pad(pR2)
pR2.set_yrange(0.001, 0.299)
pR2.add_histos([hR2])
pR2.logx()
pR2.set_title("p_{T}^{ll}", "Fraction")
pR2.margins(up=0)
pR2.plot_histos()

c.tcan.cd()
atlas.ATLASLabel(0.22, 0.92, "Internal")

leg = legend()
leg.add_histos([hD, hB])
leg.create_and_draw()

c.save("test/ptll.png")
