Feature: Edit Item Details
  As an Inventory Manager
  I want to edit the details of an item
  So that I can update the inventory to stay up-to-date

  Scenario: Successfully changing the price of an item
  Given the Inventory Manager is logged in
  And an item exists with name "Pencil" and price "2.99"
  When the Inventory Manager navigates to the "Edit Item" page
  And changes the price to "3.99"
  And clicks the "Save Changes" button
  Then the item price should be updated to "3.99"