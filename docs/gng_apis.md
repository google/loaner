# Grab n Go API




## Getting Started with the GnG API

This documentation explains how to get started with the GnG API.

## API Authentication

The GnG API is authenticated based on user roles and permissions. Roles are
managed by Google groups that are synced with a Cron job.

### **Permission Containers**

Four primary roles are defined as followed:

*   **User**
    *   Any person who interacts with the application will receive the user role
        by default.
*   **Technician**
    *   A person responsible for the day-to-day inventory-related operations of
        the program including auditing shelves and adding/removing devices.
*   **Operational Admin**
    *   A person that is responsible for the operational health of the program.
        This is usually someone who works in frontline support and needs to have
        the ability to troubleshoot to ensure the health of devices and shelves.
*   **Technical Admin**
    *   A person that is in charge of configuring the application and
        experience. This role has super administrative privileges and the
        ability to perform all of the actions within the application.

Each role has a predefined set of permissions. Each role is defined with a
`namedTuple` and an enum for each permission that the role can access. We use a
decorator to check if a user has permission to execute methods.

#### Permission Container Example

```python
@enum.unique
class Permissions(str, enum.Enum):
  """Permission enums for all API method calls."""
  EDIT_SHELF = 'edit_shelf'
  ENABLE_SHELF = 'enable_shelf'
  ENROLL_DEVICE = 'enroll_device'
  ENROLL_SHELF = 'enroll_shelf'
  VIEW = 'view'
```

**`namedTuple` style:**

```python
_ROLE = collections.namedtuple('Role', 'name permissions')
```

**`namedTuple` example:**

```python
TECHNICAL_ADMIN_ROLE = _ROLE(
    name='technical-admin',
    permissions=[
        Permissions.EDIT_SHELF,
        Permissions.ENABLE_SHELF,
        Permissions.ENROLL_DEVICE,
        Permissions.ENROLL_SHELF,
    ])
OPERATIONAL_ADMIN_ROLE = _ROLE(
    name='operational-admin',
    permissions=[
        Permissions.EDIT_SHELF,
    ])
TECHNICIAN_ROLE = _ROLE(
    name='technician',
    permissions=[
        Permissions.EDIT_SHELF,
    ])
USER_ROLE = _ROLE(
    name='user', permissions=[Permissions.VIEW])
```

### Authentication Decorator

Authentication for each API call is managed with a decorator, which can restrict
a call based on two arguments, `user_auth_only` and `permission`. Setting
`user_auth_only` to `true` will only run an authentication to confirm that the
user calling the API is a valid G Suite domain user.

Setting an explicit permission will check that the user is in a role that has
the permission set in the permissions file. Several examples are shown below.
For an API call to have restricted permissions, this decorator must be set on
top of each API.

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

Users roles are managed using Google Groups. We will need to create 3 Google
groups that will contain users with elevated privileges in the Grab n Go
application. We suggest the group names be:

*   Technical Admins: For example, “technical-admins@example.com”
*   Operational Admins: For example, “operational-admins@example.com”
*   Technicians: For example, “technicians@example.com”

NOTE: Write down these group names. You'll need them later in the Settings file.

### [Adding Users to Google Groups]

To get the highest elevated permissions for GnG, add yourself to the technical
admin group.

### Set Administrative Groups in Setting.py File

1.  Go to the root of the source code and search for a file named `settings.py`.

1.  Use your favorite editor to open the file and add the administrative groups
    that you created earlier. For example:

    ```python
    # technical_admins_groups: str, The name of the Google Group that contains a
    # 'Technical Admin' in charge of configuring the app and experience.
    'technical_admins_group': 'technical-admins@example.com',

    # operational_admins_groups: str, The name of the Google Group that
    # contains a 'Operational Admin' - a person in charge of the operational
    # health of the program.
    'operational_admins_group': 'operational-admins@example.com',

    # technicians_groups: str, The name of the Google Group that contains a
    # 'Technician' - a person responsible for the day-to-day of the program,
    # check in, auditing, enrolling, etc. Also can see historical information.
    'technicians_group': 'technicians@example.com'
    ```

