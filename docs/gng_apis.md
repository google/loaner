# Grab n Go API




## Getting Started with the GnG API

This documentation explains how to get started with the GnG API.

## API Authentication

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

Additional roles can be created by using the Roles API. Each Role can be
given zero or more permissions and associated with a group to automatically
add users to the given role. Some example roles you may want to create are
a technician role that can audit shelves and other inventory-related tasks or
a helpdesk role that can assist users with their loans.


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

1.  Use your favorite editor to open the file and add the superadmin group
    that you created earlier. For example:

    ```python
    # superadmins_group: str, The name of the Google Group that governs who is
    # a superadmin. Superadmins have all permissions by default.
    SUPERADMINS_GROUP = 'technical-admins@example.com'
    ```

## API List

### Bootstrap_api

The entry point for the Bootstrap methods.

#### Methods

##### get_status

Gets general bootstrap status, and task status if not yet completed:

Requests                  | Attributes
:------------------------ | :---------
message_types.VoidMessage | None

| Returns                             | Attributes                             |
| :---------------------------------- | :------------------------------------- |
| GetStatusResponse: Bootstrap status | enabled: bool, indicates if the        |
| response ProtoRPC                   | bootstrap is enabled.                  |
|                                     | started: bool, indicated if the        |
|                                     | bootstrap has been started.            |
|                                     | completed: bool, indicated if the      |
|                                     | bootstrap is completed.                |
|                                     | tasks: BootstrapTask, A list of all of |
|                                     | the tasks to be displayed.             |

##### run

Runs request for the Bootstrap API:

| Requests                      | Attributes                                |
| :---------------------------- | :---------------------------------------- |
| RunRequest: Bootstrap request | requested_tasks: BootstrapTask, A list of |
| ProtoRPC message              | the requested tasks.                      |

Returns                   | Attributes
:------------------------ | :---------
message_types.VoidMessage | None

### Chrome_api

The entry point for the GnG Loaners Chrome App.

#### Methods

##### heartbeat

Heartbeat check-in for Chrome devices:

| Requests                            | Attributes                        |
| :---------------------------------- | :-------------------------------- |
| HeartbeatRequest: Heartbeat Request | device_id: str, The unique Chrome |
| ProtoRPC message.                   | device ID of the Chrome device.   |

| Returns                      | Attributes                                    |
| :--------------------------- | :-------------------------------------------- |
| HeartbeatResponse: Heartbeat | is_enrolled: bool, Determine if the device is |
| Response ProtoRPC message.   | enrolled.                                     |
|                              | start_assignment: bool, Determine if          |
|                              | assignment workflow should be started.        |

### Configuration_api

Lists the given setting's value.

#### Methods

##### get

Lists the given setting's value:

| Requests                            | Attributes                             |
| :---------------------------------- | :------------------------------------- |
| GetConfigurationRequest request for | setting: str, The name of the setting  |
| ProtoRPC message.                   | being requested.                       |
|                                     | configuration_type: ConfigurationType, |
|                                     | The type of configuration to request   |
|                                     | for.                                   |

| Returns                            | Attributes                              |
| :--------------------------------- | :-------------------------------------- |
| ConfigurationResponse response for | setting: str, The name of the setting   |
| ProtoRPC message.                  | being returned.                         |
|                                    | string_value: str, The string value of  |
|                                    | the setting.                            |
|                                    | integer_value: int, The integer value   |
|                                    | of the setting.                         |
|                                    | boolean_value: bool, The boolean value  |
|                                    | of the setting.                         |
|                                    | list_value: list, The list value of the |
|                                    | setting.                                |

##### list

Get a list of all configuration values.

Requests                  | Attributes
:------------------------ | :---------
message_types.VoidMessage | None

| Returns                             | Attributes                            |
| :---------------------------------- | :------------------------------------ |
| ListConfigurationsResponse response | settings: ConfigurationResponse, The  |
| for ProtoRPC message.               | setting and corresponding value being |
|                                     | returned.                             |

