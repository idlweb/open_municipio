.. -*- mode: rst -*-
 
========================================
Deploying with Fab
========================================

.. contents::

Overview
========

This document describes how to create a fab configuration for deploying
*OpenMunicipio* on a remote server.

Most of the setup is ready in the ``fabfile.sample`` directory. Here we describe
some basic assumptions about the target server environment, and how to customize
those sample files.

Requirements
============

* Copy the directory ``fabfile.sample`` in ``fabfile`` (e.g. ``cp -r fabfile.sample fabfile``)

* In the following we represent with ``CAPITAL LETTERS`` variables defined in 
  ``fabfile/conf_{staging|production}.py`` file (e.g. ``SERVER_MACHINE``, ``PYTHON_BIN``, ...)

* Your user on your local machine should have a public RSA key set and placed in a
  file in path `${HOME}/.ssh/id_rsa.pub`

* It is required that you know the ``root`` password of the target server, or at
  least your public key is in the set of allowed keys for login as root (i.e. ask 
  the administrator to add your public key to the file 
  ``/root/.ssh/authorized_keys``).

* Right now the procedure creates users ``OM_USER` and ``SOLR_USER`` but it does not 
  add them the ``sudo`` group of the remote server. The administrator of the remote
  host should do this manually,  until either we avoid using sudo-powers for them 
  or we automatically add them to the ``sudo`` group. 

* Be sure you read section  `Content indexing and searching`_ and have files 
  ``solr/context_staging.xml`` and ``solr/context_production.xml`` ready for your 
  deploy.

* Copy folder ``postgres.sample/`` to folder ``postgres`` and modify its files 
  according to your server configuration. *Beware that such files will overwrite 
  system configuration of postgres on the remote host.*

* Copy folder ``system.sample`` to folder ``system`` and modify its files according
  to your server configuration.

* At the moment, ``apache2`` is required for deploying *Open Municipio*, but it is
  not installed automatically by the ``fab ... setup_platform`` command, because 
  its configuration is usually a delicate task, and the server admin should take 
  care of it, personally.

* In case you deploy with ``apache``, copy the folder ``apache.sample`` to folder
  ``apache``, and check its files contain meaningful paths and configuration 
  parameters

* Create a role ``oo`` in your postgresql server, e.g. with the following commands::

    # su postgres
    $ createuser oo

Create your fabfile
===================

* Copy the content of folder ``fabfile.sample`` into ``fabfile``
* Edit files ``fabfile/conf_staging.py`` and ``fabfile/conf_production.py`` 
  according to your server parameters

Start deploying to s
===============

* Execute command: ``fab staging setup_platform``
* Execute command: ``fab staging initial_deploy``