## API List

### Bootstrap_api

The entry point for the Bootstrap methods.

#### Methods

##### run

Runs request for the Bootstrap API:

| Requests                      | Attributes                                |
| :---------------------------- | :---------------------------------------- |
| RunRequest: Bootstrap request | requested_tasks: BootstrapTask, A list of |
| ProtoRPC message              | the requested tasks.                      |

Returns                   | Attributes
:------------------------ | :---------
message_types.VoidMessage | None

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

##### get_loan

Get the current loan for a given Chrome device:

| Requests                         | Attributes                               |
| :------------------------------- | :--------------------------------------- |
| LoanRequest: Chrome Loan Request | device_id: str, The unique Chrome device |
| ProtoRPC message.                | ID of the Chrome device.                 |
|                                  | need_name: bool, If given name should be |
|                                  | returned.                                |

| Returns                       | Attributes                                  |
| :---------------------------- | :------------------------------------------ |
| LoanResponse: Chrome Loan     | due_date: datetime, The due date for the    |
| information Response ProtoRPC | device.                                     |
| message.                      |                                             |
|                               | max_extend_date: datetime, The max date a   |
|                               | loan can be extended.                       |
|                               | given_name: str, The given name for the     |
|                               | user.                                       |
|                               | guest_permitted: bool, If guest mode can be |
|                               | enabled.                                    |
|                               | guest_enabled: bool, If guest mode is       |
|                               | enabled.                                    |

### Configuration_api

Lists the given setting's value.

#### Methods

##### get_configuration

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

##### list_configurations

Get a list of all configuration values.

Requests                  | Attributes
:------------------------ | :---------
message_types.VoidMessage | None

| Returns                             | Attributes                            |
| :---------------------------------- | :------------------------------------ |
| ListConfigurationsResponse response | settings: ConfigurationResponse, The  |
| for ProtoRPC message.               | setting and corresponding value being |
|                                     | returned.                             |

##### update_configuration

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

##### datastore_import

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

##### enroll

Enrolls a device in the program

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

##### unenroll

Unenrolls a device from the program.

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

##### device_audit_check

Runs prechecks on a device to see if it can be audited.

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

##### get_device

Gets a device using any identifier in device_message.DeviceRequest.

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

##### list_devices

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
|                          | page_token: str, A page token to query next page  |
|                          | results.                                          |
|                          | page_size: int, The number of results to query    |
|                          | for and display.                                  |

| Returns                       | Attributes                                  |
| :---------------------------- | :------------------------------------------ |
| List device response ProtoRPC | devices: Device, A device to display.       |
| message.                      |                                             |
|                               | additional_results: bool, If there are more |
|                               | results to be displayed.                    |
|                               | page_token: str, A page token that will     |
|                               | allow be used to query for additional       |
|                               | results.                                    |

##### enable_guest_mode

Enables Guest Mode for a given device.

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

Mark that a device is damaged.

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

### Shelf_api

The entry point for the Shelf methods.

#### Methods

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

##### list_shelves

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
|                         | page_token: str, A page token to query next page   |
|                         | results.                                           |
|                         | page_size: int, The number of results to query for |
|                         | and display.                                       |

| Returns                      | Attributes                                    |
| :--------------------------- | :-------------------------------------------- |
| List Shelf Response ProtoRPC | shelves: Shelf, The list of shelves being     |
| message.                     | returned.                                     |
|                              | additional_results: bool, If there are more   |
|                              | results to be displayed.                      |
|                              | page_token: str, A page token that will allow |
|                              | be used to query for additional results.      |

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

### Survey_api

The entry point for the Survey methods.

#### Methods

##### create_survey

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
| ProtoRPC message.              |                                             |
|                                | roles: list, The roles of the user to be    |
|                                | displayed.                                  |

[Adding Users to Google Groups]: https://support.google.com/groups/answer/2465464?hl=en&ref_topic=2458761
