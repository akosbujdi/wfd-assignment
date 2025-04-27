Feature: Update Order Status
  As an Inventory Manager
  I want to update the status of an order
  So that user can track the progress of their order

  Scenario: Successfully updating an from "Pending" to "Shipped"
    Given the Inventory Manager is logged in
    And an order exists with status "Pending"
    When the Inventory Manager navigates to the "Order History" page
    And selects the order to update
    And changes the status to "Shipped"
    And clicks the "Update Status" button
    Then the order status should be updated to "Shipped"