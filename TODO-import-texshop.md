## Deal with very old versions

* old versions are not always easy to sort auomatically. Specify a manual order?

* Better: provide release dates for each version (see below), then automatically sort
  releases by date


## Release dates

* tell import-zips which dates to use,
  e.g. via a hash table in import-zips

  Or perhaps have a file "date-VER.txt" which contains an ISO 8601 date;
 it is used if present, otherwise the date is computed automatically as before

* some of the .zip files for older versions sent by Richard Koch are "polluted"
  in the sense that they contain ctimes / mtimes in 2016.
  -> create a script which reads those .zip files, and computes the "latest modification"
  from those, ignoring any dates past a certain point (say 2015+... TBD).
  
  Then let that script generate VER/date.txt files


* check the version history files for more dates, and compare those with the above dates?


* Some historic versions, from versiontracker

2.33 (2010-03-03)
2.31 (2010-02-18)
2.30 (2010-02-03)
2.29 (2009-12-25)
2.26 (2009-03-17)
2.25 (2009-02-26)
2.20 (2009-01-26)
2.18 (2008-08-29)
2.15 (2008-05-08)
2.14 (2007-08-17)
2.13 (2007-08-09)
2.12 (2007-08-08)
2.10beta10 (2007-06-01)
2.10beta9 (2007-05-20)
2.10beta8 (2007-02-11)
2.10beta7 (2007-02-10)
2.10beta6 (2007-02-09)
2.10beta5 (2007-02-07)
2.10beta2 (2006-06-12)
2.10beta (2006-06-04)
2.0.9c (2006-05-25)
2.0.9b (2006-03-12)
2.0.9a (2006-02-05)
2.0.9 (2006-01-22)
2.0.8 (2006-01-12)
2.0.7 (2006-01-10)
2.0.5 (2006-01-09)
2.0.3 (2005-05-18)
2.0.2 (2005-05-10)
2.0.1 (2005-05-02)
2.0 (2005-04-29)


