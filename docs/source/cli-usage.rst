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

    Current Wight target is 'http://api.wight.com'. In order to login with wight, use 'wight login <email>'.

User Info Commands
------------------

In order to use the CLI, users need to authenticate with Wight, as well as be part of a team (more on that in the Team Commands section).

You can also obtain information about your currently logged-in user, like what teams you are part of or projects you can schedule tests for.

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
~~~~~~~~~~~~~~~

This command allows the currently logged-in user to change his password.

Example::

    $ wight change-password

    Please enter your current password:

    Please enter your new password:

    Please enter your new password again:

    Password changed successfully.

user-info
~~~~~~~~~

Shows user info, like what teams the user is part of or projects he's allowed to schedule tests for.

Example::

    $ wight user-info

    User: bernardo@corp.globo.com
    +----------+-------+
    | team     | role  |
    +----------+-------+
    | timehome | owner |
    +----------+-------+

Team Commands
-------------

Teams are the owners of projects and contain users. They are the unit of organization of everything in Wight.

The commands in this section are responsible for managing teams created in Wight, as well as assigning and removing users to teams.

team-create
~~~~~~~~~~~

Creates a team.

Example::

    $ wight team-create myteam

    Created 'myteam' team in 'http://api.wight.com' target.

team-update
~~~~~~~~~~~

Changes a team's name.

Example::

    $ wight team-update myteam newteam

    Updated 'myteam' team to 'newteam' in 'http://api.wight.com' target.

team-show
~~~~~~~~~

Show general information about the team, like it's members and projects.

Example::

    $ wight team-show newteam

    newteam
    -------

    +---------------------+-------+
    | user                | role  |
    +---------------------+-------+
    | heynemann@gmail.com | owner |
    +---------------------+-------+

    +--------------+----------------------------------------+----------------------+
    | project name | repository                             | created by           |
    +--------------+----------------------------------------+----------------------+
    | myproject    | https://github.com/heynemann/wight.git | heynemann@gmail.com  |
    +--------------+----------------------------------------+----------------------+

team-delete
~~~~~~~~~~~

Deletes a team.

**WARNING: This operation cannot be undone and all the data (teams, projects and tests) for the given team will be removed from Wight.**

Example::

    $ wight team-delete newteam

    This operation will delete all projects and all tests of team 'newteam'.
    You have to retype the team name to confirm deletion.

    Team name:  newteam
    Deleted 'newteam' team, all its projects and tests in 'http://api.wight.com' target.


team-adduser
~~~~~~~~~~~~

Adds an user to a team. Being part of a team means that user gets to see the team test results, as well as schedule new tests.

Example::

    $ wight team-adduser newteam test@gmail.com

    User 'test@gmail.com' added to Team 'newteam'.

team-removeuser
~~~~~~~~~~~~~~~

Removes an user from a team.

Example::

    $ wight team-removeuser newteam test@gmail.com

    User 'test@gmail.com' removed from Team 'newteam'.

Project Commands
----------------

The commands in this section allow for management of the projects in a given team.

project-create
~~~~~~~~~~~~~~

Creates a new project.

Example::

    $ wight project-create myproject --team=myteam --repo=https://github.com/heynemann/wight.git

    Created 'myproject' project in 'myteam' team at 'http://api.wight.com'.

project-update
~~~~~~~~~~~~~~

Updates a project's information, like name or repository.

Example::

    $

project-delete
~~~~~~~~~~~~~~

Deletes a project.



Defaults Commands
-----------------

In order to make it easier to use, Wight allows the user to specify a default team and default project.

When you have the defaults set you don't have to pass them in each command, as before.

default-set
~~~~~~~~~~~

Define default team and/or project to be used in subsequent commands.

Example::

    $ wight default-set --team=myteam --project=myproject

    Default team set to 'myteam'.

    Default project set to 'myproject'.

default-get
~~~~~~~~~~~

Shows the defined default team and/or project.

Example::

    $ wight default-get

    Default team is 'myteam'.

    Default project is 'myproject'.

list
List load tests.

schedule
Schedules a new load test.

show
Show load tests.

show-result
Show load test results.


