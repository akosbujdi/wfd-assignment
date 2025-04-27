Feature: User Registration
  As a user I want to be able to register with the system
  So that I can access the features of the system

  Scenario: Successful student registration
    Given the user is on the student registration page
    When the user enters email "new@student.com" name "John Doe" and password "password"
    And the user clicks the "Register" button
    Then the user should be redirected to the login page