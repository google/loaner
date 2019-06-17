<html lang="en">

# Grab n Go API

## Getting Started with the GnG API

This documentation explains how to get started with the GnG API.

### API Authentication

The GnG API is authenticated based on user roles and permissions. Roles are
managed by Google groups that are synced with a Cron job.

### **Permission Containers**

There are two roles built into the app by default:

*   **User**
    *   Any person who interacts with the application is considered a user.
        Users do not have access to any administrative views and can only
        view/interact with their own loans.
*   **Super Admin**
    *   A person that is in charge of configuring the application and
        experience. This role has all permissions by default and thus
        the ability to perform all of the actions within the application.

Additional roles can be created by using the Roles API. Each role can be given
zero or more permissions and associated with a group to automatically add users
to the given role. Some example roles you may want to create are a technician
role that can audit shelves and other inventory-related tasks or a helpdesk role
that can assist users with their loans.

### Authentication Decorator

Authentication for each API call is managed with a decorator, which can restrict
an api method based on the optional argument `permission`. If a permission is
set on an API the calling user must belong to a role that has that permission
in order to use it. If no permission is provided any user of the app can call
that api method.

#### Usage

```python
 # configuration of an endpoints method with enforced user auth check only.
@loaner_endpoints.authed_method(
    chrome_message.ChromeRequest,
    chrome_message.ChromeResponse,
    name='heartbeat',
    path='heartbeat',
    http_method='GET',
    user_auth_only=True)
def do_something(self, request):
    ...

# The above method will execute if the current user is authenticated properly.

 # configuration of an endpoints method with enforced permission.
@loaner_endpoints.authed_method(
    chrome_message.ChromeRequest,
    chrome_message.ChromeResponse,
    name='heartbeat',
    path='heartbeat',
    http_method='GET',
    permission='view')
def do_something(self, request):
    ...

# The above method will only execute if the current user's role has the permission
# "view".
```

## Prepare for Authentication

### Set up Google Groups

User's roles are managed using Google Groups. Before setting up the application
you will need to create a Google group that contains one or more super admins
(including the user setting up the application). Any other roles you create can
also be synced to groups so you don't need to manually update them.

### Set Administrative Group in constants.py File

1.  Go to the root of the source code and search for a file named
    `constants.py`.

1.  Use your favorite editor to open the file and add the superadmin group that
    you created earlier. For example:

    ```python
    # superadmins_group: str, The name of the Google Group that governs who is
    # a superadmin. Superadmins have all permissions by default.
    SUPERADMINS_GROUP = 'technical-admins@example.com'
    ```

## API List

  <!--- Used HTML for the tables because GitHub-flavored MD Markup doesn't allow for merging of rows within tables. Tables won't render properly without HTML. *-->

### Bootstrap_api

The entry point for the Bootstrap methods.

#### Methods

`get_status` Gets general bootstrap status, and task status if not yet
completed:

<table>
   <tbody>
      <tr>
         <th align="center">Requests</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>message_types.VoidMessage</td>
         <td>None</td>
      </tr>
   </tbody>
</table>

<table>
   <tbody>
      <tr>
         <th align="center">Returns</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>GetStatusResponse: Bootstrap status response ProtoRPC</td>
         <td>enabled: bool, indicates if the bootstrap is enabled.</td>
      <tr>
         <td></td>
         <td>started: bool, indicated if the bootstrap has been started.</td>
      <tr>
         <td></td>
         <td>completed: bool, indicated if the bootstrap is completed.</td>
      <tr>
         <td></td>
         <td> tasks: BootstrapTask, A list of all of the tasks to be displayed.</td>
   </tbody>
</table>

<br>

`run` Runs request for the Bootstrap API:

<table>
   <tbody>
      <tr>
         <th align="center">Requests</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>RunRequest: Bootstrap request ProtoRPC message</td>
         <td>requested_tasks: BootstrapTask, A list of the requested tasks.</td>
      </tr>
   </tbody>
</table>

<table>
   <tbody>
      <tr>
         <th align="center">Returns</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>message_types.VoidMessage</td>
         <td>None</td>
      </tr>
   </tbody>
</table>

<br>

### Chrome_api

The entry point for the GnG Loaners Chrome App.

#### Methods

`heartbeat`Heartbeat check-in for Chrome devices:

<table>
   <tbody>
      <tr>
         <th align="center">Requests</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>HeartbeatRequest: Heartbeat Request ProtoRPC message.</td>
         <td>device_id: str, The unique Chrome device ID of the Chrome device.</td>
      </tr>
   </tbody>
</table>

<table>
   <tbody>
      <tr>
         <th align="center">Returns</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>HeartbeatResponse: Heartbeat Response ProtoRPC message.</td>
         <td>is_enrolled: bool, Determine if the device is enrolled.</td>
      </tr>
      <tr>
         <td></td>
         <td>start_assignment: bool, Determine if assignment workflow should be started.</td>
   </tbody>
</table>

<br>

### Configuration_api

Lists the given setting's value.

#### Methods

`get` Lists the given setting's value:

<table>
   <tbody>
      <tr>
         <th align="center">Requests</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>GetConfigurationRequest request for ProtoRPC message.</td>
         <td>setting: str, The name of the setting being requested.</td>
      </tr>
      <tr>
         <td></td>
         <td>configuration_type: ConfigurationType, the type of configuration to request for.</td>
   </tbody>
