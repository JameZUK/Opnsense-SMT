PLUGIN_NAME=SMT
PLUGIN_VERSION=0.1
PLUGIN_COMMENT="Social Media Timeout Plugin for OPNsense"

.PHONY: all package install

all: package

package:
	pkg create -r . -M pkg_manifest -p pkg-plist -o ./smt-${PLUGIN_VERSION}.txz

install:
	pkg install smt-${PLUGIN_VERSION}.txz
	# Install Python dependencies
	/usr/local/bin/python3 -m pip install --upgrade pip
	/usr/local/bin/python3 -m pip install -r /usr/local/opnsense/scripts/smt/requirements.txt
