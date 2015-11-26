SHCROOT=../3party/shc-3.8.9
SHC=shc
EXEC_PREFIX:=/promise/bin
POSTINSTALL_PREFIX=../mkpromiseiso/postinstall/cluster_wizard
EXEFILES=all_destroy.py \
	check_mcli_array.sh \
	cluster_wizard \
	create_cluster \
	create_volume \
	destroy_node \
	__init__.py \
	join_cluster \
	local_network_config_class.py \
	run_mcli.sh
MISCFILES=README

FILES=$(EXEFILES) $(MISCFILES)

all:

postfiles:
	mkdir -p $(POSTINSTALL_PREFIX)
	cp $(FILES) $(POSTINSTALL_PREFIX)
	cp Makefile $(POSTINSTALL_PREFIX)/
	rm -rf `find $(POSTINSTALL_PREFIX) -type d -name .svn`

postinstall:
	mkdir -p $(EXEC_PREFIX)
	install -m 644 $(MISCFILES) $(EXEC_PREFIX)/
	install -m 755 $(EXEFILES) $(EXEC_PREFIX)/


