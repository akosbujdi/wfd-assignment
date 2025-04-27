Feature: View student order history
  As a student I want to view my order history
  So that I can track my past purchases

  Scenario: Student views their past orders
    Given the student is logged in
    And they have placed at least one order
    When they visit the "Order History" page
    Then they should see a list of their past orders with order statuses