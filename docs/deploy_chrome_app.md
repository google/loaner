# Deploy the Grab n Go Chrome OS App


[TOC]

## Prerequisites

*   Google Chrome: GnG has been tested with Chrome v64
*   A Linux, Mac OS, or Windows device
*   [Node Package Manager (NPM)]: GnG has been tested with NPM 5.5.1
*   Text editor: Google recommends [Visual Studio Code]

## Step 1: Key and Pre-Build the Application

Chrome Apps use a public/private key pair to maintain a static ID in the Chrome
Webstore and during testing. This process requires that you use a local Google
Chrome instance to pack the application. Part of the process involves
pre-building the application, which is described below:

1.  Clone the repository from GitHub and `cd` into the project directory if you
    haven't already.

1.  In the root loaner directory, which contains folders such as `chrome_app`
    and `web_app`, run the following commands:

    ```
    npm install
    ```

    *The previous command installs all the node packages required to build the
    application.*

    ```
    npm run build:chromeapp:once
    ```

    *This command builds the chrome app so that we can create the public/private
    key pair below*

1.  Once the application is built, navigate to the `dist` folder in the
    `chrome_app` directory.

    ```
    cd chrome_app/dist
    ```

1.  Open Google Chrome and navigate to **chrome://extensions** in the URL bar.

1.  On the 'Extensions' page, check the box marked **Developer Mode** and click
    the button labeled **'Pack Extension...'**.

1.  In the Pack Extension window:

    1.  For Extension Root Directory, click Browse.
    1.  Go to the `chrome_app/dist` directory you created.
    1.  Click Pack Extension to generate the `.crx` and `.pem` file in the
        chrome_app directory.

**WARNING**: Do **not** lose this PEM file! If you lose the PEM file, you'll
need to re-key the application.

*Note: The CRX file doesn't need to be stored anywhere for safe keeping as this
will be replaced every time you rebuild the application.*

## Step 2: Upload the Pre-Built Application to the Chrome Webstore for the First Time

We'll now take the pre-built application and upload it to the Chrome Webstore to
initialize it. Below are the steps you'll need to complete.

1.  Copy and paste the `dist.pem` file created in the previous step into the
    `dist` folder, which contains the `manifest.json` for the application.

1.  Rename the newly copied `dist.pem` file in the application folder to
    `key.pem`. The file **must** have this name to allow uploading and keying of
    the application.

1.  Zip the `dist` folder and save it somewhere you can easily access. It must
    be a zip file (other archive formats are not recognized).

