PLUGIN_NAME=SMT
PLUGIN_VERSION=0.1
PLUGIN_DESC="Social Media Timeout Plugin for OPNsense"

.PHONY: all package install

all: package

package:
	pkg create -r . -m pkg-descr -p pkg-plist -o ./smt-${PLUGIN_VERSION}.txz

install:
	pkg install smt-${PLUGIN_VERSION}.txz
	# Install Python dependencies
	/usr/local/bin/python3 -m pip install --upgrade pip
	/usr/local/bin/python3 -m pip install -r /usr/local/opnsense/mvc/app/plugins/smt/etc/opnsense/scripts/smt/requirements.txt
