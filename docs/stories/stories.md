# COGS User Stories

## Roles:
- User
 - Exists as user in integration tests
- Project owner
 - Is the user the created the project
- Principal Investigator
 - A field in a project, not a user
- RSE
- System Administrator
 - Both in integration tests but no difference
- Attribution Authoriser
- Project Authoriser
 - Same as RSE or Admin?

## Stories
### Project creation
- Users with valid, non-student institutional email addresses can create new projects as the project owner
 - Implemented and tested
- Users with student or non-institutional email address cannot create new projects
 - No check on emails, student is treated the same as a staff member
 - A test is included and fails accordingly
- New projects are created with a default priority level and are not active
 -The standard user project submission test checks this
- Projects do not have a start or end date (start or end dates are specified on allocations, users and attributions)
 - Project have a start and end date and the form requires this information
- New projects must have a name, description, project owner and institution
 - Testing that leaving a required field blank causes the expected error

### Project administration
- Any user can request membership in a project, which will create a membership request pending approval
 - Pending testing
- Only the tech lead can approve project memberships requests
 - Pending testing

- Project owner can associate new/existing users to an existing projects by email address
 - Not implemented
- Users added to a project should be required to click a link in a confirm email before being added
 - Not implemented

- Associating users to a project should fail after a specified number of user has been reached (to avoid excessive disk space to a project)
- Not implemented
- The associated user limit should be set on a per-project basis and have a per-institution limit
- Not implemented
- Project owner can request a raised priority level if priority criterion is met (requests are sent to a system administrator to handle manually)
- Not implemented


### User creation
- Anyone with an institutional email address should be able to log in
 - Not implemented
- Anyone with a pre-approved (non-institutional) email address log in
 - Not implemented
- Users should set institution, college/department, orcid, scopus url and homepage
 - Not implemented
- Users from Swansea university can set a Cronfa URL
 - Not implemented
- Users should be automatically removed from the system when they leave university
- User signup should require agreeing to terms and conditions
 - I don't see any implementation of user creation except on the admin page

### Attribution addition and approval
- Users can add an attributions to a projects they are associated, specifying an attribution owner (e.g. principal investigator or lead author)
- An attribution can be of type grant or paper
- An attribution can associated with one or more projects
- A paper has a title, authors, a Journal, a doi and a cronfa link (Swansea)
- A grant has a title, grant code, total amount, amount attributed to SCW, grant code, comments, a funding body and a principal investigator
- Principal investigator receives a confirmation request email for every grant application
- Confirmation request emails contain a mailto link to an email reply statement, pre-populated with information derived from the attribution data and confirming that the sender is PI of the grant and that grant income is only attributed once.
- Confirmation request emails will tell the user to modify the text if incorrect
- Attribution authoriser is notified of a new attribution at their institution
- Attribution authoriser can mark an attribution confirmation email as valid
- Attribution authoriser can see highlighted changes to attribution confirmation emails (compared to original message)

### Project approval and system allocation
- Project approvers, RSEs and attribution authorisers can see a page listing pending/unapproved projects per institution
- Project approvers, RSEs and attribution authorisers can see details of pending/unapproved projects per institution
- Project approvers can set project status to approved
- Project approvers can reject project with a comment (project owner receives comment)
- Project approvers can specify a system (or systems) on which a system allocation is created
- Project approvers can modify default values of that system allocation
- Project approvers can add new system allocations (for example on another cluster system or over a new time period) to an existing project
- System allocations allowable and their priority should be determined in some way by level and/or nature of attribution (policy to be agreed by management board)
- The associated cluster user accounts are enabled on the appropriate cluster when new (active) system allocations are created
- Historical comments on a project are stored in a separate table

### Cluster accounts
- Can users have a cluster accounts on a cluster system (or multiple systems)
- System administrators can create cluster user accounts for users
- Creating a cluster account which belongs to a system will create an account on the appropriate cluster
- Users should be able to reset passwords for their cluster accounts, user passwords will not be stored on the cogs system

### Raven users
- New raven users will automatically have a new cluster account set up on first login and will belong to a default "Raven" project
- Active cluster user accounts created on the Cardiff system with no approval required

### Potential future changes
- Attribution should automatically affect resource allocation by some mechanism (according to policy agreed by management board)
- All database records should contain a created and modified time stamp for auditing purposes. Records likely to be subject to auditing (e.g. approvals) should be versioned as appropriate

### Other Suggestions
- Projects who aren't returning anything (yet) need a grant number to be raised from bottom category
- Storage is allocated in system allocation table
- On boarding and training could be combined to a single field
- Paragraph about attribution from previous SCW form should be included
- Project doesn't have an institution, it is derived from the main user
