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

## Important notice about Chrome Apps!
**Note:** [Chrome Apps are being phased out in favor of extensions and progressive web apps](https://blog.chromium.org/2020/01/moving-forward-from-chrome-apps.html)

**If you haven't yet deployed Grab and Go to the Chrome Web Store**

Enterprise/EDU customers can continue to deploy Chrome Apps to the Chrome
Web Store using the guidance we've provided (specifically unlisted/private
hosting in the Chrome Web Store) in the documentation for the forseeable future.

**If you have deployed Grab and Go to the Chrome Web Store**

You should be in good shape for now! Existing Enterprise/EDU Chrome Apps (Grab
and Go included) are not in-scope until June 2022 according to the announcement
linked above.

## Current release: [Alpha (v0.7.1a)](https://github.com/google/loaner/tree/Alpha-(0.7.1))

**Note: If you are doing a new deployment please deploy from master as we work
on cutting a new release. For current deployments, please hold off on upgrading
until we can test the next numbered release.**

Please note that the current release of this application is in ALPHA.
We will be actively contributing to the project. Please keep an eye out for
future updates and features!


**Note:** To build this project you must install Bazel 0.26. Currently
Bazel 0.27 or later is unsupported.

To use the **latest code (also known as master)**, run the following
command:

```
git clone https://github.com/google/loaner.git
cd loaner
```

To use release number **0.7.1**, run the following command:

```
git clone -b Alpha-\(0.7.1\) https://github.com/google/loaner.git
cd loaner
```

* To discuss this project send an email to loaner@googlegroups.com. Please note
  that this group is public (anyone can view/post).
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

+  [Part 1: Create necessary accounts and computer environments](docs/gngsetup_part1.md)
+ [Part 2: Set up the GnG web app](docs/gngsetup_part2.md)
+ [Part 3: Deploy the Grab n Go Chrome app](docs/gngsetup_part3.md)
+ [Part 4: Configure the G Suite Environment](docs/gngsetup_part4.md)


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
