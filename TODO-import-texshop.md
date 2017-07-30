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
