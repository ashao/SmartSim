# BSD 2-Clause License
#
# Copyright (c) 2021-2024 Hewlett Packard Enterprise
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# Location to place the final dependencies
INSTALL_LOCATION := $(PWD)/install
DEPENDENCY_DESTINATION = $(INSTALL_LOCATION)
MODULEFILE_DESTINATION = $(INSTALL_LOCATION)/modulefiles
DEPENDENCY_SCRATCH = $(PWD)/dependencies

LIBFFI_VERSION = 3.4.3
LIBFFI_URL = https://gcc.gnu.org/pub/libffi/libffi-$(LIBFFI_VERSION).tar.gz
LIBFFI_NAME = libffi-$(LIBFFI_VERSION)
LIBFFI_DESTINATION = $(DEPENDENCY_DESTINATION)/libffi/$(LIBFFI_VERSION)
LIBSQLITE3_VERSION_STRING = 3440200
LIBSQLITE3_VERSION = 3.44.2
LIBSQLITE3_NAME = sqlite-autoconf-$(LIBSQLITE3_VERSION_STRING)
LIBSQLITE3_URL = https://www.sqlite.org/2023/$(LIBSQLITE3_NAME).tar.gz
LIBSQLITE3_DESTINATION = $(DEPENDENCY_DESTINATION)/libsqlite3/$(LIBSQLITE3_VERSION)
JQ_VERSION = 1.7.1
JQ_NAME = jq-$(JQ_VERSION)
JQ_URL = https://github.com/jqlang/jq/releases/download/$(JQ_NAME)/jq-linux-amd64
JQ_DESTINATION = $(DEPENDENCY_DESTINATION)/jq/$(JQ_VERSION)
GIT_LFS_VERSION = 3.5.1
GIT_LFS_URL = https://github.com/git-lfs/git-lfs/releases/download/v$(GIT_LFS_VERSION)/git-lfs-linux-amd64-v$(GIT_LFS_VERSION).tar.gz
GIT_LFS_NAME = git-lfs-$(GIT_LFS_VERSION)
GIT_LFS_DESTINATION = $(DEPENDENCY_DESTINATION)/git-lfs/$(GIT_LFS_VERSION)

CUDATOOLKIT_MAJOR_VERSION = 11
CUDATOOLKIT_MINOR_VERSION = 8
CUDATOOLKIT_SUBMINOR_VERSION = 0

CUDATOOLKIT_VERSION = $(CUDATOOLKIT_MAJOR_VERSION).$(CUDATOOLKIT_MINOR_VERSION).$(CUDATOOLKIT_SUBMINOR_VERSION)
CUDATOOLKIT_DRIVER_VERSION = 520.61.05
CUDATOOLKIT_INSTALL_FILE = cuda_$(CUDATOOLKIT_VERSION)_$(CUDATOOLKIT_DRIVER_VERSION)_linux.run
CUDATOOLKIT_URL = https://developer.download.nvidia.com/compute/cuda/$(CUDATOOLKIT_VERSION)/local_installers/$(CUDATOOLKIT_INSTALL_FILE)
CUDATOOLKIT_DESTINATION = $(DEPENDENCY_DESTINATION)/cudatoolkit/$(CUDATOOLKIT_VERSION)/

CUDNN_VERSION = 8.9.7.29
CUDNN_INSTALL_FILE = libcudnn8-$(CUDNN_VERSION)-1.cuda$(CUDATOOLKIT_MAJOR_VERSION).$(CUDATOOLKIT_MINOR_VERSION).x86_64.rpm
CUDNN_URL = https://developer.download.nvidia.com/compute/cuda/repos/rhel9/x86_64/$(CUDNN_INSTALL_FILE)
CUDNN_DESTINATION = $(DEPENDENCY_DESTINATION)/cudnn/$(CUDNN_VERSION)/

# Note this points to a specific commit, since pyenv-installer doesn't have tags
PYENV_VERSION = 86a08ac9e38ec3a267e4b5c758891caf1233a2e4
PYENV_URL = https://raw.githubusercontent.com/pyenv/pyenv-installer/$(PYENV_VERSION)/bin/pyenv-installer
PYENV_DESTINATION = $(INSTALL_LOCATION)/pyenv

.DEFAULT_GOAL := help
OUTPUT = /dev/null
ifeq ($(VERBOSE),1)
	OUTPUT = &1
endif


# Do not remove this block. It is used by the 'help' rule when
# constructing the help output.
# help:
# help: Testing infrastructure makefile help
# help:

