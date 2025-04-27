Feature: Inventory manager adds a new item
  As an inventory manager I want to add new items to the inventory
  So that users can purchase them

  Scenario: Inventory manager successfully adds a new item
    Given the inventory manager is logged in
    When they navigate to the "Add Item" page
    And fill in name "Notebook", description "Red, useful for notes", price "4.99", quantity "100"
    And click the "Add Item" button
    Then the item "Notebook" should be appear to the inventory