##### update

Updates a given settings value.

| Requests                           | Attributes                              |
| :--------------------------------- | :-------------------------------------- |
| UpdateConfigurationRequest request | setting: str, The name of the setting   |
| for ProtoRPC message.              | being requested.                        |
|                                    | configuration_type: ConfigurationType,  |
|                                    | The type of configuration to request    |
|                                    | for.                                    |
|                                    | string_value: str, The string value of  |
|                                    | the setting being updated.              |
|                                    | integer_value: int, The integer value   |
|                                    | of the setting being updated.           |
|                                    | boolean_value: bool, The boolean value  |
|                                    | of the setting being updated.           |
|                                    | list_value: list, The list value of the |
|                                    | setting being updated.                  |

Returns                   | Attributes
:------------------------ | :---------
message_types.VoidMessage | None

### Datastore_api

The entry point for the Datastore methods.

#### Methods

##### import

Datastore import request for the Datastore API.

| Requests                      | Attributes                            |
| :---------------------------- | :------------------------------------ |
| Datastore YAML Import Request | yaml: str, The name of the YAML being |
| ProtoRPC message.             | imported.                             |

Returns                   | Attributes
:------------------------ | :---------
message_types.VoidMessage | None

### Device_api

API endpoint that handles requests related to Devices.

#### Methods

##### auditable

If a device is able to be audited for shelf audits. Returns an error if the
device cannot be moved to the shelf for any reason.

| Requests                          | Attributes                               |
| :-------------------------------- | :--------------------------------------- |
| General Device request ProtoRPC   | asset_tag: str, The asset tag of the     |
| message with several identifiers. | Chrome device.                           |
| Only one identifier needs to be   | chrome_device_id: str, The Chrome device |
| provided.                         | id of the Chrome device.                 |
|                                   | serial_number: str, The serial number of |
|                                   | the Chrome device.                       |
|                                   | urlkey: str, The URL-safe key of a       |
|                                   | device.                                  |
|                                   | unknown_identifier: str, Either an asset |
|                                   | tag or serial number of the device.      |

Returns                   | Attributes
:------------------------ | :---------
message_types.VoidMessage | None

##### enable_guest_mode

Enables Guest Mode for a given device.

| Requests                          | Attributes                               |
| :-------------------------------- | :--------------------------------------- |
| General Device request ProtoRPC   | asset_tag: str, The asset tag of the     |
| message with several identifiers. | Chrome device.                           |
| Only one identifier needs to be   | chrome_device_id: str, The Chrome device |
| provided.                         | id of the Chrome device.                 |
|                                   | serial_number: str, The serial number of |
|                                   | the Chrome device.                       |
|                                   | urlkey: str, The URL-safe key of a       |
|                                   | device.                                  |
|                                   | unknown_identifier: str, Either an asset |
|                                   | tag or serial number of the device.      |

Returns                   | Attributes
:------------------------ | :---------
message_types.VoidMessage | None

##### enroll

Enrolls a device in the program

| Requests                          | Attributes                               |
| :-------------------------------- | :--------------------------------------- |
| General Device request ProtoRPC   | asset_tag: str, The asset tag of the     |
| message with several identifiers. | Chrome device.                           |
| Only one identifier needs to be   | chrome_device_id: str, The Chrome device |
| provided.                         | id of the Chrome device.                 |
|                                   | serial_number: str, The serial number of |
|                                   | the Chrome device.                       |
|                                   | urlkey: str, The URL-safe key of a       |
|                                   | device.                                  |
|                                   | unknown_identifier: str, Either an asset |
|                                   | tag or serial number of the device.      |

Returns                   | Attributes
:------------------------ | :---------
message_types.VoidMessage | None

##### extend_loan

Extend the current loan for a given Chrome device.

