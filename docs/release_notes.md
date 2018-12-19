# Release notes




## Notes on Master branch
If you are planning on deploying this program for use on your domain we
recommend pulling from one of the branched releases as opposed to the master
branch. While we try to keep the master branch working we consider it
"unstable" and don't recommend using it unless you want to develop for the
project.

## [Alpha 0.7.1](https://github.com/google/loaner/tree/Alpha-(0.7.1))
Released 2018-12-19

#### Features added
* No major functionality has been added, but this release includes many
  bug fixes and stability improvements.
* This release includes the framework of our new deployment system that we will
  continue to build on in 2019. While there is no added functionality yet it
  will soon be the easiest way to automatically configure, deploy, and update
  your GnG experience.

#### Known issues
* You must manually [create the GSuite Chrome organizational units](gsuite_config.md)
  as the app cannot yet create them.
* You may need to run 'npm install' to update to the latest NPM packages.
* There may be additional incompatibilities with older versions of this app. If
  you experience any problems please use GitHub's issue tracker.

## [Alpha 0.7](https://github.com/google/loaner/tree/Alpha-(0.7))
Released 2018-09-08

Warning: This is a breaking change. If you are running earlier versions of the
app you will need to take the following steps after upgrading for the app to
continue functioning correctly.

1. Open the `shared/config.ts` file from within the loaner directory and scroll
   to the CHROME_PUBLIC_KEYS section. In this section, you'll paste the value
   from the key field in the `chrome_app/manifet.json` (the public key of the
   Chrome App) to the respective environment (eg. if this is your prod app,
   paste the public key into the prod's quoted value). This is how the Chrome
   App will determine which API to target.

   NOTE: Make sure the key fits on a single line.
1. Save the file and follow the [Deploy to the Chrome Web Store](deploy_chrome_app.md)
   steps to update the application.

#### Features added
* Added configuration view so that configurations can be dynamically updated
  without redeploying the app.
* Settings are now loaded into datastore by default during bootstrap.
* Animations and additional assets have been added.
* Adds limited support for multiple domains as long as they're controlled by the
  same G Suite account. This feature is still considered unstable. See the
  "Multi-domain Support" section of the [Setup Guide](setup_guide.md)
  for more information.

#### Known issues
* You must manually [create the GSuite Chrome organizational units](gsuite_config.md)
  as the app cannot yet create them.
* There may be additional incompatibilities with older versions of this app. If
  you experience any problems please use GitHub's issue tracker.
* If you are constantly redirected to the bootstrap screen you may need to go
  into Datastore and select "Config" in the dropdown menu and set
  bootstrap_completed to true.

## [Alpha 0.6a](https://github.com/google/loaner/tree/Alpha-(0.6))
Released 2018-06-08

Warning: This is a breaking change. If you are running earlier versions of the
app you will need to take the following steps after upgrading for the app to
continue functioning correctly.

1. Open your project in [Cloud Console](http://console.cloud.google.com) and
navigate to Datastore > Entities.
1. In the Kind dropdown select User.
1. Select all User entities and Delete them.
1. Navigate to App Engine > Memcache.
1. Click the "Flush Cache" button.
1. Navigate to App Engine > Task Queues and select the Cron Jobs tab.
1. Find `/_cron/sync_user_roles` and click "Run now."

#### Features added
* Added Search functionality, you can now search by device, shelf, and user.
* The permissions/roles system has been refactored. Now instead of three static
  roles there's just one pre-defined role (superadmin) that gets all
  permissions. Additional roles can be defined by superadmins and synced with
  groups. For more information about the new system see the APIs doc.
* Device and shelf views now correctly paginate.
* Added support for synchronous actions in addition to async actions.
  Synchronous actions can be attached to many of the same workflows async
  actions can be attached to.

#### Known issues
* You must manually [create the GSuite Chrome organizational units](gsuite_config.md)
  as the app cannot yet create them.
* There is no configuration view. Configurations must be changed by calling
  the configuration API manually.
* There may be additional incompatibilities with older versions of this app. If
  you experience any problems please use GitHub's issue tracker.


## [Alpha 0.5a](https://github.com/google/loaner/tree/Alpha-(0.5))
Released 2018-03-30

#### Known issues
* There is no configuration view. Configurations must be changed by calling
  the configuration API manually.
