U_DBUS=uninstalled/dbus-1/services

EXTRA_DIST = \
  dbus-services/Phoenix.Approver.service.in \
  dbus-services/Phoenix.Authenticator.service.in \
  dbus-services/Phoenix.EchoCall.service.in \
  dbus-services/Phoenix.EchoText.service.in \
  telepathy-clients/Phoenix.Approver.client \
  telepathy-clients/Phoenix.Authenticator.client \
  telepathy-clients/Phoenix.EchoCall.client \
  telepathy-clients/Phoenix.EchoText.client

service_files = \
  org.freedesktop.Telepathy.Client.Phoenix.EchoCall.service \
  org.freedesktop.Telepathy.Client.Phoenix.EchoText.service \
  org.freedesktop.Telepathy.Client.Phoenix.Approver.service \
  org.freedesktop.Telepathy.Client.Phoenix.Authenticator.service

uninstalled_service_files = \
  $(U_DBUS)/org.freedesktop.Telepathy.Client.Phoenix.EchoCall.service \
  $(U_DBUS)/org.freedesktop.Telepathy.Client.Phoenix.EchoText.service \
  $(U_DBUS)/org.freedesktop.Telepathy.Client.Phoenix.Approver.service \
  $(U_DBUS)/org.freedesktop.Telepathy.Client.Phoenix.Authenticator.service

client_files = \
  telepathy-clients/Phoenix.EchoCall.client \
  telepathy-clients/Phoenix.EchoText.client \
  telepathy-clients/Phoenix.Approver.client \
  telepathy-clients/Phoenix.Authenticator.client

uninstalled_client_files = \
  uninstalled/telepathy/clients/Phoenix.EchoCall.client \
  uninstalled/telepathy/clients/Phoenix.EchoText.client \
  uninstalled/telepathy/clients/Phoenix.Approver.client \
  uninstalled/telepathy/clients/Phoenix.Authenticator.client

$(U_DBUS)/org.freedesktop.Telepathy.Client.%.service: dbus-services/%.service.in
	$(MKDIR_P) $(U_DBUS)
	$(AM_V_GEN)sed -e "s|[@]PATH[@]|@abs_top_builddir@/src|g" $< > $@

uninstalled/telepathy/clients/%.client: telepathy-clients/%.client
	$(MKDIR_P) uninstalled/telepathy/clients
	cp $< $@

org.freedesktop.Telepathy.Client.%.service: dbus-services/%.service.in
	$(AM_V_GEN)sed -e "s|[@]PATH[@]|$(libexecdir)|g" $< > $@


xdgdatadir = $(pkgdatadir)/data
dbusservicesdir = $(xdgdatadir)/dbus-1/services
dbusservices_DATA = $(service_files)
tpclientsdir = $(xdgdatadir)/telepathy/clients
tpclients_DATA = $(client_files)

BUILT_SOURCES=$(uninstalled_service_files) $(uninstalled_client_files)
CLEANFILES = $(BUILT_SOURCES) $(service_files)