| Requests                        | Attributes                                |
| :------------------------------ | :---------------------------------------- |
| Loan extension request ProtoRPC | device: DeviceRequest, A device to be     |
| message.                        | fetched.                                  |
|                                 | extend_date: datetime, The date to extend |
|                                 | the loan for.                             |

Returns                   | Attributes
:------------------------ | :---------
message_types.VoidMessage | None

##### get

Gets a device using any identifier in device_message.DeviceRequest.

| Requests                          | Attributes                               |
| :-------------------------------- | :--------------------------------------- |
| General Device request ProtoRPC   | asset_tag: str, The asset tag of the     |
| message with several identifiers. | Chrome device.                           |
| Only one identifier needs to be   | chrome_device_id: str, The Chrome device |
| provided.                         | id of the Chrome device.                 |
|                                   | serial_number: str, The serial number of |
|                                   | the Chrome device.                       |
|                                   | urlkey: str, The URL-safe key of a       |
|                                   | device.                                  |
|                                   | unknown_identifier: str, Either an asset |
|                                   | tag or serial number of the device.      |

Returns                   | Attributes
:------------------------ | :---------
message_types.VoidMessage | None

##### list

Lists all devices based on any device attribute.

| Requests                 | Attributes                                        |
| :----------------------- | :------------------------------------------------ |
| Device ProtoRPC message. | serial_number: str, The serial number of the      |
|                          | Chrome device.                                    |
|                          | asset_tag: str, The asset tag of the Chrome       |
|                          | device.                                           |
|                          | enrolled: bool, Indicates the enrollment status   |
|                          | of the device.                                    |
|                          | device_model: int, Identifies the model name of   |
|                          | the device.                                       |
|                          | due_date: datetime, The date that device is due   |
|                          | for return.                                       |
|                          | last_know_healthy: datetime, The date to indicate |
|                          | the last known healthy status.                    |
|                          | shelf: shelf_messages.Shelf, The shelf the device |
|                          | is placed on.                                     |
|                          | assigned_user: str, The email of the user who is  |
|                          | assigned to the device.                           |
|                          | assignment_date: datetime, The date the device    |
|                          | was assigned to a user.                           |
|                          | current_ou: str, The current organizational unit  |
|                          | the device belongs to.                            |
|                          | ou_change_date: datetime, The date the            |
|                          | organizational unit was changed.                  |
|                          | locked: bool, Indicates whether or not the device |
|                          | is locked.                                        |
|                          | lost: bool, Indicates whether or not the device   |
|                          | is lost.                                          |
|                          | mark_pending_return_date: datetime, The date a    |
|                          | user marked device returned.                      |
|                          | chrome_device_id: str, A unique device ID.        |
|                          | last_heartbeat: datetime, The date of the last    |
|                          | time the device checked in.                       |
|                          | damaged: bool, Indicates the if the device is     |
|                          | damaged.                                          |
|                          | damaged_reason: str, A string denoting the reason |
|                          | for being reported as damaged.                    |
|                          | last_reminder: Reminder, Level, time, and count   |
|                          | of the last reminder the device had.              |
|                          | next_reminder: Reminder, Level, time, and count   |
|                          | of the next reminder.                             |
|                          | page_size: int, The number of results to query    |
|                          | for and display.                                  |
|                          | page_number: int, the page index to offset the    |
|                          | results                                           |
|                          | max_extend_date: datetime, Indicates maximum      |
|                          | extend date a device can have.                    |
|                          | guest_enabled: bool, Indicates if guest mode has  |
|                          | been already enabled.                             |
|                          | guest_permitted: bool, Indicates if guest mode has|
|                          | been allowed.                                     |
|                          | give_name: str, The given name of the user.       |
|                          | query: shared_message.SearchRequest, a message    |
|                          | containing query options to conduct a search on an|
|                          | index.                                            |

| Returns                       | Attributes                                  |
| :---------------------------- | :------------------------------------------ |
| List device response ProtoRPC | devices: Device, A device to display.       |
| message.                      |                                             |
|                               | total_results: int, the total number of     |
|                               | results for a query.                        |
|                               | total_pages: int, the total number of pages |
|                               | needed to display all of the results.       |

