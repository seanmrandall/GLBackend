# GLBackend

This is the server side component of GlobaLeaks. It is through this piece of
software that the Node Administrator is able to anonymously setup and expose
GlobaLeaks Node.

It is implemented based on Twisted (using cyclone) and uses Storm as a
database.

**Warning** This version of software is under heavy development and is not
reccommended to be used by anybody.

If you are interested in running a GlobaLeaks node, you should try
[GlobaLeaks 0.1](https://github.com/globaleaks/globaleaks-0.1) the currently
"stable" release.

# Dependencies

GLBackend is written in Python version [2.7](http://docs.python.org/whatsnew/) 
and is mostly based on [twisted](twistedmatrix.com). For more informations see [requirements.txt](https://github.com/globaleaks/GLBackend/blob/master/requirements.txt)

# Getting Started

See wiki page [Setting up Development Environment](https://github.com/globaleaks/GLBackend/wiki/Setting-up-development-environment)

Start the software, using

    bin/startglobaleks

Emulate the initialization wizard using (remind, you need HTTPie to run wizard.sh)

   cd shooter/
   ./wizard.sh

  * shooter.py act like a client and is update with the interface supported in GLBacked. 
  * The script creating the first context and receivers, emulating the wizards that would be
    implemented in GLClient.

Or go in http://127.0.0.1:8082/#/ where GLBackend serve GLClient (you need GLBackend and
[GLClient](https://github.com/globaleaks/GLClient) in the same directory)

# Documentation

  * [Main GlobaLeaks documentation](https://github.com/globaleaks/GlobaLeaks/wiki/Home)
  * [GLBackend specific documentation](https://github.com/globaleaks/GLBackend/wiki/Home)
  * [APAF](https://github.com/globaleaks/APAF/wiki/Home): is the package manager developed for
    expose GLBackend as [Tor](http://www.torproject.org) [hidden service](https://www.torproject.org/docs/tor-hidden-service.html.en).
