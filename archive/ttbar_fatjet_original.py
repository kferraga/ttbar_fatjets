import ROOT
import sys

# python3 ttbar_fatjet.py filelist_https.txt

ROOT.EnableImplicitMT() # enabling multithreading

with open(sys.argv[1]) as f:
    files = [line.strip() for line in f if line.strip()]

hist = ROOT.TH1D("hist", "test", 100, 0, 100)
df = ROOT.RDataFrame("Events", files)

TKISOID = 2 # Loose or Tight?
WP_M = {"L": 0.0490, "M": 0.2783, "T": 0.7100}
# Filter - cut out events with only 1 muon
# Define - now instead create a new variable GoodMuon that selects for where the Muon_pt > 55, Muon_eta < 2.4, and muon's are tight

#FatJet_dRmu > 0.8 and Jet_dRmu > 0.4 currently not implemented
df_1mu = df.Define("GoodMuon", f"Muon_pt > 55 && abs(Muon_eta) < 2.4 && Muon_tkIsoId == {TKISOID}").Filter("Sum(GoodMuon) == 1", "events with exactly one muon").Define("mu_idx", "ROOT::VecOps::ArgMax(GoodMuon)")
df_g2jet = df_1mu.Define("GoodJet", "Jet_pt > 30 && abs(Jet_eta) < 2.5").Filter("Sum(GoodJet) >= 2", "events with more than two AK4 jets")
df_g2bjet = df_g2jet.Define("GoodBJet", f"GoodJet && Jet_btagDeepFlavB > {WP_M["M"]}").Filter("Sum(GoodBJet) >= 2", "events with more than two b jets") # Wwant to select for bjets that are distinct from the muon. 0.4 (cone radius) tends to be a good cutoff
df_1ak8 = df_g2bjet.Define("GoodFatJet", "FatJet_pt > 200 && abs (FatJet_eta) < 2.4").Filter("Sum(GoodFatJet) == 1", "events with exactly 1 fat jet")


# Above is a boolean mask. This 4vec then reduces the events down to only those desired. But do these values need to be defined again? 
# ArgMax grabs the highest scoring jets
# Grabbing the 4vectors for the bjet and fatjet
# Reconstruct based on the top quark decay to W boson -> fat jet & b jet
def_4vec = (df_1ak8.Define("bjet_idx", "ROOT::VecOps::ArgMax(GoodBJet * Jet_btagDeepFlavB)")
                .Define("fatjet_idx", "ROOT::VecOps::ArgMax(GoodFatJet)")
                .Define("fatjet_p4", "ROOT::Math::PtEtaPhiMVector(FatJet_pt[fatjet_idx], FatJet_eta[fatjet_idx], FatJet_phi[fatjet_idx], FatJet_msoftdrop[fatjet_idx])")
                .Define("bjet_p4", "ROOT::Math::PtEtaPhiMVector(Jet_pt[bjet_idx], Jet_eta[bjet_idx], Jet_phi[bjet_idx], Jet_mass[bjet_idx])")
                .Filter("ROOT::Math::VectorUtil::DeltaR(fatjet_p4, bjet_p4) > 0.8", "b not in fatjet")
                .Define("top_p4", "fatjet_p4 + bjet_p4")
                .Define("top_mass", "top_p4.M()"))

# {XXX} is subscript
h_w = df.Histo1D(("h_w", "AK8 soft drop mass;m_{soft_drop} [GeV];Events", 60, 0, 400), "FatJet_msoftdrop")
h_top = df.Histo1D(("h_top", "Reconstructed top;m_{top} [GeV];Events", 60, 0, 400), "top_mass")

report = def_4vec.Report()
c = ROOT.TCanvas()
h_w.Draw(); c.SaveAs("w_mass.png")
h_top.Draw(); c.SaveAs("top_mass.png")
report.Print()