1.  Go to the [Chrome Webstore Developer
    Dashboard](https://chrome.google.com/webstore/developer/dashboard). You may
    see a warning that you have to pay an access fee ($5 at the time of this
    writing), but you can safely disregard this message.

1.  Click **Add New Item**.

1.  Click **Choose File** and then select the zip file you created previously.
    Upload the file.

1.  Populate information about the app. It will require screenshots, icons, and
    other information that's been listed below. You can always adjust these
    later on.

    *   Add a short description to the detailed description.

    *   For the icon, you can use the **gng128.png** file provided in
        chrome_app/webstore_assets/

    *   For screenshots, you can use the **screenshot.png** provided in
        chrome_app/webstore_assets/

    *   For promotion tile images, you can use **small_tile.png** provided in
        chrome_app/webstore_assets/

    *   For category, choose Productivity

    *   For regions, it's recommended that you select all regions

    *   Set language to English (US)

    *   Visibility options should be set to private

    *   Select the everyone at yourdomain.com option

1.  Click `Publish changes` to publish the application.

## Step 3: Keying the Application

1.  Return to the [Chrome Webstore Developer
    Dashboard](https://chrome.google.com/webstore/developer/dashboard) and click
    **More Info on your application**.

1.  Copy the contents below the "BEGIN PUBLIC KEY" and above the "END PUBLIC
    KEY" comments.

1.  In your application's `manifest.json` in the root `chrome_app` folder (not
    the one in the `dist` folder), create the object named `key` and paste in
    the value you copied (the public key) in to the quoted area.

    Ex: Place the key object above "oauth2" object and below "icons" object.

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

1.  Make sure you've stored the `key.pem` file in a secure place and remove it
    from the `dist` folder. If the `key.pem` file is located here in future
    uploads, you may be denied access unless you are rekeying the application.

When you build locally and upload to the webstore, the app ID remains a
constant. This is important when working with technologies such as OAuth to
ensure that the application is properly authorized to complete certain tasks.

## Step 4: Defining the OAuth Client for the Chrome App in Google Cloud

To communicate between the Chrome App and the API, generate credentials for
OAuth.

> IMPORTANT: Requirements:
>
> *   A project for the loaner back-end must already exist on Google Cloud (the
>     project needn't be live)
> *   Your application **must** be published to the Chrome Webstore

To define the OAuth client:

1.  Go to the [Google Cloud Console](https://console.cloud.google.com).
1.  Go to the "APIs & Services" > "Credentials".
1.  Click **Create Credential > OAuth Client ID**.
1.  For application type, select Chrome App.
1.  Give it an easy to remember name, like "GnG Chrome App"
1.  Paste the application ID from the Chrome Developer Dashboard. The ID is
    located in more info under Item Id, just above Public key you copied
    earlier.
1.  Click Create. The Client ID is created.
1.  In the `chrome_app/manifest.json` modify the oauth2 object with the client
    ID:

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
    and re-deploy the web app using the deploy.sh script while in the
    loaner/deployments directory:

    ```
    ./deploy.sh web prod
    ```

**NOTE:** You will need to migrate all of your traffic in the [App
Engine>Versions](https://console.cloud.google.com/appengine/versions) menu to
the newest version every time you re-deploy the app. You can do so by selecting
the new version's checkbox, and clicking **Migrate Traffic** for each service
(i.e. default, action system, chrome, endpoints). Once you are certain the new
version is working properly, you can delete the old one(s) to save resources.

Your application can now use OAuth to communicate with the API.

## Step 5: Whitelist the API to Bypass OAuth Prompts

To avoid prompting users to grant access to their e-mail addresses, whitelist
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
backend. Additionally, we'll set the troubleshooting information for the Chrome
App.

**View of the default troubleshooting page for the Chrome App:**
![Chrome App's troubleshooting page](../images/ca_troubleshoot.png)

> **Important Requirements**
>
> *   You must have deployed the backend and completed the steps in the [Setup
>     Guide](setup_guide.md)
> *   The backend API URL(s) for Chrome and Endpoints.

With these requirements completed, edit the configuration file:

1.  Open `chrome_app/src/app/config.ts` in an editor.
1.  Near the bottom, under "`@Injectable()`" is class `APIService`:

    *   In this service, you'll see a `chromeEndpoint` and a `standardEnpoint`
        variable.

    *   Update these values with the endpoint URLs uploaded when deploying the
        backend. You can find these URLs in the Google Cloud console by going to
        App Engine > Versions and changing the service from the menu.

    *   (*optional*) If you have a prod environment only, use that value for
        both fields. Otherwise, specify your separate prod and dev endpoint
        URLs.

1.  Find the variable named `TROUBLESHOOTING_INFORMATION`:

    *   This field should be treated as a description for the troubleshooting
        page in the Chrome App's management view. You should update this field
        if the default description does not work for your organization.

1.  Find the variable named `IT_CONTACT_PHONE`:

    *   Enter your IT departments phone number, otherwise leave it blank.

1.  Find the variable named `IT_CONTACT_WEBSITE`:

    *   Enter your IT departments website, otherwise leave it blank.

1.  Find the variable named `IT_CONTACT_EMAIL`:

    *   Enter your IT departments e-mail, otherwise leave it blank.

1.  Save and close the file.

## Step 7: Add your FAQ to the Chrome App (optional)

The Chrome App's management view allows for FAQ to be displayed in the FAQ tab.
The application will use the standard markdown format to display these FAQs.

**View of the default FAQ page for the Chrome App:**
![Chrome App's FAQ page](../images/ca_faq.png)

To add content to the FAQ section:

1.  Edit the contents of our included `chrome_app/src/app/assets/faq.md` file
    using [markdown
    format](https://guides.github.com/features/mastering-markdown/) to what you
    want to see in your FAQ tab in the application.

    *   If you want some examples of how the FAQ works on the Chrome App, you
        can visit the included `chrome_app/src/app/assets/faq.md` file and look
        at the examples we've included.

NOTE: Any time you need to make changes to the FAQ section, you will have to
update this file using the same steps listed above to modify the file.

## Step 8: Deploy to the Chrome Webstore

The app is configured and ready to communicate with the backend.

To deploy the app:

1.  Run the following command from the loaner directory:

    ```
    bash deployments/deploy.sh chrome prod

    ```

1.  Follow the prompts. Be sure to increment the version number when prompted.
    For example, if the current webstore version is 0.0.1, the new version would
    be 0.0.2.

1.  When the app is finished building, open the app on the [Webstore Developer
    Dashboard](https://chrome.google.com/webstore/developer/dashboard) and click
    Edit, then click Upload Updated Package to upload the zip folder
    (loaner_chrome_app.zip) that was just created in the root of the workspace.
    Once the file has uploaded, click **Publish changes** all the way at the
    bottom right in the edit page. Whenever you deploy an application, you need
    to promote it to the current version on the Webstore Developer Dashboard.

NOTE: When publishing applications, allow at least 30 minutes for the new
version to become available. In addition, it can take up to 24 hours for the
application to be updated on deployed devices.

## Step 9: Deploy Chrome App

In order to deploy the Chrome app, follow the instructions for [Configuring G
Suite Environment](gsuite_config.md).
