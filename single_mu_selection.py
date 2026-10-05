import ROOT
import sys
import argparse

##### SETUP #####

trigger_sets = {
    "highpt":  ["HLT_Mu50", "HLT_HighPtTkMu100", "HLT_CascadeMu100"],
    "all":     ["HLT_IsoMu24", "HLT_Mu50", "HLT_HighPtTkMu100", "HLT_CascadeMu100"]
} 

parser = argparse.ArgumentParser()
parser.add_argument("file")
parser.add_argument("output")
parser.add_argument("--trigger", choices=trigger_sets.keys(), default="highpt")
args = parser.parse_args()

ROOT.EnableImplicitMT() # enabling multithreading

with open(args.file) as f:
    files = [l.strip() for l in f if l.strip() and not l.startswith("#")] # Grabbing samples to use

# Value setup

good_mu_pt_min = 20 # in GeV
signal_mu_pt_min = 55 # subset ^

## UNUSED ##
jet_mu_r = 0.4 # AK4
fatjet_mu_r = 0.8 #AK8
####

##### DATAFRAME, TRIGGERS, & MU DEFINITION #####

df = ROOT.RDataFrame("Events", files) # Grabbing all events frmo the files

trigger_expr = " || ".join(trigger_sets[args.trigger])
df_trig = df.Filter(trigger_expr, f"trigger: {trigger_expr}") # Filtering by triggers

df_mu = ( # Grabbing exactly one signal muon
    df_trig
    .Define("GoodMuon", f"Muon_pt > {good_mu_pt_min} && Muon_looseId") # When good muon...
    .Define("SignalMuon", f"GoodMuon && Muon_pt > {signal_mu_pt_min} && Muon_mediumPromptId") # Find the signal muon on top of the good muon
    .Filter("Sum(SignalMuon) == 1", "exactly 1 SignalMuon")
    .Filter("Sum(GoodMuon) == 1", "no additional GoodMuon")
    .Define("mu_idx", "ROOT::VecOps::ArgMax(Muon_pt * SignalMuon)")  # leading signal muon
    .Define("mu_pt", "Muon_pt[mu_idx]")
    .Define("mu_eta", "Muon_eta[mu_idx]")
    .Define("mu_phi", "Muon_phi[mu_idx]")
)


##### HISTOGRAMS & OUTPUT #####
hists = [ # Should this be weighted based on luminosity?
    df_mu.Histo1D(("h_mu_pt", "Signal muon p_{T};p_{T} [GeV];Events", 50, 0, 500), "mu_pt"),
    df_mu.Histo1D(("h_mu_eta", "Signal muon #eta;#eta;Events", 50, -2.5, 2.5), "mu_eta"),
    df_mu.Histo1D(("h_mu_phi", "Signal muon #phi;#phi;Events", 50, -3.2, 3.2), "mu_phi"),
]

report = df_mu.Report()

out = ROOT.TFile(args.output, "RECREATE") 
for h in hists:
    h.GetValue().Write()
out.Close()

report.Print()
