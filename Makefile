#!/bin/bash
PLUGIN_NAME=SMT
PLUGIN_VERSION=0.1
PLUGIN_DESC="Social Media Timeout Plugin for OPNsense"

.PHONY: all package install

all: package

package:
\tpkg create -m Makefile -r . -o ./smt-${PLUGIN_VERSION}.txz

install:
\tpkg install smt-${PLUGIN_VERSION}.txz
\t# Install Python dependencies
\t/usr/local/bin/python3 -m pip install --upgrade pip
\t/usr/local/bin/python3 -m pip install -r /usr/local/opnsense/mvc/app/plugins/smt/etc/opnsense/scripts/smt/requirements.txt

