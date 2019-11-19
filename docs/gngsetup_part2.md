# Grab n Go Setup Part 2: Set up the GnG web app




## About

The Grab n Go (GnG) web app makes it easy to manage a fleet of loaner Chromebook
devices. Using GnG, users can self-checkout a loaner Chromebook and begin using
it right away, thereby decreasing the workload on IT support while keeping users
productive.

## Step 1: Set up a development computer

This computer will be the device that you'll modify the code, and build and
upload GnG from.

**Note:** This deployment has only been tested on Linux and macOS.

**Warning:** You must install Bazel 0.26 or earlier as this configuration is
incompatible with Bazel 0.27 and later.

Install the following software:

+   [Git](https://git-scm.com/downloads)
+   [Bazel 0.26.1](https://github.com/bazelbuild/bazel/releases/tag/0.26.1)
+   [Google Cloud SDK](https://cloud.google.com/sdk/)
+   [NPM](https://www.npmjs.com/get-npm)

## Step 2: Clone the GnG loaner source code

Clone the GnG loaner source code by running the command for the current release,
found in the
[Current Release section of the README](README.md).

**Note:** This setup guide assumes that your working directory is the root of
the Git repository.

## Step 3: Customize the App Deployment Script

1.  In `loaner/deployments/deploy.sh`, find `PROD="prod=loaner-prod"` and
    replace `loaner-prod` with the Google Cloud Project ID you created.
1.  If you created multiple projects for QA and DEV, replace the `loaner-dev`
    and `loner-qa` with the relevant Google Cloud Project IDs.

## Step 4: Customize the BUILD Rule for deployment

1.  Find the client secret file for the service account you created earlier and
    rename it `client-secret.json`
1.  Move `client-secret.json` into `loaner/web_app`

    If you are using Cloud Shell or a remote computer, you can copy and paste
    the contents of the file.

1.  In `loaner/web_app/BUILD`, update following section of code:

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

## Step 5: Customize the App Constants

Constants are variables you typically define once. For a constant to take
effect, you must deploy a new version of the app. Constants can’t be configured
in a running app. Instead, they must be set manually in
`loaner/web_app/constants.py` and `loaner/shared/config.ts`.

1.  In `loaner/web_app/constants.py`, configure the following constants:

    +   `APP_DOMAINS`: Use the Google domain that you run G Suite with Chrome
        Enterprise. You can add a list of other domains that you would like to
        have access to this deployment of Grab n Go, but they must be listed
        after the Google domain that you run G Suite with Chrome Enterprise.

        **If you'd like to run this program on more than one domain**, see the
        "Multi-domain Support" section at the bottom of this doc.

    +   `ON_PROD`: Replace the string `prod-app-engine-project` with the Google
        Cloud Project ID the production version of GnG will run in.

    +   `ADMIN_EMAIL`: Use the email address of the G Suite role account you set
        up.

    +   `SEND_EMAIL_AS`: Use the email address within the G Suite Domain that
        you want GnG app email notifications to be sent from.

    +   `SUPERADMINS_GROUP`: Use the Google Groups email address that contains
        at least one Superadmin in charge of configuring the app.

    +   `WEB_CLIENT_ID`: Use the OAuth2 Client ID you created previously for the
        production version of GnG. In your Cloud Project, this can be found in
        **APIs and Services > Credentials**.

    +   `SECRETS_FILE`: Set this equal to `loaner/web_app/client-secret.json`

        The remaining ON_QA and ON_DEV are only required if you choose to use
        multiple versions to test deployments before promoting them to the
        production version.

    +   **Optional:** `CUSTOMER_ID`: Use the unique ID for your organization's G
        Suite account, which GnG uses to access Google's Directory API. If this
        is not configured the app will use the helper string `my_customer` which
        will default to the G Suite domain the app is running in.

1.  In `loaner/shared/config.ts`, configure the following:

    +   `Export const PROD`: Replace `'prod-app-engine-project'` with the Google
        Cloud Project ID the production version of GnG will run in.

    +   `WEB_CLIENT_IDS`: Use the OAuth2 Client ID you created previously. In
        your Cloud Project, this can be found in **APIs and Services >
        Credentials**. If you are deploying a single instance of the
        application, fill in the PROD value with the Client ID.

    +   `STANDARD_ENDPOINTS`: If you're using a custom Domain, replace the URL
        with your domain. Other you can leave this as is. If you are deploying a
        single instance of the application, use that value for all fields.
        Otherwise, specify your separate prod, qa and dev endpoint URLs.

## Step 6: Build and Deploy

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

## Step 7: Confirm that GnG is Running

In the Cloud Console under _App Engine > Versions_ the GnG code that you just
built and pushed should appear.

To display all four services, click the _Service_ drop-down menu:

+   **`default`** is the main service, which interacts with the web frontend
+   **`action-system`** runs the cron jobs that spawn Custom and Reminder events
    and process the resulting Action tasks
+   **`chrome`** is the service that handles heartbeats from the Chrome app
+   **`endpoints`** handles API requests via Cloud endpoints for all API clients
    except Chrome app heartbeats

## Step 8: Bootstrapping

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

### [Grab n Go Setup Part 3: Deploy the Grab n Go Chrome app](gngsetup_part3.md)
