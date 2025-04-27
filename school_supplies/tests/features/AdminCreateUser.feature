Feature: Super admin creates a new inventory manager account
  As a super admin I want to create new inventory manager accounts
  So that they can manage the inventory

  Scenario: Super admin adds a new inventory manager user
    Given the super admin is logged in
    When they navigate to the "Add new user" page
    And they fill in the user form with role "Inventory Manager", email "newim@im.com", name "John Doe", and password "password"
    And they click the "Add User" button
    Then the new user should be added to the system and appear in the user list