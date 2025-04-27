Feature: Edit User Details
  As a Super Admin
  I want to edit the details of a user
  So that I can manage user accounts

  Scenario: Successfully changing the name of a user
    Given the Super Admin is logged in
    And a user exists with name "John Doe"
    When the Super Admin navigates to the "Edit User" page
    And changes the name to "Jane Doe"
    And clicks the "Save Changes" button
    Then the user name should be updated to "Jane Doe" in the user list