</table>

<table>
   <tbody>
      <tr>
         <th align="center">Returns</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>ConfigurationResponse response for ProtoRPC message. </td>
         <td>setting: str, The name of the setting being returned.</td>
      </tr>
      <tr>
         <td></td>
         <td>string_value: str, The string value of the setting.</td>
      <tr>
         <td></td>
         <td>integer_value: int, The integer value of the setting.</td>
      <tr>
         <td></td>
         <td>boolean_value: bool, The boolean value of the setting.</td>
      <tr>
         <td></td>
         <td>list_value: list, The list value of the setting.</td>
   </tbody>
</table>

<br>

`list` Get a list of all configuration values.

<table>
   <tbody>
      <tr>
         <th align="center">Requests</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>message_types.VoidMessage</td>
         <td>None</td>
      </tr>
   </tbody>
</table>

<table>
   <tbody>
      <tr>
         <th align="center">Returns</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>ListConfigurationsResponse response for ProtoRPC message.</td>
         <td>settings: ConfigurationResponse, The setting and corresponding value being returned.</td>
      </tr>
   </tbody>
</table>

<br>

`update` Updates a given settings value.

<table>
   <tbody>
      <tr>
         <th align="center">Requests</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>UpdateConfigurationRequest request for ProtoRPC message.</td>
         <td>setting: str, The name of the setting being requested.</td>
      </tr>
      <tr>
         <td></td>
         <td>configuration_type: ConfigurationType, The type of configuration to request for.</td>
      <tr>
         <td></td>
         <td>string_value: str, The string value of the setting being updated.</td>
      <tr>
         <td></td>
         <td>integer_value: int, The integer value ff the setting being updated.</td>
      <tr>
         <td></td>
         <td>boolean_value: bool, The boolean value of the setting being updated.</td>
      <tr>
         <td></td>
         <td>list_value: list, The list value of the setting being updated.</td>

   </tbody>
</table>

<table>
   <tbody>
      <tr>
         <th align="center">Returns</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>message_types.VoidMessage</td>
         <td>None</td>
      </tr>
   </tbody>
</table>

<br>

### Datastore_api

The entry point for the Datastore methods.

#### Methods

`import` Datastore import request for the Datastore API.

<table>
   <tbody>
      <tr>
         <th align="center">Requests</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>Datastore YAML Import Request ProtoRPC message.</td>
         <td>yaml: str, The name of the YAML being imported.</td>
      </tr>
   </tbody>
</table>

<table>
   <tbody>
      <tr>
         <th align="center">Returns</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>message_types.VoidMessage.</td>
         <td>None</td>
      </tr>
   </tbody>
</table>

<br>

### Device_api

API endpoint that handles requests related to Devices.

#### Methods

`auditable` If a device is able to be audited for shelf audits. Returns an error
if the device cannot be moved to the shelf for any reason.

<table>
   <tbody>
      <tr>
         <th align="center">Requests</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>General Device request ProtoRPC message with several identifiers. Only one identifier needs to be provided.</td>
         <td>asset_tag: str, The asset tag of the Chrome device.</td>
      </tr>
      <tr>
         <td></td>
         <td>chrome_device_id: str, The Chrome device id of the Chrome device.</td>
      <tr>
         <td></td>
         <td>serial_number: str, The serial number of the Chrome device.</td>
      <tr>
         <td></td>
         <td>urlkey: str, The URL-safe key of a device.</td>
      <tr>
         <td></td>
         <td>unknown_identifier: str, Either an asset tag or serial number of the device.</td>
   </tbody>
</table>

<table>
   <tbody>
      <tr>
         <th align="center">Returns</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>message_types.VoidMessage</td>
         <td>None</td>
      </tr>
   </tbody>
</table>

<br>

`enable_guest_mode` Enables Guest Mode for a given device.

<table>
   <tbody>
      <tr>
         <th align="center">Requests</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>RunRequest: Bootstrap request ProtoRPC message</td>
         <td>requested_tasks: BootstrapTask, A list of the requested tasks.</td>
      </tr>
   </tbody>
</table>

<table>
   <tbody>
      <tr>
         <th align="center">Requests</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>General Device request ProtoRPC message with several identifiers. Only one identifier needs to be provided.</td>
         <td>asset_tag: str, The asset tag of the Chrome device.</td>
      </tr>
      <tr>
         <td></td>
         <td>chrome_device_id: str, The Chrome device id of the Chrome device.</td>
      <tr>
         <td></td>
         <td>serial_number: str, The serial number of the Chrome device.</td>
      <tr>
         <td></td>
         <td>urlkey: str, The URL-safe key of a device.</td>
      <tr>
         <td></td>
         <td>unknown_identifier: str, Either an asset tag or serial number of the device.</td>
   </tbody>
</table>

<table>
   <tbody>
      <tr>
         <th align="center">Returns</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>message_types.VoidMessage</td>
         <td>None</td>
      </tr>
   </tbody>
</table>

<br>

`enroll` Enrolls a device in the program

