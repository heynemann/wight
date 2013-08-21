CLI Usage
=========

Running the Wight CLI is as simple as::

    $ wight --help

This will show you the full list of commands (a summary of this page).

To run a wight command, like `list` for example::

    $ wight list

Target Commands
---------------

The target is the endpoint the CLI will use to connect to wight.

target-set
~~~~~~~~~~

Sets target for wight to use. It requires an url as positional argument. *Do not forget http:// (or https://).*

Example::

    $ wight target-set http://api.wight.com

    Wight target set to 'http://api.wight.com'. In order to login with wight, use 'wight login <email>'.

target-get
~~~~~~~~~~

Gets the target wight is using currently.

Example::

    $ wight target-get

    Current Wight target is 'http://api.wight.globoi.com'. In order to login with wight, use 'wight login <email>'.

Authentication Commands
-----------------------

In order to use the CLI, users need to authenticate with Wight, as well as be part of a team (more on that in the Team Commands section).

login
~~~~~

Logs in to Wight. Wight will keep your current authentication token in your home folder, meaning you won't have to login again until your token expiration.

If your user is not registered, Wight will ask you if you want to create a new account.

Example of registering a new account::

    $ wight login test@gmail.com

    Please enter the password to authenticate with (nothing will be displayed):
    User does not exist. Do you wish to register? [y/n] y

    User registered and authenticated.

Example of authenticating::

    $ wight login test@gmail.com

    Please enter the password to authenticate with (nothing will be displayed):

    Authenticated.

change-password
Changes user password.

default-get
Shows the defined default team and/or project.

default-set
Define default team and/or project to be used in subsequent commands.

list
List load tests.

project-create
Creates a project.

project-delete
Deletes a project.

project-update
Updates a project.

schedule
Schedules a new load test.

show
Show load tests.

show-result
Show load test results.

team-adduser
Adds user to a team

team-create
Create a team.

team-delete
Delete a team.

team-removeuser
Removess user from a team

team-show
Show the registered team information.

team-update
Updates a team.

user-info
Shows user info
