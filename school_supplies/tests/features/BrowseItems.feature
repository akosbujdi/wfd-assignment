Feature: Browsing inventory items
  As a user I want to be able to browse the available items in the inventory
  So that I can make purchases

  Scenario: User browses available items
    Given the system has items in stock
    When the user visits the "Items" page
    Then they should see a list of available items with their names and prices