<table>
   <tbody>
      <tr>
         <th align="center">Requests</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>General Device request ProtoRPC message with several identifiers. Only one identifier needs to be provided.</td>
         <td>asset_tag: str, The asset tag of the Chrome device.</td>
      </tr>
      <tr>
         <td></td>
         <td>chrome_device_id: str, The Chrome device id of the Chrome device.</td>
      <tr>
         <td></td>
         <td>serial_number: str, The serial number of the Chrome device.</td>
      <tr>
         <td></td>
         <td>urlkey: str, The URL-safe key of a device.</td>
      <tr>
         <td></td>
         <td>unknown_identifier: str, Either an asset tag or serial number of the device.</td>
   </tbody>
</table>

<table>
   <tbody>
      <tr>
         <th align="center">Returns</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>message_types.VoidMessage</td>
         <td>None</td>
      </tr>
   </tbody>
</table>

<br>

`extend_loan` Extend the current loan for a given Chrome device.

<table>
   <tbody>
      <tr>
         <th align="center">Requests</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>Loan extension request ProtoRPC message.</td>
         <td>device: DeviceRequest, A device to be fetched.</td>
      </tr>
      <tr>
         <td></td>
         <td>extend_date: datetime, The date to extend the loan for.</tr>
   </tbody>
</table>

<table>
   <tbody>
      <tr>
         <th align="center">Returns</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>message_types.VoidMessage</td>
         <td>None</td>
      </tr>
   </tbody>
</table>

<br>

`get` Gets a device using any identifier in device_message.DeviceRequest.

<table>
   <tbody>
      <tr>
         <th align="center">Requests</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>General Device request ProtoRPC message with several identifiers. Only one identifier needs to be provided.</td>
         <td>asset_tag: str, The asset tag of the Chrome device.</td>
      </tr>
      <tr>
         <td></td>
         <td>chrome_device_id: str, The Chrome device id of the Chrome device.</td>
      <tr>
         <td></td>
         <td>serial_number: str, The serial number of the Chrome device.</td>
      <tr>
         <td></td>
         <td>urlkey: str, The URL-safe key of a device.</td>
      <tr>
         <td></td>
         <td>unknown_identifier: str, Either an asset tag or serial number of the device.</td>
   </tbody>
</table>

<table>
   <tbody>
      <tr>
         <th align="center">Returns</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>message_types.VoidMessage</td>
         <td>None</td>
      </tr>
   </tbody>
</table>

<br>

`list` Lists all devices based on any device attribute.

<table>
   <tbody>
      <tr>
         <th align="center">Requests</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>Device ProtoRPC message.</td>
         <td>serial_number: str, The serial number of the Chrome device.</td>
      </tr>
      <tr>
         <td></td>
         <td>asset_tag: str, The asset tag of the Chrome device.</td>
       <tr>
         <td>enrolled: bool, Indicates the enrollment status of the device.</td>
          <td></td>
       <tr>
         <td></td>
          <td>device_model: int, Identifies the model name of the device.</td>
       <tr>
         <td></td>
         <td>due_date: datetime, The date that device is due for return.</td>
       <tr>
         <td></td>
         <td>last_know_healthy: datetime, The date to indicate the last known healthy status.</td>
       <tr>
         <td></td>
         <td>shelf: shelf_messages. Shelf, The shelf the device is placed on.</td>
       <tr>
          <td></td>
          <td>assigned_user: str, The email of the user who is assigned to the device.</td>
       <tr>
          <td></td>
          <td>assignment_date: datetime, The date the device was assigned to a user.</td>
       <tr>
          <td></td>
          <td>current_ou: str, The current organizational unit the device belongs to.</td>
       <tr>
          <td></td>
          <td>ou_change_date: datetime, The date the organizational unit was changed.</td>
       <tr>
          <td></td>
          <td>locked: bool, Indicates whether or not the device is locked.</td>
       <tr>
          <td></td>
          <td>lost: bool, Indicates whether or not the device is lost.</td>
       <tr>
          <td></td>
          <td>mark_pending_return_date: datetime, The date a user marked device returned.</td>
       <tr>
          <td></td>
          <td>chrome_device_id: str, A unique device ID.</td>
       <tr>
          <td></td>
          <td>last_heartbeat: datetime, The date of the last time the device checked in.</td>
       <tr>
          <td></td>
          <td>damaged: bool, Indicates the if the device is damaged.</td>
       <tr>
          <td></td>
          <td>damaged_reason: str, A string denoting the reason for being reported as damaged.</td>
       <tr>
          <td></td>
          <td>last_reminder: Reminder, Level, time, and count of the last reminder the device had.</td>
       <tr>
          <td></td>
          <td>next_reminder: Reminder, Level, time, and count of the next reminder.</td>
       <tr>
          <td></td>
          <td>page_size: int, The number of results to query for and display.</td>
       <tr>
          <td></td>
          <td>page_token: str, A page token to query next page results.</td>
       <tr>
          <td></td>
          <td>max_extend_date: datetime, Indicates maximum extend date a device can have.</td>
       <tr>
          <td></td>
          <td>guest_enabled: bool, Indicates if guest mode has been already enabled.</td>
       <tr>
          <td></td>
          <td>guest_permitted: bool, Indicates if guest mode has been allowed.</td>
       <tr>
          <td></td>
          <td>give_name: str, The given name of the user.</td>
       <tr>
          <td></td>
          <td>query: shared_message.SearchRequest, a message containing query options to conduct a search on an index.</td>
   </tbody>
