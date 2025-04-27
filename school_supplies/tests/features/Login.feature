Feature: User Login
  As a user I want to be able to log in to the system
  So that I can access the features of the system

  Scenario: Successful login with valid credentials
    Given the user is on the login page
    And a registered user exists with email "admin@admin.com" and password "password"
    When the user enters "admin@admin.com" and "password"
    And clicks the "Login" button
    Then the user should be redirected to the home page