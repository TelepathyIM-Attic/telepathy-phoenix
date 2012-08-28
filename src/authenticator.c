/*
 * phoenix-authenticator.c
 * Copyright (C) 2011 Collabora Ltd.
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 2.1 of the License, or (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public
 * License along with this library; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */

#include <stdio.h>
#include <string.h>
#include <telepathy-glib/telepathy-glib.h>

static void
sasl_status_changed_cb (TpChannel *channel,
  TpSASLStatus status,
  const gchar *error,
  GHashTable *details,
  gpointer user_data,
  GObject *weak_object)
{
  printf ("New sasl status: %d\n", status);
  switch (status) {
    case TP_SASL_STATUS_SERVER_SUCCEEDED:
      tp_cli_channel_interface_sasl_authentication_call_accept_sasl (
        channel, -1, NULL, NULL, NULL, NULL);
      break;
    case TP_SASL_STATUS_SUCCEEDED:
    case TP_SASL_STATUS_SERVER_FAILED:
      tp_cli_channel_call_close (channel, -1, NULL, NULL, NULL, NULL);
      break;
    default:
      break;
  }
}


static void
password_provided_cb (TpChannel *channel,
  const GError *error,
  gpointer user_data,
  GObject *weak_data)
{
  if (error != NULL)
    {
      printf ("Failed to start mechanism: %s\n", error->message);
      return;
    }

    printf ("Started mechanism successfully\n");
}

static void
provide_password (TpChannel *channel, const gchar *password)
{
  GArray *array = g_array_sized_new (TRUE, FALSE,
    sizeof (gchar), strlen (password));

  g_array_append_vals (array, password, strlen (password));

  tp_cli_channel_interface_sasl_authentication_call_start_mechanism_with_data (
        channel, -1, "X-TELEPATHY-PASSWORD", array,
        password_provided_cb, NULL, NULL, NULL);

  g_array_unref (array);
}


static void
handle_channels_cb (TpSimpleHandler *handler,
  TpAccount *account,
  TpConnection *connection,
  GList *channels,
  GList *request_satisfied,
  gint64 user_aciton_time,
  TpHandleChannelsContext *handler_context,
  gpointer user_data)
{
  TpChannel *channel = channels->data;
  gchar *path = g_build_filename (
    g_get_user_config_dir (),
    "phoenix",
    "auth",
    NULL);
  GFile *file = g_file_new_for_path (path);
  GFileIOStream *stream;
  GDataInputStream *input = NULL;
  char *password = NULL;
  char *line;

  if (g_list_length (channels) != 1)
    {
      GError err = { TP_ERROR, TP_ERROR_INVALID_ARGUMENT,
        "Can only handle one channel at a time" };
      tp_handle_channels_context_fail (handler_context,
        &err);
      goto out;
    }

  stream = g_file_open_readwrite (file, NULL, NULL);

  if (stream == NULL)
    {
      GError err = { TP_ERROR, TP_ERROR_INVALID_ARGUMENT,
        "No authenication data stored" };
      tp_handle_channels_context_fail (handler_context,
        &err);
      goto out;
    }

  input = g_data_input_stream_new (
    g_io_stream_get_input_stream (G_IO_STREAM (stream)));
  while ((line = g_data_input_stream_read_line_utf8 (input, NULL, NULL, NULL))
      != NULL)
    {
      gchar **r = g_strsplit (line, " ", 2);
      if (r[0] == NULL || r[1] == NULL)
        continue;

      if (!tp_strdiff (r[0], tp_account_get_path_suffix (account)))
        {
          password = g_strdup (r[1]);
          printf ("Found password: %s\n", password);
          g_strfreev(r);
          break;
        }
      g_strfreev(r);
    }
  g_object_unref (input);

  if (password == NULL)
    {
      GError err = { TP_ERROR, TP_ERROR_INVALID_ARGUMENT,
        "No authenication data stored for this account" };
      tp_handle_channels_context_fail (handler_context,
        &err);
      goto out;
    }

  tp_handle_channels_context_accept (handler_context);

  tp_cli_channel_interface_sasl_authentication_connect_to_sasl_status_changed
    (channel, sasl_status_changed_cb, NULL, NULL, NULL, NULL);
  provide_password (channel, password);

out:
  g_free (path);
  g_free (password);
}

int
main (int argc, char **argv)
{
  TpBaseClient *client;
  TpAccountManager *am;
  GMainLoop *loop;

  g_type_init ();

  loop = g_main_loop_new (NULL, FALSE);

  am = tp_account_manager_dup ();

  client = tp_simple_handler_new_with_am (am,
    FALSE,
    FALSE,
    "Phoenix.Authenticator",
    FALSE,
    handle_channels_cb,
    NULL,
    NULL);

  tp_base_client_take_handler_filter (client,
    tp_asv_new (
       TP_PROP_CHANNEL_CHANNEL_TYPE, G_TYPE_STRING,
          TP_IFACE_CHANNEL_TYPE_SERVER_AUTHENTICATION,
        TP_PROP_CHANNEL_TYPE_SERVER_AUTHENTICATION_AUTHENTICATION_METHOD,
          G_TYPE_STRING,
          TP_IFACE_CHANNEL_INTERFACE_SASL_AUTHENTICATION,
       NULL));

  tp_base_client_register (client, NULL);

  g_main_loop_run (loop);

  g_object_unref (am);
  g_object_unref (client);
  g_main_loop_unref (loop);

  return 0;
}