</table>

<table>
   <tbody>
      <tr>
         <th align="center">Returns</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>List device response ProtoRPC message.</td>
         <td>devices: Device, A device to display.</td>
      </tr>
      <tr>
         <td></td>
         <td>has_additional_results: bool, If there are more results to be displayed.</td>
      <tr>
         <td></td>
         <td>page_token: str, A page token that will allow be used to query for additional results.</td>
   </tbody>
</table>

<br>

`mark_damaged` Mark that a device is damaged.

<table>
   <tbody>
      <tr>
         <th align="center">Returns</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>Damaged device ProtoRPC message.</td>
         <td>device: DeviceRequest, A device to be fetched.</td>
      </tr>
      <tr>
         <td></td>
         <td>damaged_reason: str, The reason the device is being reported as damaged.</td>
   </tbody>
</table>

<table>
   <tbody>
      <tr>
         <th align="center">Returns</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>message_types.VoidMessage</td>
         <td>None</td>
      </tr>
   </tbody>
</table>

<br>

`mark_lost` Mark that a device is lost.

<table>
   <tbody>
      <tr>
         <th align="center">Requests</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>General Device request ProtoRPC message with several identifiers. Only one identifier needs to be provided.</td>
         <td>asset_tag: str, The asset tag of the Chrome device.</td>
      </tr>
      <tr>
         <td></td>
         <td>chrome_device_id: str, The Chrome device id of the Chrome device.</td>
      <tr>
         <td></td>
         <td>serial_number: str, The serial number of the Chrome device.</td>
      <tr>
         <td></td>
         <td>urlkey: str, The URL-safe key of a device.</td>
      <tr>
         <td></td>
         <td>unknown_identifier: str, Either an asset tag or serial number of the device.</td>
   </tbody>
</table>

<table>
   <tbody>
      <tr>
         <th align="center">Returns</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>message_types.VoidMessage</td>
         <td>None</td>
      </tr>
   </tbody>
</table>

<br>

`mark_pending_return` Mark that a device is pending return.

<table>
   <tbody>
      <tr>
         <th align="center">Requests</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>General Device request ProtoRPC message with several identifiers. Only one identifier needs to be provided.</td>
         <td>asset_tag: str, The asset tag of the Chrome device.</td>
      </tr>
      <tr>
         <td></td>
         <td>chrome_device_id: str, The Chrome device id of the Chrome device.</td>
      <tr>
         <td></td>
         <td>serial_number: str, The serial number of the Chrome device.</td>
      <tr>
         <td></td>
         <td>urlkey: str, The URL-safe key of a device.</td>
      <tr>
         <td></td>
         <td>unknown_identifier: str, Either an asset tag or serial number of the device.</td>
   </tbody>
</table>

<table>
   <tbody>
      <tr>
         <th align="center">Returns</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>message_types.VoidMessage</td>
         <td>None</td>
      </tr>
   </tbody>
</table>

<br>

`resume_loan` Manually resume a loan that was paused because the device was
marked pending_return.

<table>
   <tbody>
      <tr>
         <th align="center">Requests</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>General Device request ProtoRPC message with several identifiers. Only one identifier needs to be provided.</td>
         <td>asset_tag: str, The asset tag of the Chrome device.</td>
      </tr>
      <tr>
         <td></td>
         <td>chrome_device_id: str, The Chrome device id of the Chrome device.</td>
      <tr>
         <td></td>
         <td>serial_number: str, The serial number of the Chrome device.</td>
      <tr>
         <td></td>
         <td>urlkey: str, The URL-safe key of a device.</td>
      <tr>
         <td></td>
         <td>unknown_identifier: str, Either an asset tag or serial number of the device.</td>
   </tbody>
</table>

<table>
   <tbody>
      <tr>
         <th align="center">Returns</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>message_types.VoidMessage</td>
         <td>None</td>
      </tr>
   </tbody>
</table>

<br>

`unenroll` Unenrolls a device from the program.

<table>
   <tbody>
      <tr>
         <th align="center">Requests</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>General Device request ProtoRPC message with several identifiers. Only one identifier needs to be provided.</td>
         <td>asset_tag: str, The asset tag of the Chrome device.</td>
      </tr>
      <tr>
         <td></td>
         <td>chrome_device_id: str, The Chrome device id of the Chrome device.</td>
      <tr>
         <td></td>
         <td>serial_number: str, The serial number of the Chrome device.</td>
      <tr>
         <td></td>
         <td>urlkey: str, The URL-safe key of a device.</td>
      <tr>
         <td></td>
         <td>unknown_identifier: str, Either an asset tag or serial number of the device.</td>
   </tbody>
</table>

<table>
   <tbody>
      <tr>
         <th align="center">Returns</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>message_types.VoidMessage</td>
         <td>None</td>
      </tr>
   </tbody>
</table>

<br>

`user_devices` Lists the devices assigned to the currently logged in user.

<table>
   <tbody>
      <tr>
         <th align="center">Returns</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>message_types.VoidMessage</td>
         <td>None</td>
      </tr>
   </tbody>
</table>