.PHONY: help
help:
	@grep "^# help\:" Makefile | grep -v grep | sed 's/\# help\: //' | sed 's/\# help\://'

# help: ----Description----
# help: This makefile coordinates the installation of various dependencies that commonly need to be
# help: installed as part of the nightly testing for SmartSim and SmartRedis. These nominally
# help: include jq, libffi, and libsqlite3. jq is needed by the testing suite to read in the
# help: JSON-based configuration files whereas libffi and libsqlite3 are need to compile various
# help: versions of Python via pyenv.
# help:
# help: Most users will only need to modify the INSTALL_LOCATION variable to point to their own
# help: scratch space:
# help:
# help:    make INSTALL_LOCATION=/path/to/user/scratch/ user-deps
# help:
# help: Occasionally, the SmartSim team's main modulefiles may also need to be
# help: updated. For most internal machines this should be the team's scratch space
# help:
# help:    make INSTALL_LOCATION=/lus/scratch/smartsim/local system-gpu # system-cpu
# help:
# help: Some dependencies e.g. cudNN) are not possible to install via this Makefile
# help: These are listed under the "extras" target and contain text instructions
# help:
# help: To see the output from make commands, run make with VERBOSE=1
# help:
# help: ----Meta targets----
# help:

# help: help                    - Display this makefile's help information
# help: user-deps               - Make basic dependencies and modulefiles (not extras)
.PHONY: user-deps
deps: pyenv pyenv_init

# help: system-cpu		- Install only system libraries on cpu (i.e. for site install)
.PHONY: system-cpu
system-cpu: libffi libsqlite3 jq git-lfs

# help: system-gpu		- Install only system libraries on gpu (i.e. for site install)
.PHONY: system-gpu
system-gpu: system-cpu cudatoolkit cudnn


# help: uninstall               - Uninstalls all libraries and modulefiles
.PHONY: uninstall
uninstall: uninstall_cudatoolkit uninstall_jq uninstall_libffi uninstall_libsqlite3
	@rm -rf $(DEPENDENCY_SCRATCH)
	$(warning *** To uninstall pyenv, 'make uninstall_pyenv' manually ***)

# help:
# help: ----Individual targets----
# help:

# help: libffi                  - Compiles and installs FFI (needed for Python)
.PHONY: libffi
libffi: $(LIBFFI_DESTINATION)/lib64/libffi.so $(MODULEFILE_DESTINATION)/libffi/$(LIBFFI_VERSION)

$(DEPENDENCY_SCRATCH)/$(LIBFFI_NAME):
	mkdir -p $(DEPENDENCY_SCRATCH) && \
		cd $(DEPENDENCY_SCRATCH)   && \
		wget $(LIBFFI_URL)		   && \
		tar -xvzf $(LIBFFI_NAME).tar.gz 1>$(OUTPUT)

$(LIBFFI_DESTINATION)/lib64/libffi.so: $(DEPENDENCY_SCRATCH)/$(LIBFFI_NAME)
	$(info Making $@)
		cd $(DEPENDENCY_SCRATCH)/$(LIBFFI_NAME) && \
		./configure --prefix=$(LIBFFI_DESTINATION) --enable-shared 1>$(OUTPUT) && \
		make -j install 1>$(OUTPUT)

$(MODULEFILE_DESTINATION)/libffi/$(LIBFFI_VERSION):
	mkdir -p $(MODULEFILE_DESTINATION)/libffi
	sed -e "s,;version;,$(LIBFFI_VERSION),g" \
		-e "s,;libffi_root;,$(LIBFFI_DESTINATION),g" .templates/libffi > $@

# help: libsqlite3              - Compiles and installs SQLite3 (needed for Python)
.PHONY: libsqlite3
libsqlite3: $(LIBSQLITE3_DESTINATION)/lib/libsqlite3.so $(MODULEFILE_DESTINATION)/libsqlite3/$(LIBSQLITE3_VERSION)

$(DEPENDENCY_SCRATCH)/$(LIBSQLITE3_NAME):
	mkdir -p $(DEPENDENCY_SCRATCH) && \
		cd $(DEPENDENCY_SCRATCH)   && \
		wget $(LIBSQLITE3_URL)     && \
		tar -xzf $(LIBSQLITE3_NAME).tar.gz