##### mark_damaged

Mark that a device is damaged.

| Requests                         | Attributes                            |
| :------------------------------- | :------------------------------------ |
| Damaged device ProtoRPC message. | device: DeviceRequest, A device to be |
|                                  | fetched.                              |
|                                  | damaged_reason: str, The reason the   |
|                                  | device is being reported as damaged.  |

Returns                   | Attributes
:------------------------ | :---------
message_types.VoidMessage | None

##### mark_lost

Mark that a device is lost.

| Requests                          | Attributes                               |
| :-------------------------------- | :--------------------------------------- |
| General Device request ProtoRPC   | asset_tag: str, The asset tag of the     |
| message with several identifiers. | Chrome device.                           |
|                                   | chrome_device_id: str, The Chrome device |
|                                   | id of the Chrome device.                 |
|                                   | serial_number: str, The serial number of |
|                                   | the Chrome device.                       |
|                                   | urlkey: str, The URL-safe key of a       |
|                                   | device.                                  |
|                                   | unknown_identifier: str, Either an asset |
|                                   | tag or serial number of the device.      |

Returns                   | Attributes
:------------------------ | :---------
message_types.VoidMessage | None

##### mark_pending_return

Mark that a device is pending return.

| Requests                          | Attributes                               |
| :-------------------------------- | :--------------------------------------- |
| General Device request ProtoRPC   | asset_tag: str, The asset tag of the     |
| message with several identifiers. | Chrome device.                           |
| Only one identifier needs to be   | chrome_device_id: str, The Chrome device |
| provided.                         | id of the Chrome device.                 |
|                                   | serial_number: str, The serial number of |
|                                   | the Chrome device.                       |
|                                   | urlkey: str, The URL-safe key of a       |
|                                   | device.                                  |
|                                   | unknown_identifier: str, Either an asset |
|                                   | tag or serial number of the device.      |

Returns                   | Attributes
:------------------------ | :---------
message_types.VoidMessage | None

##### resume_loan

Manually resume a loan that was paused because the device was marked
pending_return.

| Requests                          | Attributes                               |
| :-------------------------------- | :--------------------------------------- |
| General Device request ProtoRPC   | asset_tag: str, The asset tag of the     |
| message with several identifiers. | Chrome device.                           |
| Only one identifier needs to be   | chrome_device_id: str, The Chrome device |
| provided.                         | id of the Chrome device.                 |
|                                   | serial_number: str, The serial number of |
|                                   | the Chrome device.                       |
|                                   | urlkey: str, The URL-safe key of a       |
|                                   | device.                                  |
|                                   | unknown_identifier: str, Either an asset |
|                                   | tag or serial number of the device.      |

Returns                   | Attributes
:------------------------ | :---------
message_types.VoidMessage | None

##### unenroll

Unenrolls a device from the program.

| Requests                          | Attributes                               |
| :-------------------------------- | :--------------------------------------- |
| General Device request ProtoRPC   | asset_tag: str, The asset tag of the     |
| message with several identifiers. | Chrome device.                           |
| Only one identifier needs to be   | chrome_device_id: str, The Chrome device |
| provided.                         | id of the Chrome device.                 |
|                                   | serial_number: str, The serial number of |
|                                   | the Chrome device.                       |
|                                   | urlkey: str, The URL-safe key of a       |
|                                   | device.                                  |
|                                   | unknown_identifier: str, Either an asset |
|                                   | tag or serial number of the device.      |

Returns                   | Attributes
:------------------------ | :---------
message_types.VoidMessage | None

##### user_devices

Lists the devices assigned to the currently logged in user.

Requests                  | Attributes
:------------------------ | :---------
message_types.VoidMessage | None

