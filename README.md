# Groups
## Motivation

I wanted to create a website that would automatize the process of splitting into groups for students. 

## Features

The service is divided into two main parts

- standard user interface
- administration panel

The *user panel* allows students to sign up for a variety of groups (**1 group per subject**).
The administrator can add subjects and groups as well as delete them, they can also remove users from groups.
There is an option to dump data from the database to an xlsx file (all users who have signed up for a subject).

## Possible bugs
The application has been deployed in a state very similar to the one shown in this repository (the repo app is in *debug mode*). Nontheless there are some security flaws that have not been addressed yet. **xlsx dump** might not work, depending on server setup.