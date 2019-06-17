# Grab n Go Setup Part 2: Set up the GnG web app




## About

The Grab n Go (GnG) web app makes it easy to manage a fleet of loaner Chromebook
devices. Using GnG, users can self-checkout a loaner Chromebook and begin using
it right away, thereby decreasing the workload on IT support while keeping users
productive.

While the following skills are not explicitly required, you should be
comfortable referencing the documentation for each of these to troubleshoot
deployments of GnG:

+   **[Know some Python](https://www.python.org/).** \
    To customize the GnG backend, you’ll use Python 2.7.

+   **[Know some Angular and Typescript](https://angular.io/).** \
    To modify the GnG frontend and Chrome App, you will use Angular with
    Typescript.

+   **[Learn the Basics of Google App Engine](https://cloud.google.com/appengine/docs/standard/python/).**
    \
    Although GnG is mostly set up, it is helpful to know the App Engine
    environment should you want to customize it.

+   **[Learn Git](https://git-scm.com/).** \
    If you have not used Git before, become familiar with this popular version
    control system. You will clone the repository with Git.

## Configuration

Use Git to make a copy of the GnG loaner source code, the command to run for the
current release can be found on the
[README](README.md).

**Note**: The rest of this setup guide assumes that your working directory will
be the root of the Git repository.

### Customize the App Deployment Script

In the `loaner/deployments` directory, edit `deploy.sh` and change the instances
(`PROD`, `QA` and `DEV`) to the Google Cloud Project ID(s) you've created for
your app. If you've only created one project, assign the project ID to `PROD`.
We find it useful to have separate development and qa apps for testing, but
these are optional.

### Customize the BUILD Rule for Deployment

The source code includes a `WORKSPACE` file to make it a
[Bazel workspace](https://docs.bazel.build/versions/master/build-ref.html#workspaces).

The client secret file for the service account you created earlier must be moved
into your local copy of the GnG app inside the `loaner/web_app` directory. If
you are using Cloud Shell or a remote computer, you can simply copy and paste
the contents of the file. A friendly name is suggested e.g.
`client-secret.json`. Once the file has been relocated to this directory, the
BUILD rule in `loaner/web_app/BUILD` named "loaner" must have a
[data dependency](https://docs.bazel.build/versions/master/build-ref.html#data)
that references the `client-secret.json` file.

```
    loaner_appengine_library(
        name = "loaner",
        data = ["client-secret.json"],  # Add this line.
        deps = [
            ":chrome_api",
            ":endpoints_api",
            ":main",
            "//loaner/web_app/backend",
        ],
    )
```

### Customize the App Constants

Constants are variables you typically define once. For a constant to take
effect, you must deploy a new version of the app. Constants can’t be configured
in a running app. Instead, they must be set manually in
`loaner/web_app/constants.py` and `loaner/shared/config.ts`.

Before you deploy GnG, the following constants must be configured:

#### loaner/web_app/constants.py

+   **`APP_DOMAINS`** is a list of domains you would like to have access to this
    deployment of Grab n Go. The primary domain should be listed first, this is
    the Google domain in which you run G Suite with Chrome Enterprise. For
    example, if you arrange G Suite for the domain `mycompany.com` use that
    domain name as the first value in this list constant.

    Note: If you'd like to run this program on more than one domain, please see
    the "Multi-domain Support" section at the bottom of this doc.

+   **`ON_PROD`** is the Google Cloud Project ID the production version of GnG
    will run in. You need to replace the string 'prod-app-engine-project' with
    the ID of your project.

+   **`ADMIN_EMAIL`** the email address of the G Suite role account you set up.
    Usually loaner-role@example.com.

+   **`SEND_EMAIL_AS`** is the email address within the G Suite Domain that GnG
    app email notifications will be sent from.

+   **`SUPERADMINS_GROUP`**: The Google Groups email address that contains at
    least one Superadmin in charge of configuring the app.

Within the `if ON_PROD` block are the required constants to be configured on the
Google Cloud Project you will be using to host the production version of GnG:

+   **`CHROME_CLIENT_ID`** the Chrome App will use this to authenticate to the
    production version of GnG. **Leave this blank for now, you'll generate this
    ID later.**

+   **`WEB_CLIENT_ID`** is the OAuth2 Client ID you created previously that the
    Web App frontend will use to authenticate to the production version of GnG.

+   **`SECRETS_FILE`** is the location of the Directory APIs service account
    secret json file relative to the Bazel WORKSPACE. If using the example above
    for the BUILD rule the constant would look like this:

    SECRETS_FILE = 'loaner/web_app/client-secret.json'

The remaining ON_QA and ON_DEV are only required if you choose to use multiple
versions to test deployments before promoting them to the production version.

+   **`CUSTOMER_ID`** is the (optional) unique ID for your organization's G
    Suite account, which GnG uses to access Google's Directory API. If this is
    not configured the app will use the helper string `my_customer` which will
    default to the G Suite domain the app is running in.

+   By default, **`BOOTSTRAP_ENABLED`** is set to `True`. This constant unlocks
    the bootstrap functionality of GnG necessary for the initial deployment.

    **WARNING:** Change this constant to `False` *after* you complete the
    initial bootstrap. Setting this constant to `False` will prevent unexpected
    bootstraps in the future (a bootstrap will cause data loss).

#### shared/config.ts

+   **`PROD`** is the Google Cloud Project ID that the production version of GnG
    will operate in. You will need to replace the string
    'prod-app-engine-project' with the ID of your project. This is the same ID
    used for ON_PROD in loaner/web_app/constants.py.

+   **`WEB_CLIENT_IDS`** is the OAuth2 Client ID you created previously that the
    Web App frontend will use to authenticate to the backend. This is the same
    ID that was used for the WEB_CLIENT_ID in loaner/web_app/constants.py. If
    you are deploying a single instance of the application, fill in the PROD
    value with the Client ID.

+   **`STANDARD_ENDPOINTS`** is the Google Endpoints URL the frontend uses to
    access your backend API. If necessary, update the `prod`, `qa` and `dev`
    values.

    *   (*optional*) If you are deploying a single instance of the application,
        use that value for all fields. Otherwise, specify your separate prod, qa
        and dev endpoint URLs.

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

## Build and Deploy

1.  Go to the `loaner/` directory and launch the GnG deployment script:

    ```
    cd loaner
    bash deployments/deploy.sh web prod
    ```

    **Note**: If you are running `deploy.sh` on Linux, you may need to install
    `node-sass` using `npm` manually using the following command:

    ```
    npm install --unsafe-perm node-sass
    ```

    This command builds the GnG web application GnG and deploys it to prod using
    gcloud.

    The `deploy.sh` script also includes other options:

    ```
    bash deployments/deploy.sh (web|chrome) (local|dev|qa|prod)
    ```

1.  App Engine's SDK provides an app named `dev_appserver.py` that you can use
    to test the app on your local development machine. To do so, build the app
    manually and then use `dev_appserver.py` from the output directory like so:

    ```
    bash loaner/deployments/deploy.sh web local
    cd ../bazel-bin/loaner/web_app/runfiles.runfiles/gng/
    dev_appserver.py app.yaml
    ```

### Confirm that GnG is Running

In the Cloud Console under _App Engine > Versions_ the GnG code that you just
built and pushed should appear.

To display all four services, click the _Service_ drop-down menu:

+   **`default`** is the main service, which interacts with the web frontend
+   **`action-system`** runs the cron jobs that spawn Custom and Reminder events
    and process the resulting Action tasks
+   **`chrome`** is the service that handles heartbeats from the Chrome app
+   **`endpoints`** handles API requests via Cloud endpoints for all API clients
    except Chrome app heartbeats

### Bootstrapping

The first time you visit the GnG Web app you will be prompted to bootstrap the
application. You can only do this if you're a technical administrator, so make
sure you've added your account to the correct group `technical-admins` group you
defined previously. Bootstrapping the app will set up the default configurations
and initialize the connection to [BigQuery](https://cloud.google.com/bigquery/)
and the [Directory API](https://developers.google.com/admin-sdk/directory/).
After the app has been successfully bootstrapped, make sure to edit the
`constants.py` file and set `bootstrap_enabled` to `False` so that you don't
accidentally overwrite your configuration.

**Note**: The bootstrap process may take a few minutes to complete.

#### Create an Authorized Email Sender

You need to configure an authorized email sender that GnG emails will be sent
from, e.g. loaner@example.com. To do that, add an
[Email API Authorized Senders](https://console.cloud.google.com/appengine/settings)
in the GCP Console.

#### Deploy the Chrome App

After bootstrapping is complete, you will need to set up the GnG Chrome App.
This app helps configure the Chromebooks you will be using as loaners and
provides the bulk of the user-facing experience. Continue on to
[deploying the chrome app](gngsetup_part3.md).

#### Multi-domain Support (Optional).

WARNING: This functionality is considered unstable. Use with caution and report
any bugs using GitHub's issue tracker.

If you want to support more than one managed domain on loaner devices please
follow the steps below. Please note, the domains you want to support must be
part of the same G Suite account and added to admin.google.com via Account >
Domains > Add/Remove Domains. Different domains managed by different G Suite
accounts and public Gmail addresses are not supported.

+   The domains you want to support must be added to the App Engine project from
    console.cloud.google.com via App Engine > Settings > Custom Domains.
+   In App Engine > Settings > Application settings "Referrers" must be set to
    Google Accounts API. WARNING: Setting this allows any Google managed account
    to try and sign into the app. Make sure you have the latest version of the
    code deployed or you could be exposing the app publicly.
+   In the application's code in web_app/constants.py the variable APP_DOMAINS
    should be a list of all the domains you plan on supporting.
+   Go to admin.google.com and in Devices > Chrome Management > Device Settings
    find the Grab n Go parent OU and set Sign-in Restriction to the list of
    domains you're supporting. Optionally, you may also want to switch off the
    Autocomplete Domain option as it may cause some confusion (it's not very
    intuitive that you can override the sign-in screen by typing your full email
    address).

#### Datastore backups (Optional, but Recommended).

A cron is used to schedule an automatic export of the Google Cloud Datastore
entities for backup purposes. The export is done directly to a Google Cloud
Storage bucket.

Requirements:

+   [Create a Cloud Storage bucket for your project](https://cloud.google.com/storage/docs/creating-buckets).
    All exports and imports rely on Cloud Storage. You must use the same
    location for your Cloud Storage bucket and Cloud Datastore. For example, if
    you chose your Project location to be US, make sure that same location is
    chosen when creating the bucket.
+   [Configure access permissions](https://cloud.google.com/datastore/docs/schedule-export#setting_up_scheduled_exports)
    for the default service account and the Cloud Storage bucket created above.
+   Enter the name of the bucket in the configuration page of the application.
+   Toggle datastore backups to on in the configuration page of the application.

NOTE: Please review the
[Object Lifecycle Management](https://cloud.google.com/storage/docs/lifecycle)
feature of Cloud Storage buckets in order to get familiar with retention
policies. For example, policies can be set on GCS buckets such that objects can
be deleted after a specified interval. This is to avoid additional costs
associated with Cloud Storage.

## Next up:

### [Grab n Go Setup Part 3: Deploy the Grab n Go Chrome app](docs/gngsetup_part3.md)
