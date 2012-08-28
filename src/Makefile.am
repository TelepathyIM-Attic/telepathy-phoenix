EXTRA_DIST = \
  approver.py \
  echo-text.py \
  phoenix.py  \
  util.py

libexec_PROGRAMS = phoenix-authenticator

phoenix_authenticator_SOURCES = authenticator.c
phoenix_authenticator_CFLAGS = @GLIB_CFLAGS@ @TP_GLIB_CFLAGS@
phoenix_authenticator_LDFLAGS = @GLIB_LIBS@ @TP_GLIB_LIBS@
