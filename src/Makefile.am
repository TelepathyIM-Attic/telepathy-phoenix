EXTRA_DIST = \
  approver.py \
  echo-text.py \
  phoenix.py  \
  util.py \
  echo-call-info.xml

libexec_PROGRAMS = phoenix-authenticator phoenix-echo-call

phoenix_authenticator_SOURCES = authenticator.c
phoenix_authenticator_CFLAGS = @GLIB_CFLAGS@ @TP_GLIB_CFLAGS@
phoenix_authenticator_LDFLAGS = @GLIB_LIBS@ @TP_GLIB_LIBS@

phoenix_echo_call_SOURCES = echo-call.c \
    echo-call-info-dbus.c echo-call-info-dbus.h
phoenix_echo_call_CFLAGS = @GLIB_CFLAGS@ @TP_GLIB_CFLAGS@ \
                               @TP_FARSTREAM_CFLAGS@
phoenix_echo_call_LDFLAGS = @GLIB_LIBS@ @TP_GLIB_LIBS@ \
                               @TP_FARSTREAM_LIBS@
