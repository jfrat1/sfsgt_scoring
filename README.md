# San Francisco Summer Golf Tour Scoring Tracker

The SFSGT is a recreational golf tour that was founded by a close friend of mine
in 2022.  I set up a spreadsheet to track scoring for the first year, but it quickly
got out of hand. In 2023 I wrote some python code to do the scoring for us. This
repo is the result of that effort.

## Repository Organization

- .vscode/settings.json
  - VSCode setting specific to this project.
- ad_hoc_events
  - Code to calculate handicaps and scoring for special events that are not
    part of the SFSGT season.
- docs
  - This is a bit of a pipe dream for a personal project, but here's
    to hoping that I actually write some things down as I go along.
- google_cloud_creds
  - Credentials for accessing google content are stored here. The creds files
    themselves are ignored in the published version of this repo.
- scripts
  - Folder to store handy scripts for executing tests or real runs of the
    application. As of this writing, there isn't much content here yet.
- sfsgt_scoring
  - This folder holds all of the python sources and tests which make up the
    scoring application.
- sfsgt_scoring_2023
  - This is a copy of the 2023 version of the scoring app which I'm using
    for reference while rebuilding the main app. It's subject to deletion
    at any time.
- README.MD
  - This file
- requirements.txt
  - Python requirements that must be installed to execute the SFSGT scoring application.

## Python Environment Setup

As of this writing, the SFSGT scoring app has been developed and tested
with **Python 3.12.2**.

A requirements file is provided at the root of this repo named `requirements.txt`.
To install the required packages into your python environment, run this command
from the root of the repository.

```sh
pip install -r requirements.txt
```

## Requirements

### Requirements for UI

* Easy cloud-based way to input data - shareable numbers sheet is sweet
* Easy way to view the scores, standings, etc - either cloud based or a web page
* Scores should be updateable without needing to be in front of a computer

### Requirements for scoring

* Can generate a new "season" with same underlying code and different data source
* Can add/subtract rounds with course data including handicap info
* Players can be added/subtracted with their user handicaps
* "running" handicap calculation
* Scores for each round, including handling ties, max strokes per hole by course, etc
