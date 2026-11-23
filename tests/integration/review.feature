Feature: Independent review of a completed request
  Scenario: Code and Markdown reviewers return one report
    Given a completed request in a sample workspace
    When the review plugin receives a mixed patch and a stop event
    Then it returns a report with findings from each review perspective
    And a follow-up stop does not request another review

  Scenario: Markdown instructions bury a sequence and a choice in one paragraph
    Given a completed request in a sample workspace
    When the user edits a paragraph containing setup and two alternative commands
    Then the Markdown reviewer proposes ordered steps with grouped alternatives and preserves the prerequisite