<table>
   <tbody>
      <tr>
         <th align="center">Returns</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>List device response ProtoRPC message.</td>
         <td>devices: Device, A device to display.</td>
      </tr>
      <tr>
         <td></td>
         <td>has_additional_results: bool, If there are more results to be displayed.</td>
      <tr>
         <td></td>
         <td>page_token: str, A page token that will allow be used to query for additional results.</td>
   </tbody>
</table>

<br>

### Roles_api

API endpoint that handles requests related to user roles.

#### Methods

`create` Create a new role.

<table>
   <tbody>
      <tr>
         <th align="center">Requests</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>user_messages.Role</td>
         <td>name: str, the name of the role.</td>
      </tr>
      <tr>
         <td></td>
         <td>permissions: list of str, zero or more permissions to add to the role.</td>
      <tr>
         <td></td>
         <td>associated_group: str, optional group to associate to the role for automatic sync.</td>
   </tbody>
</table>

<table>
   <tbody>
      <tr>
         <th align="center">Returns</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>message_types.VoidMessage</td>
         <td>None</td>
      </tr>
   </tbody>
</table>

<br>

`get` Get a specific role by name.

<table>
   <tbody>
      <tr>
         <th align="center">Requests</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>user_messages.GetRoleRequest</td>
         <td>name: str, the name of the role.</td>
      </tr>
   </tbody>
</table>

<table>
   <tbody>
      <tr>
         <th align="center">Returns</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>user_messages.Role</td>
         <td>name: str, the name of the role.</td>
      </tr>
      <tr>
         <td></td>
         <td>permissions: list of str, zero or more permissions associated with the role.</td>
      <tr>
         <td></td>
         <td>associated_group: str, optional group associated to the role for automatic sync.</td>

   </tbody>
</table>

<br>

`update` Updates a role's permissions or associated group. Role names cannot be
changed once set.

<table>
   <tbody>
      <tr>
         <th align="center">Requests</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>user_messages.Role</td>
         <td>name: str, the name of the role.</td>
      </tr>
      <tr>
         <td></td>
         <td>permissions: list of str, zero or more permissions to add to the role.</td>
      <tr>
         <td></td>
         <td>associated_group: str, optional group to associate to the role for automatic sync.</td>
   </tbody>
</table>

<table>
   <tbody>
      <tr>
         <th align="center">Returns</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>message_types.VoidMessage</td>
         <td>None</td>
      </tr>
   </tbody>
</table>

<br>

### Search_api

API endpoint that handles requests related to search.

#### Methods

`clear` Clear the index for a given model (Device or Shelf).

<table>
   <tbody>
      <tr>
         <th align="center">Requests</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>search_messages.SearchMessage</td>
         <td>model: enum, the model to clear the index of (Device or Shelf).</td>
      </tr>
   </tbody>
</table>

<table>
   <tbody>
      <tr>
         <th align="center">Returns</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>message_types.VoidMessage</td>
         <td>None</td>
      </tr>
   </tbody>
</table>

<br>

`reindex` Reindex the entities for a given model (Device or Shelf).

<table>
   <tbody>
      <tr>
         <th align="center">Requests</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>search_messages.SearchMessage</td>
         <td>model: enum, the model to clear the index of (Device or Shelf).</td>
      </tr>
   </tbody>
</table>

<table>
   <tbody>
      <tr>
         <th align="center">Returns</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>message_types.VoidMessage</td>
         <td>None</td>
      </tr>
   </tbody>
</table>

<br>

### Shelf_api

The entry point for the Shelf methods.

#### Methods

`audit` Performs an audit on a shelf based on location.

<table>
   <tbody>
      <tr>
         <th align="center">Requests</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>ShelfAuditRequest ProtoRPC message.</td>
         <td>shelf_request: ShelfRequest, A message containing the unique identifiers to be used when retrieving a shelf.</td>
      </tr>
      <tr>
         <td></td>
         <td>device_identifiers: list, A list of device serial numbers to perform a device audit on.</td>
   </tbody>
</table>

<table>
   <tbody>
      <tr>
         <th align="center">Returns</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>message_types.VoidMessage</td>
         <td>None</td>
      </tr>
   </tbody>
</table>

<br>

`disable` Disable a shelf by its location.

<table>
   <tbody>
      <tr>
         <th align="center">Requests</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>ShelfRequest</td>
         <td>location: str, The location of the shelf.</td>
      </tr>
      <tr>
         <td></td>
         <td>urlsafe_key: str, The urlsafe representation of a ndb.Key.</td>
   </tbody>
</table>

<table>
   <tbody>
      <tr>
         <th align="center">Returns</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>message_types.VoidMessage</td>
         <td>None</td>
      </tr>
   </tbody>
</table>

<br>

`enroll` Enroll request for the Shelf API.

