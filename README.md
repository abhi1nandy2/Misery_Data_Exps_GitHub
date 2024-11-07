# Misery_Data_Exps_GitHub
 
- `misery_index_game_show.py` - code for running the LLM as a game show contestant
- `utils.py` - functions for generating responsed from LLM functions
- `eval.py` - evaluating the responses
- `Misery_Data.csv` - data containing miserable situations, their annotated misery index values, contestant responses, and other metadata
  
  - Run `python misery_index_game_show.py <SEED> <MODEL_NAME>`
   
    - `<SEED>` - 12, 123, 1234
    - `<MODEL_NAME>` - gpt-3.5-turbo, gpt-4, gpt-4-turbo, gpt-4o, gpt-4o-mini, o1, o1-mini

## Progress

- **Game-show setting**

Column headers are seeds.

|             | 12        | 123       | 1234      |
|-------------|-----------|-----------|-----------|
| gpt-3.5-turbo | ✅        | ✅        | ✅        |
| gpt-4       | ✅        | ❌        | ❌        |
| gpt-4-turbo | ✅        | ✅        | ✅        |
| gpt-4o-mini | ✅        | ✅        | ✅        |
| gpt-4o      | ✅        | ✅        | ✅        |
| o1-preview  | ❌        | ❌        | ❌        |
| o1-mini     | ❌        | ❌        | ❌        |
|gemini-1.5-pro| ❌        | ❌        | ❌        |

- **Game-show setting with chain-of-thought**
  
- **Directly predicting the misery index**

## Links used for gathering data 

- https://bobbymgsk.wordpress.com/category/the-misery-index/
- https://jericho.blog/2021/02/03/the-misery-index-data/ - contains most of the data in a spreadsheet - https://docs.google.com/spreadsheets/d/151WjFwDdhIURf48subj6SDOdra0XVIEo0xulnBMMfRo/edit#gid=1169151367
