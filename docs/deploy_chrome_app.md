# Deploy the Grab n Go Chrome App




## Prerequisites

*   [Google Chrome](https://www.google.com/chrome/): GnG has been tested with
    Chrome v64
*   A Linux, macOS, or Windows device
*   [Node Package Manager (NPM)](https://www.npmjs.com/get-npm): GnG has been
    tested with NPM 5.5.1
*   A Text Editor such as [Visual Studio Code](https://code.visualstudio.com/)

## Step 1: Key and Pre-Build the Chrome App

Chrome Apps use a public/private key pair to maintain a static ID in the Chrome
Web Store and during testing. This process requires that you use Google Chrome
to pack the Chrome App before deployment. Part of the process involves
pre-building the Chrome App, which is described below.

1.  Install the node packages required to build the Chrome App:

    ```
    npm install
    ```

1.  To build the Chrome App, run the following command:

    ```
    npm run build:chromeapp:once
    ```

    *This command builds the chrome app so that we can create the public/private
    key pair below*

1.  Once the Chrome App is built, navigate to the `dist` folder in the
    `chrome_app` directory.

    ```
    cd chrome_app/dist
    ```

1.  Open Google Chrome and navigate to **chrome://extensions** in the URL bar.

1.  On the 'Extensions' page, activate the **Developer Mode** option at the top
    right.

1.  Next, select the menu at the top labeled **Pack Extension**.

1.  In the Pack Extension window:

    1.  For **Extension root directory**, select **BROWSE**.
    1.  From the root of the Git repository, navigate to and select the
        `loaner/chrome_app/dist` directory.
    1.  Click the **PACK EXTENSION** button, which will generate the `.crx` and
        the `.pem` files in the `loaner/chrome_app/` directory.

**WARNING**: Do **not** lose this `.pem` file! If you do, you will need to
re-key the Chrome App.

**Note**: The `.crx` file does not need to be saved, as this will be replaced
every time you rebuild the Chrome App.

## Step 2: Upload the GnG Chrome App to the Chrome Web Store for the First Time

Next, we will take the Chrome App and upload it to the Chrome Web Store to
initialize it. Below are the steps you will need to complete.

1.  Copy and paste the `dist.pem` file created in the previous step into the
    `dist` folder, which contains the `manifest.json` for the Chrome App.

1.  Rename the newly copied `dist.pem` file in the `dist` folder to `key.pem`.
    The file **must** have this name to allow uploading and keying of the Chrome
    App.

1.  Zip the `dist` folder and save it somewhere you can easily access. It must
    be a zip file (other archive formats are not recognized).

1.  Go to the [Chrome Web Store Developer
    Dashboard](https://chrome.google.com/webstore/developer/dashboard). You may
    see a warning that you have to pay an access fee ($5 at the time of this
    writing), but you can safely disregard this message.

1.  Click **Add New Item**.

1.  Click **Choose File** and then select the zip of the `dist` folder you
    created previously and click **Upload**.

1.  Populate information about the app. It will require screenshots, icons, and
    other information that is been listed below. You can always adjust these
    later on.

    *   Add a short description to the detailed description.

    *   For the icon, you can use the `gng128.png` file provided in the
        `chrome_app/webstore_assets/` directory.

    *   For screenshots, you can use the `screenshot.png` file provided in the
        `chrome_app/webstore_assets/` directory.

    *   For the small promotion tile image, you can use the `small_tile.png`
        file in the provided in `chrome_app/webstore_assets/` directory.

    *   For category, choose Productivity.

    *   For regions, it is recommended that you select all regions.

    *   Set language to English (US).

    *   Visibility options should be set to private.

    *   Select the everyone at yourdomain.com option.

1.  Click **Publish changes** to publish the Chrome App.

## Step 3: Keying the Chrome App

1.  Return to the [Chrome Web Store Developer
    Dashboard](https://chrome.google.com/webstore/developer/dashboard) and click
    **More Info on your application**.

1.  Copy the contents below the "BEGIN PUBLIC KEY" and above the "END PUBLIC
    KEY" comments.

1.  In your Chrome App's `manifest.json` in the root `chrome_app` folder (not
    the one in the `dist` folder), insert an object named `key` and paste in the
    value you copied (the public key) in to the quoted area.

    E.g.: Place the key object above "oauth2" object and below "icons" object.

    ```json
      "icons": {
        "16": "assets/icons/gng16.png",
        "48": "assets/icons/gng48.png",
        "128": "assets/icons/gng128.png"
      },
      "key": "LONGRANDOMGENERATEDKEYTHATNEEDSTOBEONONELINE",
      "oauth2": { ...
    ```

    NOTE: Make sure the key fits on a single line.

1.  Save `manifest.json`.

1.  Open the `shared/config.ts` file from within the loaner directory and scroll
    to the CHROME_PUBLIC_KEYS section. In this section, you'll paste that same
    public key to the respective environment (eg. if this is your prod app,
    paste the public key into the prod's quoted value). This is how the Chrome
    App will determine which API to target.

    NOTE: Make sure the key fits on a single line.

1.  Be sure that you have stored the `key.pem` file in a secure place and that
    you have removed it from the `dist` folder. If the `key.pem` file is located
    here in future uploads, you may be denied access unless you are re-keying
    the Chrome App.

Each time that you build locally and upload to the Chrome Web Store, the app ID
remains a constant. This is important when working with technologies such as
OAuth to ensure that the Chrome App is properly authorized to complete certain
tasks.

## Step 4: Defining the OAuth Client for the Chrome App in Google Cloud

To communicate between the Chrome App and the API, generate credentials for
OAuth.

> IMPORTANT: Requirements:
>
> *   A project for the loaner back-end must already exist on Google Cloud (the
>     project does not need to be live)
> *   Your Chrome App **must** be published to the Chrome Web Store

To define the OAuth client:

1.  Go to the [Google Cloud Console](https://console.cloud.google.com).
1.  Go to the _APIs & Services" > "Credentials_.
1.  Click **Create Credential > OAuth Client ID**.
1.  For application type, select **Chrome App**.
1.  Give it an easy to remember name, such as "GnG Chrome App".
1.  Paste the app ID from the Chrome Developer Dashboard. The app ID can be
    found by clicking **more info** and is listed as **Item Id**, just above
    Public key you copied earlier.
1.  Click Create.
1.  Copy the OAuth Client ID that pops up and paste it into the
    `chrome_app/manifest.json`. e.g.:

    ```
    "oauth2": {
       "client_id": "PUT THE GENERATED CLIENT ID HERE",
       "scopes": [
        "https://www.googleapis.com/auth/userinfo.email"
       ]
    }
    ```

1.  In `web_app/` reopen constants.py and find the **CHROME_APP_CLIENT_ID**
    setting and paste the Client ID in there as well. Save the constants file
    and re-deploy the web app using the `deploy.sh` script while in the
    `loaner/deployments` directory (relative to the root of the Git repository):

    ```
    cd loaner/deployments
    bash deploy.sh web prod
    ```

    **Reminder:** While you are editing this file change BOOTSTRAP_ENABLED to
    `False`. Be sure to do this only *after* you complete the initial bootstrap
    (which you should have done in the Setup Guide). Setting this constant to
    `False` will prevent unexpected bootstraps in the future (a bootstrap will
    cause data loss).

**NOTE:** You will need to migrate all of your traffic in the [App
Engine>Versions](https://console.cloud.google.com/appengine/versions) menu to
the newest version every time you re-deploy the app. You can do so by selecting
the new version's checkbox, and clicking **Migrate Traffic** for each service
(i.e. default, action system, chrome, endpoints). Once you are certain the new
version is working properly, you can delete the old one(s) to save resources.

Your Chrome App can now use OAuth to communicate with the API.

## Step 5: Whitelist the API to Bypass OAuth Prompts

To avoid prompting users to grant access to their email addresses, whitelist
the API client and the scopes. It is important to do this for your domain
because if the Chrome App cannot collect email addresses automatically, it will
not be able to assign devices.

1.  Open the [Manage API client
    access](https://admin.google.com/ManageOauthClients) menu in Google Admin.
1.  Paste the Client ID you generated in the previous section as the Client
    Name.
1.  For scope, use:

    ```
    https://www.googleapis.com/auth/userinfo.email
    ```

1.  Click **Authorize**.

## Step 6: Update the API URL and Troubleshooting Info in the Configuration File

We'll now update the API URL to allow the Chrome App to communicate with the
backend. Additionally, we will set the troubleshooting information for the
Chrome App.

**View of the default troubleshooting page for the Chrome App:** ![Chrome App's
troubleshooting page](images/ca_troubleshoot.png)

Edit the configuration file:

1.  Open `shared/config.ts` in an editor.

1.  In the `shared/config.ts` file, find the variable named
    `TROUBLESHOOTING_INFORMATION`:

    *   This field should be treated as a description for the troubleshooting
        page in the Chrome App's management view. You should update this field
        if the default description does not work for your organization.

1.  Find the variable named `IT_CONTACT_PHONE`:

    *   Enter your IT department's phone number, otherwise leave it blank.

1.  Find the variable named `IT_CONTACT_WEBSITE`:

    *   Enter your IT department's website, otherwise leave it blank.

1.  Find the variable named `IT_CONTACT_EMAIL`:

    *   Enter your IT department's email, otherwise leave it blank.

1.  Save and close the file.

## Step 7: Add your FAQ to the Chrome App (optional)

The Chrome App's management view allows for FAQ to be displayed in the FAQ tab.
The Chrome App will use the standard markdown format to display these FAQs.

**View of the default FAQ page for the Chrome App:** ![Chrome App's FAQ
page](images/ca_faq.png)

To add content to the FAQ section:

1.  You can edit the contents of our provided `chrome_app/src/app/assets/faq.md`
    file using [the markdown
    format](https://guides.github.com/features/mastering-markdown/) to what you
    want to see in your FAQ tab in the Chrome App.

    *   If you want some examples of how the FAQ works on the Chrome App, you
        can visit the included `chrome_app/src/app/assets/faq.md` file and look
        at the examples we have included.

**NOTE**: Anytime you need to make changes to the FAQ section, you will have to
update this file using the steps as listed above to modify the file.

## Step 8: Deploy to the Chrome Web Store

The Chrome App is now configured and ready to communicate with the backend
running on Google App Engine (GAE). Now, we can deploy it to the Chrome Web
Store.

To deploy the Chrome App:

1.  Run the following command from the loaner directory (relative to the root of
    the Git repository):

    ```
    bash deployments/deploy.sh chrome prod
    ```

1.  Follow the prompts. Be sure to increment the version number when prompted
    relative to the version of the Chrome App as it currently exists in your
    Chrome Web Store Developer Dashboard. For example, if the current Chrome Web
    Store version is 0.0.1, the new version would be 0.0.2.

1.  When the app is finished building, open the app on the [Web Store Developer
    Dashboard](https://chrome.google.com/webstore/developer/dashboard) and click
    **Edit**, then click **Upload Updated Package** to upload the zip folder
    (loaner_chrome_app.zip) that was just created in the root of the workspace.
    Once the file has uploaded, click **Publish changes** all the way at the
    bottom right in the edit page. Whenever you deploy a Chrome App, you need to
    promote it to the current version on the Chrome Web Store Developer
    Dashboard.

**NOTE**: When publishing Chrome Apps, allow at least 30 minutes for the new
version to become available. In addition, it can take up to 24 hours for the
Chrome App to be updated on your Chrome OS fleet.

## Step 9: Deploy Chrome App

In order to deploy the Chrome App to your Chrome OS fleet, continue to follow
the instructions at: [Configure the G Suite Environment](gsuite_config.md).