<table>
   <tbody>
      <tr>
         <th align="center">Requests</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>EnrollShelfRequest ProtoRPC message.</td>
         <td>friendly_name: str, The friendly name of the shelf.</td>
      </tr>
      <tr>
         <td></td>
         <td>location: str, The location of the shelf.</td>
      <tr>
         <td></td>
         <td>latitude: float, A geographical point represented by floating-point.</td>
      <tr>
         <td></td>
         <td>latitude: float, A geographical point represented by floating-point.</td>
      <tr>
         <td></td>
         <td>longitude: float, A geographical point represented by floating-point.</td>
      <tr>
         <td></td>
         <td>altitude: float, Indicates the floor.</td>
      <tr>
         <td></td>
         <td>capacity: int, The amount of devices a shelf can hold.</td>
      <tr>
         <td></td>
         <td>audit_notification_enabled: bool, Indicates if an audit is enabled for the shelf.</td>
      <tr>
         <td></td>
         <td>responsible_for_audit: str, The party responsible for audits.</td>
   </tbody>
</table>

<table>
   <tbody>
      <tr>
         <th align="center">Returns</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>message_types.VoidMessage</td>
         <td>None</td>
      </tr>
   </tbody>
</table>

<br>

`get` Get a shelf based on location.

<table>
   <tbody>
      <tr>
         <th align="center">Requests</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>ShelfRequest</td>
         <td>location: str, The location of the shelf.</td>
      </tr>
      <tr>
         <td></td>
         <td>urlsafe_key: str, The urlsafe representation of a ndb.Key.</td>
   </tbody>
</table>

<table>
   <tbody>
      <tr>
         <th align="center">Returns</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>Shelf ProtoRPC message</td>
         <td>enabled: bool, Indicates if the shelf is enabled or not.</td>
      </tr>
         <td></td>
         <td>friendly_name: str, The friendly name of the shelf.</td>
      <tr>
         <td></td>
         <td>location: str, The location of the shelf.</td>
      <tr>
         <td></td>
         <td>latitude: float, A geographical point represented by floating-point.</td>
      <tr>
         <td></td>
         <td>longitude: float, A geographical point represented by floating-point.</td>
      <tr>
         <td></td>
         <td>altitude: float, Indicates the floor.</td>
      <tr>
         <td></td>
         <td>capacity: int, The amount of devices a shelf can hold.</td>
      <tr>
         <td></td>
         <td>audit_notification_enabled: bool, Indicates if an audit is enabled for the shelf.</td>
      <tr>
         <td></td>
         <td>audit_requested: bool, Indicates if an audit has been requested.</td>
      <tr>
         <td></td>
         <td>responsible_for_audit: str, The party responsible for audits.</td>
      <tr>
         <td></td>
         <td>last_audit_time: datetime, Indicates the last audit time.</td>
      <tr>
         <td></td>
         <td>last_audit_by: str, Indicates the last user to audit the shelf.</td>
      <tr>
         <td></td>
         <td>page_token: str, A page token to query next page results.</td>
      <tr>
         <td></td>
         <td>page_size: int, The number of results to query for and display.</td>
      <tr>
         <td></td>
         <td>shelf_request: ShelfRequest, A message containing the unique identifiers to be used when retrieving a shelf.</td>
   </tbody>
</table>

<br>

`list` List enabled or all shelves based on any shelf attribute.

<table>
   <tbody>
      <tr>
         <th align="center">Returns</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>Shelf ProtoRPC message</td>
         <td>enabled: bool, Indicates if the shelf is enabled or not.</td>
      </tr>
         <td></td>
         <td>friendly_name: str, The friendly name of the shelf.</td>
      <tr>
         <td></td>
         <td>location: str, The location of the shelf.</td>
      <tr>
         <td></td>
         <td>latitude: float, A geographical point represented by floating-point.</td>
      <tr>
         <td></td>
         <td>longitude: float, A geographical point represented by floating-point.</td>
      <tr>
         <td></td>
         <td>altitude: float, Indicates the floor.</td>
      <tr>
         <td></td>
         <td>capacity: int, The amount of devices a shelf can hold.</td>
      <tr>
         <td></td>
         <td>audit_notification_enabled: bool, Indicates if an audit is enabled for the shelf.</td>
      <tr>
         <td></td>
         <td>audit_requested: bool, Indicates if an audit has been requested.</td>
      <tr>
         <td></td>
         <td>responsible_for_audit: str, The party responsible for audits.</td>
      <tr>
         <td></td>
         <td>last_audit_time: datetime, Indicates the last audit time.</td>
      <tr>
         <td></td>
         <td>last_audit_by: str, Indicates the last user to audit the shelf.</td>
      <tr>
         <td></td>
         <td>page_token: str, A page token to query next page results.</td>
      <tr>
         <td></td>
         <td>page_size: int, The number of results to query for and display.</td>
      <tr>
         <td></td>
         <td>shelf_request: ShelfRequest, A message containing the unique identifiers to be used when retrieving a shelf.</td>
      <tr>
         <td></td>
         <td>query: shared_message.SearchRequest, a message containing query options to conduct a search on an index.</td>
   </tbody>
</table>

<table>
   <tbody>
      <tr>
         <th align="center">Returns</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>List Shelf Response ProtoRPC message.</td>
         <td>shelves: Shelf, The list of shelves being returned.</td>
      </tr>
      <tr>
         <td></td>
         <td>has_additional_results: bool, If there are more results to be displayed.</td>
      <tr>
         <td></td>
         <td>page_token: str, A page token that will allow be used to query for additional results.</td>
   </tbody>
</table>

<br>

`update` Get a shelf using location to update its properties.

