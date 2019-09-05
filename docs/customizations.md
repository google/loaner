### (Optional) Customize GnG Settings

*Default Configurations* are those options you can configure when GnG is
running. The default values for these options are defined in
`loaner/web_app/config_defaults.yaml`. After first launch, GnG stores these
values in [Cloud Datastore](https://cloud.google.com/datastore/). You can change
settings without deploying a new version of GnG:

+   **allow_guest_mode**: Allow users to use guest mode on loaner devices.
+   **loan_duration**: The number of days to assign a device.
+   **maximum_loan_duration**: The maximum number of days a loaner can be
    loaned.
+   **loan_duration_email**: Send a duration email to the user.
+   **reminder_email_throttling**: Do not send emails to a user when a reminder
    appears in the loaner's Chrome app.
+   **reminder_delay**: Number of hours after which GnG will send a reminder
    email for a device identified as needing a reminder.
+   **shelf_audit**: Enable shelf audit.
+   **shelf_audit_email**: Whether email should be sent for audits.
+   **shelf_audit_email_to**: List of email addresses to receive a notification.
+   **shelf_audit_interval**: The number of hours to allow a shelf to remain
    unaudited. Can be overwritten via the audit_interval_override property for a
    shelf.
+   **responsible_for_audit**: Group that is responsible for performing an audit
    on a shelf.
+   **support_contact**: The name of the support contact.
+   **org_unit_prefix**: The organizational unit to be the root for the GnG
    child organizational units.
+   **audit_interval**: The shelf audit threshold in hours.
+   **sync_roles_query_size**: The number of users for whom to query and
    synchronize roles.
+   **anonymous_surveys**: Record surveys anonymously (or not).
+   **use_asset_tags**: To require asset tags when enrolling new devices, set as
    True. Otherwise, set as False to only require serial numbers.
+   **img_banner_**: The banner is a custom image used in the reminder emails
    sent to users. Use the URL of an image you have stored in your GCP Storage.
+   **img_button_**: The button images is a custom image used for reminder
    emails sent to users. Use the URL of an image you have stored in your GCP
    Storage.
+   **timeout_guest_mode**: Specify that a deferred task should be created to
    time out guest mode.
+   **guest_mode_timeout_in_hours**: The number of hours to allow guest mode to
    be in use.
+   **unenroll_ou**: The organizational unit into which to move devices as they
    leave the GnG program. This value defaults to the root organizational unit.
+   **return_grace_period**: The grace period (in minutes) between a user
    marking a device as pending return and when we reopen the existing loan.

### (Optional) Customize Images for Button and Banner in Emails

You can upload custom banner and button images to
[Google Cloud Storage](https://cloud.google.com/storage/) to use in the emails
sent by the GnG.

To do this, upload your custom images to Google Cloud Storage via the console by
following
[these instructions](https://cloud.google.com/storage/docs/cloud-console).

Name your bucket and object something descriptive, e.g.
`https://storage.cloud.google.com/[BUCKET_NAME]/[OBJECT_NAME]`.

The recommended banner image size is 1280 x 460 and the recommended button size
is 840 x 140. Make sure the `Public Link` checkbox is checked for both of the
images you upload to Cloud Storage.

Next, click on the image names in the console to open the images and copy their
URLs. Take these URLs and populate them as values for the variables
`img_banner_primary` and `img_button_manage` in the `config_defaults.yaml` file.

### (Optional) Customize Events and Email Templates in the GnG Datastore

This YAML file contains the event settings and email templates that the
bootstrap process imports into Cloud Datastore after first launch:

`loaner/web_app/backend/lib/bootstrap.yaml`

#### Core Events

Core events (in the `core_events` section) are events that GnG raises at runtime
when a particular event occurs. For example, the assignment of a new device or
the enrollment of a new shelf. The calls to raise events are hard-coded and the
event names in the configuration YAML file must correspond to actions defined in
the `loaner/web_app/backend/actions` directory.

Specifically, each event can be configured in the datastore to call zero or more
actions and these actions are defined by the modules contained in the
`loaner/web_app/backend/actions` directory. Each of these actions will be run as
an
[App Engine Task](https://cloud.google.com/appengine/docs/standard/python/taskqueue/),
which allows them to run asynchronously and not block the processing of GnG.

While GnG contains several pre-coded actions, you can also add your own. For
example, you can add an action as a module in the
`loaner/web_app/backend/actions` directory to interact with your organization's
ticketing or inventory system. If you do this, please be sure to add or remove
the actions in the applicable events section in the YAML file.

When bootstrapping is complete, this YAML will have been imported and converted
into Cloud Datastore entities — you'll need to make further changes to those
entities.

#### Custom Events

Custom events (in the `custom_events` section) are events that GnG raises as
part of a regular cron job. These events define criteria on the Device and Shelf
entities in the Cloud Datastore. GnG queries the Datastore using the defined
criteria and raises Action tasks, just as it does for Core events.

The difference is that GnG uses the query to determine which entities require
these events. For example, you can specify that Shelf entities with an audit
date of more than three days ago should trigger an email to a management team
and run the corresponding actions that are defined for that event.

The custom events system can access the same set of actions as core events.

#### Reminder Events

Reminder events (in the `reminder_events` section) define criteria for device
entities that trigger reminders for a user. For example, that their device is
due tomorrow or is overdue. These events are numbered starting with 0. You can
customize the events as need be.

**Note**: If you customize any event, be sure to change the neighboring events,
too. Reminder events must not overlap with each other. If so, reminders may
provide conflicting information to borrowers.

The reminder events system can access the same set of actions as core and custom
events.

#### Shelf Audit Event

Shelf audit events (in the `shelf_audit_events` section) are events that are
triggered by the shelf audit cron job. GnG runs a single Shelf audit event by
default, but you can add custom events as well.

#### Email Templates

The `templates` section contains a base email template for reminders, and
higher-level templates that extend that base template for specific reminders.
You can customize the templates.
