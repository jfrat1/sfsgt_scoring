# SFSGT Scoring Tracker

I want to write a better scoring tracker for SFSGT. The numbers file
is good, but it requires too much manual work to fine-tune scores and set up new rounds.

## Requirements

### Requirements for UI

* Easy cloud-based way to input data - shareable numbers sheet is sweet
* Easy way to view the scores, standings, etc - either cloud based or a web page
* Score viewing should be updateable without me needing to be in front of a computer

### Requirements for scoring

* Can generate a new "season" with same underlying code and different data source
* Can add/subtract rounds with course data including handicap info
* Players can be added/subtracted with their user handicaps
* "running" handicap calculation
* Scores for each round, including handling ties, max strokes per hole by course, etc

## Setting up timed jobs

Timed jobs are implemented using cron. To set up a timed job:

* Open a Terminal window
* Enter `crontab -l` to list the currently-running cron jobs
* Enter `crontab -e` to edit the crontab file
  * If the default editor leads to an error, then enter `export EDITOR=/usr/bin/vi` then run `crontab -e`
* Copy the contentx of `crontab.txt` from this directory and past it into your cron editor