<table>
   <tbody>
      <tr>
         <th align="center">Requests</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>UpdateShelfRequest ProtoRPC message.</td>
         <td>shelf_request: ShelfRequest, A message containing the unique identifiers to be used when retrieving a shelf.</td>
      </tr>
      <tr>
         <td></td>
         <td>friendly_name: str, The friendly name of the shelf.</td>
      <tr>
         <td></td>
         <td>location: str, The location of the shelf.</td>
      <tr>
         <td></td>
         <td>latitude: float, A geographical point represented by floating-point.</td>
      <tr>
         <td></td>
         <td>longitude: float, A geographical point represented by floating-point. </td>
      <tr>
         <td></td>
         <td>altitude: float, Indicates the floor.</td>

   </tbody>
</table>

<table>
   <tbody>
      <tr>
         <th align="center">Returns</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>message_types.VoidMessage</td>
         <td>None</td>
      </tr>
   </tbody>
</table>

<br>

### Survey_api

The entry point for the Survey methods.

#### Methods

`create` Create a new survey and insert instance into datastore.

<table>
   <tbody>
      <tr>
         <th align="center">Requests</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>Survey ProtoRPC Message to encapsulate the survey_model.Survey.</td>
         <td>survey_type: survey_model.SurveyType, The type of survey this is.</td>
      <tr>
         <td></td>
         <td>question: str, The text displayed as the question for this survey.</td>
      </tr>
      <tr>
         <td></td>
         <td>enabled: bool, Whether or not this survey should be enabled.</td>
      <tr>
         <td></td>
         <td>rand_weight: int, The weight to be applied to this survey when using the get method survey with random.</td>
      <tr>
         <td></td>
         <td>answers: List of Answer, The list of answers possible for this survey.</td>
      <tr>
         <td></td>
         <td>survey_urlsafe_key: str, The ndb.Key.urlsafe() for the survey.</td>
   </tbody>
</table>

<table>
   <tbody>
      <tr>
         <th align="center">Returns</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>message_types.VoidMessage</td>
         <td>None</td>
      </tr>
   </tbody>
</table>

<br>

`list` List surveys.

<table>
   <tbody>
      <tr>
         <th align="center">Requests</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>ListSurveyRequest ProtoRPC Message.</td>
         <td>survey_type: survey_model.SurveyType, The type of survey to list.</td>
      </tr>
      <tr>
         <td></td>
         <td>enabled: bool, True for only enabled surveys, False to view disabled surveys.</td>
     <tr>
        <td></td>
        <td>page_size: int, The size of the page to return.</td>
     <tr>
        <td></td>
        <td>page_token: str, The urlsafe representation of the page token. </td>
   </tbody>
</table>

<table>
   <tbody>
      <tr>
         <th align="center">Returns</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>SurveyList ProtoRPC Message.</td>
         <td>surveys: List of Survey, The list of surveys to return.</td>
      </tr>
      <tr>
         <td></td>
         <td>page_token: str, The urlsafe representation of the page token.</td>
      <tr>
         <td></td>
         <td>more: bool, Whether or not there are more results to be queried.</td>
   </tbody>
</table>

<br>

`patch` Patch a given survey.

<table>
   <tbody>
      <tr>
         <th align="center">Requests</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>PatchSurveyRequest ProtoRPC Message.</td>
         <td>survey_urlsafe_key: str, The ndb.Key.urlsafe() for the survey.</td>
      </tr>
      <tr>
         <td></td>
         <td>answers: List of Answer, The list of answers possible for this survey.</td>
      <tr>
         <td></td>
         <td>answer_keys_to_remove: List of str, The list of answer_urlsafe_key to remove from this survey.</td>
      <tr>
         <td></td>
         <td>survey_type: survey_model.SurveyType, The type of survey this is. </td>
      <tr>
         <td></td>
         <td>question: str, The text displayed as the question for this survey.</td>
      <tr>
         <td></td>
         <td>enabled: bool, Whether or not this survey should be enabled.</td>
      <tr>
         <td></td>
         <td>rand_weight: int, The weight to be applied to this survey when using the get method survey with random.</td>

   </tbody>
</table>

<table>
   <tbody>
      <tr>
         <th align="center">Returns</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>message_types.VoidMessage</td>
         <td>None</td>
      </tr>
   </tbody>
</table>

<br>

`request`Request a survey by type and present that survey to a Chrome App user.

<table>
   <tbody>
      <tr>
         <th align="center">Requests</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>ListSurveyRequest ProtoRPC Message.</td>
         <td>survey_type: survey_model.SurveyType, The type of survey to list.</td>
      </tr>
   </tbody>
</table>

<table>
   <tbody>
      <tr>
         <th align="center">Returns</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>Survey ProtoRPC Message to encapsulate the survey_model.Survey</td>
         <td>survey_type: survey_model.SurveyType, The type of survey this is.</td>
      </tr>
      <tr>
         <td></td>
         <td>question: str, The text displayed as the question for this survey.</td>
      <tr>
         <td></td>
         <td>enabled: bool, Whether or not this survey should be enabled.</td>
      <tr>
         <td></td>
         <td>rand_weight: int, The weight to be applied to this survey when using the get method survey with random.</td>
      <tr>
         <td></td>
         <td>answers: List of Answer, The list of answers possible for this survey.</td>
      <tr>
         <td></td>
         <td>survey_urlsafe_key: str, The ndb.Key.urlsafe() for the survey. </td>
   </tbody>
