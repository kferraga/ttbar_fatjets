import ROOT
ROOT.gROOT.SetBatch(True)

f = ROOT.TFile.Open("test.root")
c = ROOT.TCanvas()
for name in ["h_mu_pt", "h_mu_eta", "h_mu_phi"]:
    h = f.Get(name)
    h.Draw("HIST")
    c.SaveAs(f"{name}.png")