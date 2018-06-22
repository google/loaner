# Release notes




## Notes on Master branch
If you are planning on deploying this program for use on your domain we
recommend pulling from one of the branched releases as opposed to the master
branch. While we try to keep the master branch working we consider it
"unstable" and don't recommend using it unless you want to develop for the
project.

## [Alpha 0.6a](https://github.com/google/loaner/tree/Alpha-(0.6))
Released 06/08/18

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
Released 03/30/18

#### Known issues
* There is no configuration view. Configurations must be changed by calling
  the configuration API manually.
