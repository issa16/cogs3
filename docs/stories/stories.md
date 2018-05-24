# COGS User Stories

## Roles:
#### Implemented:
- User : any user authorised on the system (internal and external)
- Internal User : any user who signs up with an institutional email address
- External user : a user without a institutional email address, which has been pre-created by a site admin
- Technical lead : the user who creates project requests
- Principal Investigator: not currently a user
- Site Admin: django superuser, can make any changes to the database
#### Not Implemented:
- Attribution Authoriser: Users who have permission to authorise attribution
- Project Authoriser: Users who have permission to authorise projects
- RSE: undefined

## Stories
### Project creation
#### Tested
- Internal users can create new project as it's technical lead [IT]
- External users can create new project as it's technical lead [IT]
- Newly created projects are created with status UNAPPROVED [UT]
- Newly created projects do not have a default category [UT]
- Project status cannot be set to approved without a category and project code [UT]
- New projects must have a name, description, technical lead, institution, start date and an end date [IT]
- Active projects are listed as 'Awaiting Authorisation' the project list [IT]
#### Not Tested
- Projects require a start and end date [UT]

### Project administration
#### Tested
- User can create a project membership request [IT]
- Project membership requests should be created in a PENDING state [IT]
- Technical lead should be able to change the state of project memberships requests made by other users to APPROVED [IT]
#### Not Implemented
- Technical lead should be able to create a project membership request for a specific user by email address
- User being added should be able to change the state of a project membership request created by a technical lead to APPROVED
- Users added to a project by a technical lead should receive email notification of a pending project membership request
- Technical leads of a project for which a user has created a project membership request receive email notification
- Project membership should be capped to a number defined at each institution (to avoid excessive disk space to a project)
- Project membership limits should be overridable on a per-project basis
- Some mechanism (yet undetermined) is required for users to request a category change as appropriate

### User creation
#### Tested
- Any users can log in with an institutional email address [IT]
- Anyone user with a  pre-approved, non-institutional email address can log in [IT]
#### Not Tested
- Users should be automatically removed from the system when they leave university
#### Not Implemented
- Users should be able to set an orcid, scopus url and homepage
- Users from Swansea university should be able to set a Cronfa URL
- User signup should require agreeing to terms and conditions

### Attribution addition and approval
#### Not Implemented
- Users can add an attributions to a projects they are associated with, specifying an attribution owner (e.g. principal investigator or lead author)
- An attribution can be a type grant or paper
- An attribution can associated with one or more projects
- A paper has a title, authors, a Journal, a doi and a cronfa link (Swansea)
- A grant has a title, grant code, total amount, amount attributed to SCW, grant code, comments, a funding body and a principal investigator
- Principal investigator receives a confirmation request email for every grant application
- Confirmation request emails contain a mailto link to an email reply statement, pre-populated with information derived from the attribution data and confirming that the sender is PI of the grant and that grant income is only attributed once.
- Confirmation request emails will tell the user to modify the text if incorrect
- Attribution authoriser is notified of a new attribution at their institution
- Attribution authoriser can mark an attribution confirmation email as valid
- Attribution authoriser can see highlighted changes to attribution confirmation emails (compared to original message)
- Paragraph about attribution from previous SCW form should be included

### Project approval and system allocation
#### Tested
- A site admin can approve projects
#### Not Implemented
- Project approvers, RSEs and attribution authorisers can see a page listing pending/unapproved projects per institution
- Project approvers, RSEs and attribution authorisers can see details of pending/unapproved projects per institution
- Project approvers can set project status to approved
- Project approvers can reject project with a comment (technical lead receives comment by email)
- New system allocations are created on the system belonging to the institution of the user
- Project approvers can add new system allocations on other clusters to an existing project

### Cluster accounts
#### Not Tested
- Cluster accounts are created for the user (undefined behaviour)
- User accounts are automatically created if they don't exist when a new system allocation is created
### Not Implemented
- Users can reset their cluster passwords

### General
#### Not Implemented
- Database records should contain a created and modified time stamp for auditing purposes. Records likely to be subject to auditing (e.g. approvals) should be versioned as appropriate
