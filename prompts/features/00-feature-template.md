---
prompt: |
  {{ prompt }}
refinement: |
  {{ refinement }}
---

# Feature Implementation Meta-Prompt

## 1. Clarification and Context

- **Clarifying Questions:** What questions do I need to ask to fully understand the user's intent and the context of this feature?
- **Assumptions:** What assumptions am I making about the user's request and the existing system?
- **Goals & Non-Goals:** What are the primary goals of this feature? What is explicitly out of scope?

## 2. Pre-Mortem Analysis

- **Potential Showstoppers:** What could prevent this feature from being implemented successfully?
- **External Dependencies:** What external systems, libraries, or APIs does this feature depend on? Are there any potential risks associated with them?
- **Edge Cases:** What are the potential edge cases and how should they be handled?

## 3. Implementation Plan

- **High-Level Steps:** Outline the high-level steps required to implement this feature.
- **Code-Level Changes:** Detail the specific code changes, new files, and modifications to existing files.
- **Data Model Changes:** Are there any changes required to the data model or database schema?

## 4. Validation and Testing

- **Unit Tests:** What new unit tests are needed to verify the functionality of this feature?
- **Integration Tests:** How will this feature be tested in the context of the larger system?
- **Manual Testing:** What manual testing steps are required to ensure the feature works as expected?

## 5. Threat Model Impact

- **Summary of Changes:** How does this feature change the attack surface of the application?
- **Asset Identification:** What new assets are being introduced (e.g., data, services, secrets)?
- **Threat Identification:** What new threats are introduced by this feature?
- **Mitigation Strategies:** What measures are in place to mitigate these new threats?

## 6. Important Sources

- [Source 1: Link to relevant documentation, articles, or examples]
- [Source 2: Link to another relevant resource]

## TL;DR

A concise summary of the feature implementation plan, including key decisions and potential risks.
