AC_PREREQ([2.59])
AC_INIT([telepathy-phoenix], [0.0.1],
        [https://bugs.freedesktop.org/enter_bug.cgi?product=Telepathy&component=phoenix])

AC_CONFIG_MACRO_DIR([m4])

AM_PROG_LIBTOOL
AM_INIT_AUTOMAKE([1.11 -Wno-portability])
AM_CONFIG_HEADER(config.h)


dnl use pretty build output with automake >= 1.11
m4_ifdef([AM_SILENT_RULES],[AM_SILENT_RULES([yes])],
  [AM_DEFAULT_VERBOSITY=1
   AC_SUBST(AM_DEFAULT_VERBOSITY)])

dnl check for tools
AC_PROG_CC
AC_PROG_CC_STDC
AC_PROG_INSTALL

dnl decide error flags
AS_COMPILER_FLAG(-Wall, ERROR_CFLAGS="-Wall", ERROR_CFLAGS="")
AS_COMPILER_FLAG(-Werror -Wno-error=deprecated-declarations, werror=yes, werror=no)

AC_ARG_ENABLE(Werror,
  AC_HELP_STRING([--disable-Werror],[compile without -Werror (normally enabled in development builds)]),
    werror=$enableval, :)

AS_COMPILER_FLAG(-Wextra, wextra=yes, wextra=no)
AS_COMPILER_FLAG(-Wno-missing-field-initializers,
        wno_missing_field_initializers=yes,
        wno_missing_field_initializers=no)
AS_COMPILER_FLAG(-Wno-unused-parameter,
        wno_unused_parameter=yes,
        wno_unused_parameter=no)

dnl Check for Glib and friends
PKG_CHECK_MODULES(GLIB, gobject-2.0 >= 2.30 glib-2.0 >= 2.30
  gio-2.0 gio-unix-2.0)
AC_DEFINE(GLIB_VERSION_MIN_REQUIRED, GLIB_VERSION_2_30, [Ignore post 2.30 deprecations])
AC_DEFINE(GLIB_VERSION_MAX_ALLOWED, GLIB_VERSION_2_30, [Prevent post 2.30 APIs])

AC_SUBST(GLIB_CFLAGS)
AC_SUBST(GLIB_LIBS)

dnl Check for Telepathy libraries
PKG_CHECK_MODULES([TP_GLIB], [telepathy-glib >= 0.17.5])

AC_SUBST(TP_GLIB_CFLAGS)
AC_SUBST(TP_GLIB_LIBS)

dnl Check for farstream
PKG_CHECK_MODULES(TP_FARSTREAM, [telepathy-farstream >= 0.1.0])

AC_SUBST(TP_FARSTREAM_CFLAGS)
AC_SUBST(TP_FARSTREAM_LIBS)

dnl Always required to generate extensions
AM_PATH_PYTHON([2.5])

AC_OUTPUT( Makefile \
          m4/Makefile \
          src/Makefile \
          data/Makefile \
          tools/Makefile \
)
