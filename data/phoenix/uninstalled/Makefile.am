service_files = \
  dbus-1/services/org.freedesktop.Telepathy.Client.Phoenix.EchoText.service \
  dbus-1/services/org.freedesktop.Telepathy.Client.Phoenix.Approver.service \
  dbus-1/services/org.freedesktop.Telepathy.Client.Phoenix.Authenticator.service
client_files = \
  telepathy/clients/Phoenix.EchoText.client \
  telepathy/clients/Phoenix.Approver.client \
  telepathy/clients/Phoenix.Authenticator.client

dbus-1/services/org.freedesktop.Telepathy.Client.%.service: dbus-1/services/%.service.in
	$(MKDIR_P) dbus-1/services
	$(AM_V_GEN)sed -e "s|[@]abs_top_builddir[@]|@abs_top_builddir@|g" $< > $@

telepathy/clients/%.client: telepathy/clients/%.client.in
	$(MKDIR_P) telepathy/clients
	$(AM_V_GEN)sed -e "s|[@]abs_top_builddir[@]|@abs_top_builddir@|g" $< > $@


BUILT_SOURCES=$(service_files) $(client_files)
CLEANFILES = $(BUILT_SOURCES)