$(LIBSQLITE3_DESTINATION)/lib/libsqlite3.so: $(DEPENDENCY_SCRATCH)/$(LIBSQLITE3_NAME)
	$(info Making $@)
	cd $(DEPENDENCY_SCRATCH)/$(LIBSQLITE3_NAME) && \
	./configure --prefix=$(LIBSQLITE3_DESTINATION) --enable-shared 1>$(OUTPUT) && \
	make -j install 1>$(OUTPUT)

$(MODULEFILE_DESTINATION)/libsqlite3/$(LIBSQLITE3_VERSION): .templates/libsqlite3
	mkdir -p $(MODULEFILE_DESTINATION)/libsqlite3
	sed -e "s,;version;,$(LIBSQLITE3_VERSION),g" \
		-e "s,;root;,$(LIBSQLITE3_DESTINATION),g" .templates/libsqlite3 > $@


# help: jq                      - Compiles and installs jq (needed for test infrastructure)
.PHONY: jq
jq: $(JQ_DESTINATION)/bin/jq $(MODULEFILE_DESTINATION)/jq/$(JQ_VERSION)

$(JQ_DESTINATION)/bin/jq:
	$(info Making $@)
	mkdir -p $(DEPENDENCY_SCRATCH) && \
		cd $(DEPENDENCY_SCRATCH)   && \
		wget $(JQ_URL)             && \
		mkdir -p $(JQ_DESTINATION)/bin && \
		mv jq-linux-amd64 $(JQ_DESTINATION)/bin/jq
		chmod a+x $(JQ_DESTINATION)/bin/jq

$(MODULEFILE_DESTINATION)/jq/$(JQ_VERSION): .templates/jq
	mkdir -p $(MODULEFILE_DESTINATION)/jq
	cp .templates/jq $@
	sed -e "s,;version;,$(JQ_VERSION),g" \
	    -e "s,;root;,$(JQ_DESTINATION),g" .templates/jq > $@

# help: git-lfs                 - Compiles and installs git-lfs (needed for test infrastructure)
.PHONY: git-lfs
git-lfs: $(GIT_LFS_DESTINATION)/bin/git-lfs $(MODULEFILE_DESTINATION)/git-lfs/$(GIT_LFS_VERSION)

$(GIT_LFS_DESTINATION)/bin/git-lfs:
	$(info Making $@)
	mkdir -p $(DEPENDENCY_SCRATCH) && \
		cd $(DEPENDENCY_SCRATCH)   && \
		wget $(GIT_LFS_URL)             && \
		tar -xvzf git-lfs-linux-amd64-v$(GIT_LFS_VERSION).tar.gz && \
		mkdir -p $(GIT_LFS_DESTINATION)/bin && \
		mv git-lfs-$(GIT_LFS_VERSION)/git-lfs $(GIT_LFS_DESTINATION)/bin/

$(MODULEFILE_DESTINATION)/git-lfs/$(GIT_LFS_VERSION): .templates/git-lfs
	mkdir -p $(MODULEFILE_DESTINATION)/git-lfs
	cp .templates/git-lfs $@
	sed -e "s,;version;,$(GIT_LFS_VERSION),g" \
	    -e "s,;root;,$(GIT_LFS_DESTINATION)/bin,g" .templates/git-lfs > $@

# help: cudatoolkit             - Install Nvidia's Cuda toolkit (for GPU support)
.PHONY: cudatoolkit
cudatoolkit: $(CUDATOOLKIT_DESTINATION)/lib64 $(MODULEFILE_DESTINATION)/cudatoolkit/$(CUDATOOLKIT_VERSION)


$(DEPENDENCY_SCRATCH)/cudatoolkit/$(CUDATOOLKIT_INSTALL_FILE):
	$(info Downloading cudatoolkit, this may take a while)
	mkdir -p $(DEPENDENCY_SCRATCH)/cudatoolkit && \
	cd $(DEPENDENCY_SCRATCH)/cudatoolkit 	   && \
	wget $(CUDATOOLKIT_URL)					   && \
	chmod +x $(CUDATOOLKIT_INSTALL_FILE)

$(CUDATOOLKIT_DESTINATION)/lib64: $(DEPENDENCY_SCRATCH)/cudatoolkit/$(CUDATOOLKIT_INSTALL_FILE)
	$(info Installing cudatoolkit, this may take a while)
	$(DEPENDENCY_SCRATCH)/cudatoolkit/$(CUDATOOLKIT_INSTALL_FILE) \
		--silent \
		--toolkit \
		--toolkitpath=$(CUDATOOLKIT_DESTINATION) \
		--installpath=$(CUDATOOLKIT_DESTINATION)

