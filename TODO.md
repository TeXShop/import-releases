== General ==

* Once the repository is stable (i.e. no more new versions inserted into ancient
  history), upload the original .zip files (both sources and binaries) to the
  GitHub release system.
  Of course that should be done with a script
* Import the history of the old SVN repository?
* Find more old versions and import them

== import-zips.py ==

* Allow incremental mode, so that one does not need to rebuild the
  whole repository after each release
* add a map from versions to known releases dates, to be used instead of the
  date guessed from the tarball

* add initial commit which adds:

.gitignore:
/TeXShop.xcodeproj/*.mode*
/TeXShop.xcodeproj/*.pbxuser
/TeXShop.xcodeproj/xcuserdata

.gitattributes:
*.nib -diff


== texshop-watcher ==

* run it 24/7 as a cron job on a machine that is always online, so that
  we don't miss any releases
* send notification (via email?) if a new release is found