| Returns                       | Attributes                                  |
| :---------------------------- | :------------------------------------------ |
| List device response ProtoRPC | devices: Device, A device to display.       |
| message.                      |                                             |
|                               | additional_results: bool, If there are more |
|                               | results to be displayed.                    |
|                               | page_token: str, A page token that will     |
|                               | allow be used to query for additional       |
|                               | results.                                    |

### Roles_api

API endpoint that handles requests related to user roles.

#### Methods

##### create

Create a new role.

| Requests                      | Attributes
| :---------------------------- | :---------
| user_messages.Role            | name: str, the name of the role.
|                               | permissions: list of str, zero or more
|                               | permissions to add to the role.
|                               | associated_group: str, optional group to
|                               | associate to the role for automatic sync.

| Returns                        | Attributes                                  |
| :----------------------------- | :------------------------------------------ |
| message_types.VoidMessage      | None                                        |

##### get

Get a specific role by name.

| Requests                      | Attributes
| :---------------------------- | :---------
| user_messages.GetRoleRequest  | name: str, the name of the role.

| Returns                       | Attributes
| :---------------------------- | :---------
| user_messages.Role            | name: str, the name of the role.
|                               | permissions: list of str, zero or more
|                               | permissions associated with the role.
|                               | associated_group: str, optional group
|                               | associated to the role for automatic sync.

##### update

Updates a role's permissions or associated group. Role names cannot be changed
once set.

| Requests                      | Attributes
| :---------------------------- | :---------
| user_messages.Role            | name: str, the name of the role.
|                               | permissions: list of str, zero or more
|                               | permissions to add to the role.
|                               | associated_group: str, optional group to
|                               | associate to the role for automatic sync.

| Returns                        | Attributes                                  |
| :----------------------------- | :------------------------------------------ |
| message_types.VoidMessage      | None                                        |

### Search_api

API endpoint that handles requests related to search.

#### Methods

##### clear

Clear the index for a given model (Device or Shelf).

| Requests                      | Attributes
| :---------------------------- | :---------
| search_messages.SearchMessage | model: enum, the model to clear the index of
|                               | (Device or Shelf).

| Returns                        | Attributes                                  |
| :----------------------------- | :------------------------------------------ |
| message_types.VoidMessage      | None                                        |

##### reindex

Reindex the entities for a given model (Device or Shelf).

| Requests                      | Attributes
| :---------------------------- | :---------
| search_messages.SearchMessage | model: enum, the model to reindex (Device or
|                               | Shelf).

| Returns                        | Attributes                                  |
| :----------------------------- | :------------------------------------------ |
| message_types.VoidMessage      | None                                        |

### Shelf_api

The entry point for the Shelf methods.

#### Methods

##### audit

Performs an audit on a shelf based on location.

| Requests                            | Attributes                             |
| :---------------------------------- | :------------------------------------- |
| ShelfAuditRequest ProtoRPC message. | shelf_request: ShelfRequest, A message |
|                                     | containing the unique identifiers to   |
|                                     | be used when retrieving a shelf.       |
|                                     | device_identifiers: list, A list of    |
|                                     | device serial numbers to perform a     |
|                                     | device audit on.                       |

Returns                   | Attributes
:------------------------ | :---------
message_types.VoidMessage | None

##### disable

Disable a shelf by its location.

| Requests                     | Attributes                                    |
| :--------------------------- | :----------------------------------------     |
| ShelfRequest                 | location: str, The location of the shelf.     |
|                              | urlsafe_key: str, The urlsafe representation  |
|                              | of a ndb.Key.                                 |

Returns                   | Attributes
:------------------------ | :---------
message_types.VoidMessage | None

##### enroll

Enroll request for the Shelf API.

