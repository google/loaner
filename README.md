<!-- mdformat off(GitHub header) -->
Grab n Go Loaners
[![Build Status](https://travis-ci.org/google/loaner.svg?branch=master)](https://travis-ci.org/google/loaner)
======
<!-- mdformat on -->

<p align="center">
  <a href="#grabngo--">
    <img src="https://storage.googleapis.com/gngloaners/gnglogo.png" alt="Grab n Go Icon" />
  </a>
</p>

The Grab n Go (GnG) Loaner project is a fully automated loaner management suite
that manages enterprise enrolled Chrome OS devices by automatically assigning,
returning, and monitoring these devices.

Using the GnG project, enterprise users can self-checkout a loaner Chromebook
and begin using it right away, thereby decreasing the workload on IT support
while keeping users productive.

The program is comprised of three parts:

*   An enterprise G Suite domain
*   A Google App Engine (GAE) application
*   A Chrome App that runs on each Chrome OS device

## Current release: [Alpha (v0.7.1a)](https://github.com/google/loaner/tree/Alpha-(0.7.1))

Please note that the current release of this application is in ALPHA.
We will be actively contributing to the project. Please keep an eye out for
future updates and features!

To clone this release run the following command:

```
git clone -b Alpha-\(0.7\) https://github.com/google/loaner.git
cd loaner
```

* To discuss this project send an email to loaner@googlegroups.com.
* Read more about releases in our [release notes](docs/release_notes.md).
* Please file bugs using the GitHub issue tracker.

## Technical Stack

*   Chrome App
    -   Angular/TypeScript
*   Frontend
    -   Angular/TypeScript
*   Backend
    -   Python
    -   GAE
    -   Endpoints Frameworks
    -   Datastore (for app state data)
    -   BigQuery (for historical data)
    -   Cloud Storage (for image assets)
    -   Google Admin API
*   Build Automation
    -   Bash
    -   Python
    -   Bazel
    -   NPM

## Documentation

To deploy and configure the Grab n Go (GnG) Loaner project, follow the steps
below.

1.  [Setup the Web
    Application](docs/setup_guide.md)
1.  [Deploy the Grab n Go Chrome
    App](docs/deploy_chrome_app.md)
1.  [Configure your G Suite
    Environment](docs/gsuite_config.md)

#### Reference Documentation

-   [Grab n Go APIs](docs/gng_apis.md)
-   [User Guide](docs/user_guide.md)
-   [Frequently Asked
    Questions](docs/faq.md)

## Contributing

We are not accepting external contributions at this time. The current release of
the application is still in alpha. We will be actively contributing to this
project throughout 2018. After this project reaches a 1.0 release, we will begin
accepting external contributions. Please feel free to file bugs and feature
requests using [GitHub's Issue
Tracker](https://github.com/google/loaner/issues).

## Disclaimers

The current release of the application is in active development.

This is **not** an official Google product. This program is not formally
supported and the code is available as-is with no guarantees.

Documentation, including those for end users of this system, is provided in this
repository only as examples of the "out of box" experience for the app and does
not account for any modifications made by the administrator in deploying the
app. Administrators should review and adjust all documentation and instructions
found in the app as applicable to their deployment.
