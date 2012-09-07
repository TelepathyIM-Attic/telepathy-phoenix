EXTRA_DIST = \
  echo-call-info.xml \
  $(bin_SCRIPTS_IN) \
  $(python_DATA) \
  $(libexec_SCRIPTS)

bin_SCRIPTS=phoenix phoenix-test
bin_SCRIPTS_IN=phoenix.in phoenix-test.in

pythondir = $(pkgdatadir)
python_DATA=phoenix.py phoenix-test.py util.py

libexec_PROGRAMS = phoenix-authenticator phoenix-echo-call
libexec_SCRIPTS = phoenix-echo-text phoenix-approver

phoenix_authenticator_SOURCES = authenticator.c
phoenix_authenticator_CFLAGS = @GLIB_CFLAGS@ @TP_GLIB_CFLAGS@
phoenix_authenticator_LDFLAGS = @GLIB_LIBS@ @TP_GLIB_LIBS@

phoenix_echo_call_SOURCES = echo-call.c \
    echo-call-info-dbus.c echo-call-info-dbus.h
phoenix_echo_call_CFLAGS = @GLIB_CFLAGS@ @TP_GLIB_CFLAGS@ \
                               @TP_FARSTREAM_CFLAGS@
phoenix_echo_call_LDFLAGS = @GLIB_LIBS@ @TP_GLIB_LIBS@ \
                               @TP_FARSTREAM_LIBS@

phoenix: phoenix.in
	sed -e "s,PKGDATADIR,$(pkgdatadir)," < $<  > $@

phoenix-test: phoenix-test.in
	sed -e "s,PKGDATADIR,$(pkgdatadir)," < $<  > $@

CLEANFILES = $(bin_SCRIPTS)