| Requests                             | Attributes                            |
| :----------------------------------- | :------------------------------------ |
| EnrollShelfRequest ProtoRPC message. | friendly_name: str, The friendly name |
|                                      | of the shelf.                         |
|                                      | location: str, The location of the    |
|                                      | shelf.                                |
|                                      | latitude: float, A geographical point |
|                                      | represented by floating-point.        |
|                                      | longitude: float, A geographical      |
|                                      | point represented by floating-point.  |
|                                      | altitude: float, Indicates the floor. |
|                                      | capacity: int, The amount of devices  |
|                                      | a shelf can hold.                     |
|                                      | audit_notification_enabled: bool,     |
|                                      | Indicates if an audit is enabled for  |
|                                      | the shelf.                            |
|                                      | responsible_for_audit: str, The party |
|                                      | responsible for audits.               |

Returns                   | Attributes
:------------------------ | :---------
message_types.VoidMessage | None

##### get

Get a shelf based on location.

| Requests                     | Attributes                                    |
| :--------------------------- | :----------------------------------------     |
| ShelfRequest                 | location: str, The location of the shelf.     |
|                              | urlsafe_key: str, The urlsafe representation  |
|                              | of a ndb.Key.                                 |

| Returns                 | Attributes                                         |
| :---------------------- | :------------------------------------------------- |
| Shelf ProtoRPC message. | enabled: bool, Indicates if the shelf is enabled   |
|                         | or not.                                            |
|                         | friendly_name: str, The friendly name of the       |
|                         | shelf.                                             |
|                         | location: str, The location of the shelf.          |
|                         | latitude: float, A geographical point represented  |
|                         | by floating-point.                                 |
|                         | longitude: float, A geographical point represented |
|                         | by floating-point.                                 |
|                         | altitude: float, Indicates the floor.              |
|                         | capacity: int, The amount of devices a shelf can   |
|                         | hold.                                              |
|                         | audit_notification_enabled: bool, Indicates if an  |
|                         | audit is enabled for the shelf.                    |
|                         | audit_requested: bool, Indicates if an audit has   |
|                         | been requested.                                    |
|                         | responsible_for_audit: str, The party responsible  |
|                         | for audits.                                        |
|                         | last_audit_time: datetime, Indicates the last      |
|                         | audit time.                                        |
|                         | last_audit_by: str, Indicates the last user to     |
|                         | audit the shelf.                                   |
|                         | page_token: str, A page token to query next page   |
|                         | results.                                           |
|                         | page_size: int, The number of results to query for |
|                         | and display.                                       |
|                         | shelf_request: ShelfRequest, A message containing  |
|                         | the unique identifiers to be used when retrieving a|
|                         | shelf.                                             |

##### list

List enabled or all shelves based on any shelf attribute.

| Requests                | Attributes                                         |
| :---------------------- | :------------------------------------------------- |
| Shelf ProtoRPC message. | enabled: bool, Indicates if the shelf is enabled   |
|                         | or not.                                            |
|                         | friendly_name: str, The friendly name of the       |
|                         | shelf.                                             |
|                         | location: str, The location of the shelf.          |
|                         | latitude: float, A geographical point represented  |
|                         | by floating-point.                                 |
|                         | longitude: float, A geographical point represented |
|                         | by floating-point.                                 |
|                         | altitude: float, Indicates the floor.              |
|                         | capacity: int, The amount of devices a shelf can   |
|                         | hold.                                              |
|                         | audit_notification_enabled: bool, Indicates if an  |
|                         | audit is enabled for the shelf.                    |
|                         | audit_requested: bool, Indicates if an audit has   |
|                         | been requested.                                    |
|                         | responsible_for_audit: str, The party responsible  |
|                         | for audits.                                        |
|                         | last_audit_time: datetime, Indicates the last      |
|                         | audit time.                                        |
|                         | last_audit_by: str, Indicates the last user to     |
|                         | audit the shelf.                                   |
|                         | page_size: int, The number of results to query for |
|                         | and display.                                       |
|                         | page_number: int, the page index to offset the     |
|                         | results                                            |
|                         | shelf_request: ShelfRequest, A message containing  |
|                         | the unique identifier to be used to retrieve the   |
|                         | shelf.                                             |
|                         | query: shared_message.SearchRequest, a message     |
|                         | containing query options to conduct a search on an |
|                         | index.                                             |