</table>

<br>

`submit` Submit a response to a survey acquired via a request.

<table>
   <tbody>
      <tr>
         <th align="center">Requests</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>SurveySubmission ProtoRPC Message.</td>
         <td>survey_urlsafe_key: str, The urlsafe ndb.Key for a survey_model.Survey instance.</td>
      </tr>
      <tr>
         <td></td>
         <td>answer_urlsafe_key: str, The urlsafe ndb.Key for a survey_model.Answer instance.</td>
      <tr>
         <td></td>
         <td>more_info: str, the extra info optionally provided for the given Survey and Answer.</td>
   </tbody>
</table>

<table>
   <tbody>
      <tr>
         <th align="center">Returns</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>message_types.VoidMessage</td>
         <td>None</td>
      </tr>
   </tbody>
</table>

<br>

### Tag_api

API endpoint that handles requests related to tags.

#### Methods

`create` Create a new tag.

<table>
   <tbody>
      <tr>
         <th align="center">Requests</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>tag_messages.CreateTagRequest</td>
         <td>tag: tag_messages.Tag, the attributes of a Tag.</td>
      </tr>
   </tbody>
</table>

<table>
   <tbody>
      <tr>
         <th align="center">Returns</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>message_types.VoidMessage</td>
         <td>None</td>
      </tr>
   </tbody>
</table>

`destroy` Destroy a tag.

<table>
   <tbody>
      <tr>
         <th align="center">Requests</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>tag_messages.TagRequest</td>
         <td>urlsafe_key: str, the urlsafe representation of the ndb.Key for the tag being requested.</td>
      </tr>
   </tbody>
</table>

<table>
   <tbody>
      <tr>
         <th align="center">Returns</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>message_types.VoidMessage</td>
         <td>None</td>
      </tr>
   </tbody>
</table>

`get` Get a tag.

<table>
   <tbody>
      <tr>
         <th align="center">Requests</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>tag_messages.TagRequest</td>
         <td>urlsafe_key: str, the urlsafe representation of the ndb.Key for the tag being requested.</td>
      </tr>
   </tbody>
</table>

<table>
   <tbody>
      <tr>
         <th align="center">Returns</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>tag_messages.Tag</td>
         <td>name: str, the unique name of the tag.</td>
      </tr>
      <tr>
         <td></td>
         <td>hidden: bool, whether the tag is hidden in the frontend, defaults to False.</td>
      <tr>
         <td></td>
         <td>color: str, the color of the tag, one of the material design palette.</td>
      <tr>
         <td></td>
         <td>protect: bool, whether the tag is protected from user manipulation; this field will only be included in response messages.</td>
      <tr>
         <td></td>
         <td>description: str, the description for the tag.</td>
   </tbody>
</table>

<br>

`update` Updates a tag.

<table>
   <tbody>
      <tr>
         <th align="center">Requests</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>tag_messages.UpdateTagRequest</td>
         <td>tag: tag_messages.Tag, the attributes of a Tag.</td>
      </tr>
   </tbody>
</table>

<table>
   <tbody>
      <tr>
         <th align="center">Returns</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>message_types.VoidMessage</td>
         <td>None</td>
      </tr>
   </tbody>
</table>

<br>

`list` Lists tags.

<table>
   <tbody>
      <tr>
         <th align="center">Requests</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>tag_messages.ListTagRequest</td>
         <td>page_size: int, the number of results to return.</td>
      </tr>
      <tr>
         <td></td>
         <td>cursor: str, the base64-encoded cursor string specifying where to start the query.</td>
      <tr>
         <td></td>
         <td>page_index: int, the page index to offset the results from.</td>
      <tr>
         <td></td>
         <td>include_hidden_tags: bool, whether to include hidden tags in the results, defaults to False.</td>
   </tbody>
</table>

<table>
   <tbody>
      <tr>
         <th align="center">Returns</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>tag_messages.ListTagResponse</td>
         <td>tags: tag_messages.Tag (repeated), the list of tags being returned.</td>
      </tr>
      <tr>
         <td></td>
         <td>cursor: str, the base64-encoded denoting the position of the last result retrieved. additional results to be retrieved.</td>
      <tr>
         <td></td>
         <td>
   </tbody>
</table>

<br>

### User_api

API endpoint that handles requests related to users.

#### Methods

`get` Get a user object using the logged in user's credential.

<table>
   <tbody>
      <tr>
         <th align="center">Returns</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>message_types.VoidMessage</td>
         <td>None</td>
      </tr>
   </tbody>
</table>

<table>
   <tbody>
      <tr>
         <th align="center">Returns</th>
         <th align="center">Attributes</th>
      </tr>
      <tr>
         <td>UserResponse response for ProtoRPC message.</td>
         <td>email: str, The user email to be displayed.</td>
      </tr>
      <tr>
         <td></td>
         <td>roles: list of str, The roles of the user to be displayed.</td>
      <tr>
         <td></td>
         <td>permissions: list of str, The permissions the user has.</td>
      <tr>
         <td></td>
         <td>superadmin: bool, if the user is superadmin.</td>
   </tbody>
</table>