$(MODULEFILE_DESTINATION)/cudatoolkit/$(CUDATOOLKIT_VERSION):
	mkdir -p $(MODULEFILE_DESTINATION)/cudatoolkit
	sed -e "s,;version;,$(CUDATOOLKIT_VERSION),g" \
		-e "s,;root;,$(CUDATOOLKIT_DESTINATION),g" .templates/cudatoolkit > $@

# help: cudnn                   - Install cuDNN (for Torch)
.PHONY: cudnn
cudnn: $(DEPENDENCY_SCRATCH)/cudnn/$(CUDNN_INSTALL_FILE) $(CUDNN_DESTINATION)/lib64 $(MODULEFILE_DESTINATION)/cudnn/$(CUDNN_VERSION)

$(DEPENDENCY_SCRATCH)/cudnn/$(CUDNN_INSTALL_FILE):
	$(info Downloading cudnn, this may take a while)
	mkdir -p $(DEPENDENCY_SCRATCH)/cudnn	 	&& \
		cd $(DEPENDENCY_SCRATCH)/cudnn		&& \
		wget $(CUDNN_URL)

$(CUDNN_DESTINATION)/lib64: $(DEPENDENCY_SCRATCH)/cudnn/$(CUDNN_INSTALL_FILE)
	cd $(DEPENDENCY_SCRATCH)/cudnn				&& \
		rpm2cpio $(CUDNN_INSTALL_FILE) | cpio -idmv	&& \
		mkdir -p $(CUDNN_DESTINATION)			&& \
		mv usr/lib64/ $(CUDNN_DESTINATION)

$(MODULEFILE_DESTINATION)/cudnn/$(CUDNN_VERSION):
	mkdir -p $(MODULEFILE_DESTINATION)/cudnn
	sed -e "s,;version;,$(CUDNN_VERSION),g" \
		-e "s,;root;,$(CUDNN_DESTINATION),g" .templates/cudnn > $@


# help: pyenv                   - Install pyenv (used for managing Python versions)
.PHONY: pyenv
pyenv: $(PYENV_DESTINATION)/bin/pyenv

$(PYENV_DESTINATION)/bin/pyenv:
	$(info Making pyenv)
	@curl -L $(PYENV_URL) | PATH=$(PYENV_DESTINATION)/bin:${PATH} PYENV_ROOT=$(PYENV_DESTINATION) bash

.PHONY: pyenv_init
pyenv_init: $(HOME)/.pyenv_init

$(HOME)/.pyenv_init: .templates/pyenv_init
	sed -e "s,;root;,$(PYENV_DESTINATION),g" .templates/pyenv_init > $@
	grep "source ~/.pyenv_init" ~/.bashrc || echo "source ~/.pyenv_init" >> ~/.bashrc

# help: ----Uninstall targets----
.PHONY: uninstall_libffi uninstall_libsqlite3 uninstall_jq uninstall_cudatoolkit uninstall_pyenv

#help : uninstall_libffi        - Removes libffi libraries and modulefile
uninstall_libffi:
	$(info Uninstalling libffi)
	@rm -rf $(LIBFFI_DESTINATION) $(MODULEFILE_DESTINATION)/libffi/$(LIBFFI_VERSION)

#help : uninstall_libsqlite3    - Removes sqlite3 libraries and modulefile
uninstall_libsqlite3:
	$(info Uninstalling libsqlite3)
	@rm -rf $(LIBSQLITE3_DESTINATION) $(MODULEFILE_DESTINATION)/libsqlite3/$(LIBSQLITE3_VERSION)

#help : uninstall_jq            - Removes jq binary and modulefile
uninstall_jq:
	$(info Uninstalling jq)
	@rm -rf $(JQ_DESTINATION) $(MODULEFILE_DESTINATION)/jq/$(JQ_VERSION)

#help : uninstall_cudatoolkit   - Removes cudatoolkit libraries and modulefile
uninstall_cudatoolkit:
	$(info Uninstalling cudatoolkit)
	@rm -rf $(CUDATOOLKIT_DESTINATION) $(MODULEFILE_DESTINATION)/cudatoolkit/$(CUDATOOLKIT_VERSION)

#help : uninstall_pyenv         - Removes pyenv and .bashrc initialization (manual only)
uninstall_pyenv:
	$(info Uninstalling pyenv)
	rm -rf $(PYENV_DESTINATION) ~/.pyenv_init
	sed -i '/source ~\/.pyenv_init/d' ~/.bashrc