| Returns                      | Attributes                                    |
| :--------------------------- | :-------------------------------------------- |
| List Shelf Response ProtoRPC | shelves: Shelf, The list of shelves being     |
| message.                     | returned.                                     |
|                              | total_results: int, the total number of       |
|                              | results for a query.                          |
|                              | total_pages: int, the total number of pages   |
|                              | needed to display all of the results.         |

##### update

Get a shelf using location to update its properties.

| Requests                             | Attributes                            |
| :----------------------------------- | :------------------------------------ |
| UpdateShelfRequest ProtoRPC message. | shelf_request: ShelfRequest, A message|
|                                      | containing the unique identifiers to  |
|                                      | be used when retrieving a shelf.      |
|                                      | friendly_name: str, The friendly name |
|                                      | of the shelf.                         |
|                                      | location: str, The location of the    |
|                                      | shelf.                                |
|                                      | latitude: float, A geographical point |
|                                      | represented by floating-point.        |
|                                      | longitude: float, A geographical      |
|                                      | point represented by floating-point.  |
|                                      | altitude: float, Indicates the floor. |

Returns                   | Attributes
:------------------------ | :---------
message_types.VoidMessage | None

### Survey_api

The entry point for the Survey methods.

#### Methods

##### create

Create a new survey and insert instance into datastore.

| Requests                             | Attributes                            |
| :----------------------------------- | :------------------------------------ |
| Survey ProtoRPC Message to           | survey_type: survey_model.SurveyType, |
| encapsulate the survey_model.Survey. | The type of survey this is.           |
|                                      | question: str, The text displayed as  |
|                                      | the question for this survey.         |
|                                      | enabled: bool, Whether or not this    |
|                                      | survey should be enabled.             |
|                                      | rand_weight: int, The weight to be    |
|                                      | applied to this survey when using the |
|                                      | get method survey with random.        |
|                                      | answers: List of Answer, The list of  |
|                                      | answers possible for this survey.     |
|                                      | survey_urlsafe_key: str, The          |
|                                      | ndb.Key.urlsafe() for the survey.     |

Returns                   | Attributes
:------------------------ | :---------
message_types.VoidMessage | None

##### list

List surveys.

| Requests                            | Attributes                            |
| :---------------------------------- | :------------------------------------ |
| ListSurveyRequest ProtoRPC Message. | survey_type: survey_model.SurveyType, |
|                                     | The type of survey to list.           |
|                                     | enabled: bool, True for only          |
|                                     | enabled surveys, False to view        |
|                                     | disabled surveys.                     |
|                                     | page_size: int, The size of the       |
|                                     | page to return.                       |
|                                     | page_token: str, The urlsafe          |
|                                     | representation of the page token.     |

| Returns                      | Attributes                                   |
| :--------------------------- | :------------------------------------------- |
| SurveyList ProtoRPC Message. | surveys: List of Survey, The list of surveys |
|                              | to return.                                   |
|                              | page_token: str, The urlsafe                 |
|                              | representation of the page token.            |
|                              | more: bool, Whether or not there are more    |
|                              | results to be queried.                       |

##### patch

Patch a given survey.

| Requests                             | Attributes                            |
| :----------------------------------- | :------------------------------------ |
| PatchSurveyRequest ProtoRPC Message. | survey_urlsafe_key: str, The          |
|                                      | ndb.Key.urlsafe() for the survey.     |
|                                      | answers: List of Answer, The list of  |
|                                      | answers possible for this survey.     |
|                                      | answer_keys_to_remove: List of str,   |
|                                      | The list of answer_urlsafe_key to     |
|                                      | remove from this survey.              |
|                                      | survey_type: survey_model.SurveyType, |
|                                      | The type of survey this is.           |
|                                      | question: str, The text displayed as  |
|                                      | the question for this survey.         |
|                                      | enabled: bool, Whether or not this    |
|                                      | survey should be enabled.             |
|                                      | rand_weight: int, The weight to be    |
|                                      | applied to this survey when using the |
|                                      | get method survey with random.        |

