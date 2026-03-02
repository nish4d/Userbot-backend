# Dashboard Update Prompt: Multiple Keywords Support

## Overview
The backend has been updated to support multiple keywords (triggers) for each reply rule. Previously, each rule could only have a single keyword that would trigger a response. Now, each rule can have multiple keywords that will all trigger the same response.

## Backend Changes Summary
1. **Database Schema Change**: 
   - New field: `triggers` (array of strings) - replaces the old `trigger` field
   - Backward compatibility maintained with the old `trigger` field

2. **API Endpoint Changes**:
   - POST `/api/rules` - Accepts `triggers` array instead of single `trigger`
   - PUT `/api/rules/{id}` - Accepts `triggers` array instead of single `trigger`
   - GET `/api/rules` - Returns `triggers` array in response

3. **Processing Logic**:
   - Message processing now checks against all keywords in the `triggers` array
   - Backward compatibility maintained for rules with old `trigger` field

## Required Dashboard Updates

### 1. Rule Creation Form
Update the form for creating new reply rules:
- Replace the single "Keyword" text input with a multi-value input component
- Allow users to enter multiple keywords that will trigger the same response
- Example UI:
  ```
  Keywords (comma separated): [hi, hello, hey, greetings]
  Response: Hello there! How can I help you?
  ```

### 2. Rule Editing Form
Similar changes to the rule creation form:
- Display existing keywords as a list/array
- Allow adding/removing keywords
- Save as `triggers` array in API requests

### 3. Rule Display
Update the rule listing to show multiple keywords:
- Instead of showing a single "Keyword" column, show a "Keywords" column
- Display all keywords for each rule
- Example:
  ```
  Rule 1:
  Keywords: hi, hello, hey
  Response: Hello there!
  
  Rule 2:
  Keywords: bye, goodbye
  Response: Goodbye! Have a great day!
  ```

## API Usage Examples

### Creating a Rule with Multiple Keywords
```json
POST /api/rules
{
  "triggers": ["hi", "hello", "hey"],
  "response": "Hello there! How can I help you today?",
  "enabled": true
}
```

### Updating a Rule
```json
PUT /api/rules/{rule_id}
{
  "triggers": ["hi", "hello", "hey", "greetings"],
  "response": "Hello there! How can I help you today?",
  "enabled": true
}
```

### Getting Rules
```json
GET /api/rules
[
  {
    "id": "rule_id_1",
    "triggers": ["hi", "hello", "hey"],
    "response": "Hello there! How can I help you today?",
    "enabled": true
  },
  {
    "id": "rule_id_2",
    "triggers": ["bye", "goodbye"],
    "response": "Goodbye! Have a great day!",
    "enabled": true
  }
]
```

## Backward Compatibility Notes
- Existing rules with the old `trigger` field will continue to work
- When retrieving rules, both new rules (with `triggers`) and old rules (with `trigger`) will be processed correctly
- The backend automatically converts single `trigger` to `triggers` array for processing

## Implementation Recommendations
1. **UI Component**: Use a tag input or multi-select component for entering keywords
2. **Data Handling**: Always send data as `triggers` array to the API
3. **Display**: Show all keywords in a readable format
4. **Validation**: Ensure keywords are unique and not empty
5. **Migration**: Optionally migrate existing rules from `trigger` to `triggers` array

## Testing Scenarios
1. Create a rule with multiple keywords and verify all keywords trigger the response
2. Edit a rule to add/remove keywords
3. Verify backward compatibility with existing single-keyword rules
4. Test edge cases like empty keywords array

This update enables users to define multiple keywords that trigger the same response, making the bot more flexible and user-friendly.