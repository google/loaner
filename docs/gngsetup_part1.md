# Grab n Go Setup Part 1: Create necessary accounts and computer environments


As you go through this guide, you may find that you already have some of these
prequisites in place, like a G Suite account for your company. If this is the
case, you can skip to the next relevant step.



## Step 1: Get G Suite and Chrome for Enterprise

+   [Get a G Suite account for your company](https://gsuite.google.com/intl/en_in/setup-hub/)

    Logging into a loaner Chromebook requires a Google G Suite account, standard
    Gmail accounts won't work.

+   [Get Chrome for Enterprise](https://cloud.google.com/chrome-enterprise/)

## Step 2: Set up an App Engine Project in Google Cloud

GnG runs on Google App Engine, an automatically scaling, sandboxed computing
environment that runs on Google Cloud.

1.  [Create a Google Cloud Platform Project](https://cloud.google.com/resource-manager/docs/creating-managing-projects).

    Name the project something you will remember, such as *loaner*.

1.  [Create a billing account](https://cloud.google.com/billing/docs/how-to/manage-billing-account)
    and
    [enable billing for the project](https://cloud.google.com/billing/docs/how-to/modify-project)
    that you created.

1.  [Create an OAuth2 Client ID within your App Engine Project](https://cloud.google.com/endpoints/docs/frameworks/python/creating-client-ids#Creating_OAuth_20_client_IDs)
    (make sure to select the **Web Client** instructons tab).

    For secure authentication, the GnG application uses OAuth2. When you create
    the OAuth2 Client ID, for:

    +   Authorized JavaScript Origins URL, use either:

        +   [Your own custom domain](https://cloud.google.com/appengine/docs/standard/python/mapping-custom-domains)
            OR

        +   Your GCP project ID (found in the project dropdown) followed by
            appspot.com

            For example, if your GCP project ID is "example-123456" then the
            default URL will be https://example-123456.appspot.com

    +   Application type: Select **Public**

1.  [Create a service account its credentials on your G Suite Domain](https://developers.google.com/admin-sdk/directory/v1/guides/delegation)
    (You can leave **Role** blank).

    This is required in order to access the G Suite APIs to move devices to and
    from organizational units, maintain permissions based on Google Groups, etc.

    **When you get the JSON file containing the client secrets for the service
    account,** save it somewhere that you'll be able to find and don't share it
    as it allows access to your G Suite domain user data.

1.  [Delegate domain-wide authority to the service account you created](https://developers.google.com/admin-sdk/directory/v1/guides/delegation).

    In the **One or More API Scopes** field, copy and paste the following list
    of scopes required by GNG:

    `https://www.googleapis.com/auth/admin.directory.device.chromeos,
    https://www.googleapis.com/auth/admin.directory.group.member.readonly,
    https://www.googleapis.com/auth/admin.directory.orgunit,
    https://www.googleapis.com/auth/admin.directory.user.readonly`

1.  [**Enable** the Admin SDK API through Google Cloud Console](https://console.developers.google.com/apis/api/admin.googleapis.com/overview).

    GnG requires the Directory API to manage devices in your G Suite Domain. To
    access the Directory API you need to enable the Admin SDK API.

1.  **Optional:** Follow these instructions (Step 2) again to create Google
    Cloup App Engine projects for DEV and QA instances. It's useful to have
    separate development and QA apps for testing. For steps 2.2 and 2.4, use the
    same accounts that you set up for Prod.

## Step 3: Set up a G Suite role account

In order to give the GnG app domain privileges, you must set up a G Suite role
account for the app to use. This account won't require an additional G Suite
license and will act only as a proxy for the application.

1.  Visit [Google Admin](https://admin.google.com/)
    +   **Name** it something memorable like *loaner-role@example.com*
    +   Set the **password** to something highly complex (a human should never
        log into this account)
    +   It is highly recommended that you also **use 2FA** on this account to
        reduce risk
2.  Give the account the following Admin roles:
    +   Directory Admin
    +   Services Admin
    +   User Management Admin

**Note:** It's recommended that you put this account in an
[Organizational Unit](https://en.wikipedia.org/wiki/Organizational_unit_\(computing\))
that has all G Suite and additional services disabled.

## Step 4: Create a superadmins permission group

In order to set up the GnG application, you'll need to create a superadmin
group, which will have all permissions by default.

1.  [Create a Google Group for superadmins](https://support.google.com/groups/answer/2464926?hl=en).
1.  Add yourself to the superadmin group. This is required for you to be able to
    set up the GnG application.
1.  If you have people in your organization that need to manage GnG loaner
    devices and shelves, add them to the superadmin group.

    Remember the name of this group, as you'll need this later on in the setup.

Additional roles can be created by calling the role API with a custom set of
permissions, depending on what access you'd like to give. You can provide
different Google Groups to manage the users in these roles and they will sync
automatically. You can also manually add users to roles if you do not provide a
group. Just
[add the appropriate users to each group](https://support.google.com/groups/answer/2465464?hl=en&ref_topic=2458761).

## Step 5: Enterprise enroll your Chromebooks

You must
[enterprise enroll](https://support.google.com/chrome/a/answer/1360534?hl=en)
each of your Chromebook loaners.

## Next up:

### [GnG Setup Part 2: Set up the GnG web app](gngsetup_part2.md)
