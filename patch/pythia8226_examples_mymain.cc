// mymain.cc:
// To simulate particle events with their transverse momentum and energy
// Created By: Milan Ganai
// December 2017

#include "Pythia8/Pythia.h"

#include "Pythia8Plugins/FastJet3.h"

using namespace Pythia8;

//==========================================================================

// Method to pick a number according to a Poissonian distribution.

int poisson(double nAvg, Rndm& rndm) {

  // Set maximum to avoid overflow.
  const int NMAX = 100;

  // Random number.
  double rPoisson = rndm.flat() * exp(nAvg);

  // Initialize.
  double rSum  = 0.;
  double rTerm = 1.;

  // Add to sum and check whether done.
  for (int i = 0; i < NMAX; ) {
    rSum += rTerm;
    if (rSum > rPoisson) return i;

    // Evaluate next term.
    ++i;
    rTerm *= nAvg / i;
  }

  // Emergency return.
  return NMAX;
}

/*
  parameters to change:
  nPileupAvg = [3,50] {check "cern_1406.0076.pdf, pg 5, sec 4}
  eCM = {7, 14}


*/
double nPileupAvg = 2.5;
int nEvent    = 1;
double eCM = 14000. ;
string fname;
int seed = 10000002;

int simulate();

int main() {

   string line;

   while (getline(cin, line)) {
     istringstream linestream(line);
     if (line.substr(0,1) == "#") {continue;}
     if (line.substr(0,3) == "EOF") {break;}
     linestream >> nEvent >> eCM >> nPileupAvg >> seed >> fname;
     simulate();
   }
   return 0;
}


int simulate() {


  // Average number of pileup events per signal event.
  double etaMax  = 5.0;    // Pseudorapidity range of detector.


  // Generator. Shorthand for event.
  Pythia pythia;
  Event& event = pythia.event;


  // No event record printout.
  pythia.readString("Next:numberShowInfo = 0");
  pythia.readString("Next:numberShowProcess = 0");
  pythia.readString("Next:numberShowEvent = 0");

  // LHC initialization.
  pythia.readString("Beams:idA = 2212");
  pythia.readString("Beams:idB = 2212");
  //pythia.readString("Beams:eCM = 14000.");
  pythia.settings.parm("Beams:eCM", eCM);

  // Initialize generator for pileup (background) processes.
  // Background generator instances copies settings and particle data.
  Pythia pythiaPileup(pythia.settings, pythia.particleData);

  // Process selection.
  pythia.readString("HardQCD:all = on");
  pythia.readString("PhaseSpace:pTHatMin = 200.");


  pythia.init();


  pythiaPileup.readString("Random:setSeed = on");
  //pythiaPileup.readString("Random:seed = 10000002");
  pythiaPileup.settings.parm("Random:seed", seed);
  pythiaPileup.readString("SoftQCD:all = on"); //ND, DD, SD, elastic
  pythiaPileup.readString("Tune:pp = 5"); //4C

  pythiaPileup.init();


  ofstream myout;
  myout.open(fname.c_str());

  // Begin event loop. Generate event. Skip if error.
  for (int iEvent = 0; iEvent < nEvent; ++iEvent) {
    if (!pythia.next()) continue;

    myout << "#SUBSTART" << endl;
    for (int i = 0; i < event.size(); ++i) if (event[i].isFinal()) {
      // Require visible/charged particles inside detector.
      if (!event[i].isVisible() ) continue;
      if (etaMax < 20. && abs(event[i].eta()) > etaMax) continue;
      if (event[i].pT() < 0.) continue;

      myout << (event[i].name()) << " ";
      myout << (event[i].isNeutral() ? "n" : "c") << " ";
      myout << "h ";
      myout << event[i].px() << " " << event[i].py() << " " << event[i].pz() << " "  <<
              event[i].e() << endl;
    }

    int pileId = event.size();
    cout << "DEBUG: nevent = " << event.size() << endl;
    // Select the number of pileup events to generate.
    int nPileup = poisson(nPileupAvg, pythiaPileup.rndm);


    // Generate a number of pileup events. Add them to event.
    for (int iPileup = 0; iPileup < nPileup; ++iPileup) {
      pythiaPileup.next();
      event += pythiaPileup.event;
    }

    cout << "DEBUG: nPileup = "<< nPileup << " nevent = " << event.size() << endl;

    myout << "#SUBSTART" << endl;
    for (int i = pileId; i < event.size(); ++i) if (event[i].isFinal()) {

      // Require visible/charged particles inside detector.
      if (!event[i].isVisible() ) continue;
      if (etaMax < 20. && abs(event[i].eta()) > etaMax) continue;
      if (event[i].pT() < 0.) continue;

      myout << (event[i].name()) << " ";
      myout << (event[i].isNeutral() ? "n" : "c") << " ";
      myout << "p ";
      myout << event[i].px() << " " << event[i].py() << " " << event[i].pz() << " "  <<
              event[i].e() << endl;
    }
    myout << "#END" << endl;

  // End of event loop.
  }
  myout.close();

  // Statistics. Histograms.
  //pythia.stat();

  // Done.
  return 0;
}