Returns                   | Attributes
:------------------------ | :---------
message_types.VoidMessage | None

##### request

Request a survey by type and present that survey to a Chrome App user.

| Requests                        | Attributes                                |
| :------------------------------ | :---------------------------------------- |
| SurveyRequest ProtoRPC Message. | survey_type: survey_model.SurveyType, The |
|                                 | type of survey being requested.           |

| Returns                              | Attributes                            |
| :----------------------------------- | :------------------------------------ |
| Survey ProtoRPC Message to           | survey_type: survey_model.SurveyType, |
| encapsulate the survey_model.Survey. | The type of survey this is.           |
|                                      | question: str, The text displayed as  |
|                                      | the question for this survey.         |
|                                      | enabled: bool, Whether or not this    |
|                                      | survey should be enabled.             |
|                                      | rand_weight: int, The weight to be    |
|                                      | applied to this survey when using the |
|                                      | get method survey with random.        |
|                                      | answers: List of Answer, The list of  |
|                                      | answers possible for this survey.     |
|                                      | survey_urlsafe_key: str, The          |
|                                      | ndb.Key.urlsafe() for the survey.     |

##### submit

Submit a response to a survey acquired via a request.

| Requests                           | Attributes                              |
| :--------------------------------- | :-------------------------------------- |
| SurveySubmission ProtoRPC Message. | survey_urlsafe_key: str, The urlsafe    |
|                                    | ndb.Key for a survey_model.Survey       |
|                                    | instance.                               |
|                                    | answer_urlsafe_key: str, The urlsafe    |
|                                    | ndb.Key for a survey_model.Answer       |
|                                    | instance.                               |
|                                    | more_info: str, the extra info          |
|                                    | optionally provided for the given       |
|                                    | Survey and Answer.                      |

Returns                   | Attributes
:------------------------ | :---------
message_types.VoidMessage | None

### Tag_api

API endpoint that handles requests related to tags.

#### Methods

##### create

Create a new tag.

| Requests                      | Attributes
| :---------------------------- | :---------
| tag_messages.CreateTagRequest | tag: tag_messages.Tag, the attributes of a Tag.

Returns                   | Attributes
:------------------------ | :---------
message_types.VoidMessage | None

##### destroy

Destroy a tag.

| Requests                       | Attributes
| :----------------------------- | :---------
| tag_messages.TagRequest        | urlsafe_key: str, the urlsafe representation
|                                | of the ndb.Key for the tag being requested.

Returns                   | Attributes
:------------------------ | :---------
message_types.VoidMessage | None

##### get

Destroy a tag.

| Requests                       | Attributes
| :----------------------------- | :---------
| tag_messages.TagRequest        | urlsafe_key: str, the urlsafe representation
|                                | of the ndb.Key for the tag being requested.

Returns           | Attributes
:---------------- | :---------
tag_messages.Tag  | name: str, the unique name of the tag.
                  | hidden: bool, whether the tag is hidden in the frontend,
                  | defaults to False.
                  | color: str, the color of the tag, one of the material
                  | design palette.
                  | protect: bool, whether the tag is protected from user
                  | manipulation; this field will only be included in response
                  | messages.
                  | description: str, the description for the tag.

### User_api

API endpoint that handles requests related to users.

#### Methods

##### get

Get a user object using the logged in user's credential.

| Requests                  | Attributes
| :------------------------ | :---------
| message_types.VoidMessage | None

| Returns                        | Attributes                                  |
| :----------------------------- | :------------------------------------------ |
| UserResponse response for      | email: str, The user email to be displayed. |
| ProtoRPC message.              | roles: list of str, The roles of the user to|
|                                | be displayed.                               |
|                                | permissions: list of str, The permissions   |
|                                | the user has.                               |
|                                | superadmin: bool, if the user is superadmin.|
