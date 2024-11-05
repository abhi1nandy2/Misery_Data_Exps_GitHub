import pandas as pd
from utils import get_completion, extract_answer, get_correct_or_wrong
import numpy as np
import os
import sys
from tqdm import tqdm
import time

seed = int(sys.argv[1]) #[12, 123, 1234]

model_name = sys.argv[2] #'gpt-4o-mini'

num_episodes = 40
num_questions_per_ep = 12

df = pd.read_csv("Misery_Data.csv", nrows = num_episodes*num_questions_per_ep)

instructions = """Gameplay
The main game consists of three rounds that involve rating and ranking miserable true stories. Ratings are on a numerical scale of 1 to 100, as determined by a panel of psychologists, and are based on the "Three Pillars of Misery": physical pain, emotional trauma, and long-term psychological impact.



Round 1: Misery Lane (consists of 2 questions)
In each question, two hypothetical situations are presented to the contestant. The contestant must decide whether a given story falls above, below, or between the two hypothetical situations; a correct choice wins $500.



Round 2: More or Less Miserable (consists of 2 questions)
In each question, the contestant is shown two similar stories and must decide which one earned the higher Index rating, earning $1,000 for a correct guess.



Round 3: Master of Misery (consists of 1 question)
One miserable story is presented, and the contestant must guess its Index rating as closely as possible. The closer the guess, the higher the reward.



Bonus Round: Margin of Misery (consists of 3 questions)
The contestant is shown three miserable stories, one at a time, and must guess the Index rating of each within a specified margin of error in order to win additional money as follows.


First story: $5,000 value, within 30 points 
Second story: $10,000 value, within 20 points
Third story: $15,000 value, within 10 points
The contestant guesses by moving a range finder on a sliding scale, attempting to cover the actual rating, and has 10 seconds to lock in a guess on each story.



You are a contestant in the aforementioned game show. This is the conversation during the gameshow between you and the game show host.



"""

prompts= {}

prompts["1_1"] = """Host: Let's start the Round 1, Misery Lane.  
## Hypothetical Situation 1: {}. Misery Rating = {}
## Hypothetical Situation 2: {}. Misery Rating = {}
## Story: {}
Does the story fall above, below, or between the two situations? Output your final answer as one of either above, below, or between in three braces, like {{{{{{this}}}}}}.

You: """

prompts["1_2"] = """Host: {} The rating for the story was {}. Let's go to the next question. 
## Story: {}
Does the story fall above, below, or between the two situations? Output your final answer as one of either above, below, or between in three braces, like {{{{{{this}}}}}}.

You: """

prompts["2_1"] = """Host: {} The rating for the story was {}. Let's start the Round 2, More or Less Miserable.
## Story 1: {}. Misery Rating = {}
## Story 2: {}
Does Story 2 have a higher or lower rating compared to Story 1? Output your final answer as one of either higher or lower in three braces, like {{{{{{this}}}}}}.

You: """

prompts["2_2"] = """Host: {} The rating for the story was {}. Let's go to the next question.
## Story 1: {}. Misery Rating = {}
## Story 2: {}
Does Story 2 have a higher or lower rating compared to Story 1? Output your final answer as one of either higher or lower in three braces, like {{{{{{this}}}}}}.

You: """

prompts["3"] = """Host: {} The rating for the story was {}. Let's start the Round 3, Master of Misery.
## Story: {}
Output your final answer as the misery rating (on a numerical scale of 1 to 100) of this story in three braces, like {{{{{{this}}}}}}.

You: """

prompts["4_1"] = """Host: The rating for the story was {}. You were off by {} points! Let's start the Bonus Round, Margin of Misery.
## Story: {}
Output your final answer as the interval of ratings (interval size = 30) in three braces, like {{{{{{LOWER LEVEL - HIGHER LEVEL}}}}}}

You: """

prompts["4_2"] = """Host: {} The rating for the story was {}. Let's go to the next question.
## Story: {}
Output your final answer as the interval of ratings (interval size = 20) in three braces, like {{{{{{LOWER LEVEL - HIGHER LEVEL}}}}}}

You: """

if model_name in ['gpt-3.5-turbo']:
    prompts['4_1'] = prompts['4_1'].replace("in three braces", "in three braces (STICK TO THIS FORMAT ONLY, NO OTHER FORMAT ALLOWED! LOWER LEVEL and HIGHER LEVEL are integers, empty values NOT ALLOWED!)")
    prompts['4_2'] = prompts['4_2'].replace("in three braces", "in three braces (STICK TO THIS FORMAT ONLY, NO OTHER FORMAT ALLOWED! LOWER LEVEL and HIGHER LEVEL are integers, empty values NOT ALLOWED!)")

prompts["4_3"] = prompts["4_2"].replace("(interval size = 20)", "(interval size = 10)")


new_tag_order = ['1_base_1', '1_base_2', '1_1', '1_2', '2_1_base', '2_1', '2_2_base', '2_2', '3', '4_1', '4_2', '4_3']

responses_dict = {}
pred_answers_dict = {}
correct_dict = {}

full_response_save_dir = "full_responses_MODEL_{}_SEED_{}".format(model_name, seed)
if os.path.exists(full_response_save_dir) == False:
    os.mkdir(full_response_save_dir)

for ep_idx in tqdm(range(num_episodes)):
    responses_dict[ep_idx] = {}
    pred_answers_dict[ep_idx] = {}
    correct_dict[ep_idx] = {}

    start_idx = ep_idx * num_questions_per_ep
    ep_rows = df[start_idx:start_idx + num_questions_per_ep].reset_index(drop=True)

    q_list = ep_rows['Misery'].tolist()
    score_list = ep_rows['Score'].tolist()
    score_list = [int(item) for item in score_list]
    win_list = ep_rows['Win'].tolist()
    tag_list = ep_rows['question_tag'].tolist()
    level_list = ep_rows['level'].tolist()

    count=0

    for idx, item in enumerate(tag_list):
        if item=="1_base":
            count+=1
            tag_list[idx] = tag_list[idx] + "_" + str(count)

    # print(str(win_list[4])=="nan")
    # break

    index_map = [tag_list.index(tag) for tag in new_tag_order]

    q_list = [q_list[i] for i in index_map]
    score_list = [score_list[i] for i in index_map]
    win_list = [win_list[i] for i in index_map]
    level_list = [level_list[i] for i in index_map]    

    # 1_1

    input_prompt = instructions + prompts["1_1"].format(q_list[0], score_list[0], q_list[1], score_list[1], q_list[2])



    response = get_completion(input_prompt, model_name, seed)

    # print("RESPONSE BEGINS")
    # print(response)
    # print("RESPONSE ENDS")

    responses_dict[ep_idx]['1_1'] = response
    answer = extract_answer(response)
    pred_answers_dict[ep_idx]['1_1'] = answer

    # print("ANSWER BEGINS")
    # print(answer)
    # print("ANSWER ENDS")

    condition=False

    if (score_list[2] > score_list[0]) and (score_list[2] > score_list[1]):
        if answer.lower()=="above":
            condition=True

    elif (score_list[2] < score_list[0]) and (score_list[2] < score_list[1]):
        if answer.lower()=="below":
            condition=True
    else:
        if answer.lower()=="between":
            condition=True

    correct_dict[ep_idx]['1_1'] = condition

    # 1_2

    input_prompt += response + "\n\n" + prompts['1_2'].format(get_correct_or_wrong(condition), score_list[2], q_list[3])



    response = get_completion(input_prompt, model_name, seed)

    # print("RESPONSE BEGINS")
    # print(response)
    # print("RESPONSE ENDS")

    responses_dict[ep_idx]['1_2'] = response
    answer = extract_answer(response)
    pred_answers_dict[ep_idx]['1_2'] = answer

    # print("ANSWER BEGINS")
    # print(answer)
    # print("ANSWER ENDS")    

    condition=False

    if (score_list[3] > score_list[0]) and (score_list[3] > score_list[1]):
        if answer.lower()=="above":
            condition=True

    elif (score_list[3] < score_list[0]) and (score_list[3] < score_list[1]):
        if answer.lower()=="below":
            condition=True
    else:
        if answer.lower()=="between":
            condition=True

    correct_dict[ep_idx]['1_2'] = condition

    # 2_1

    input_prompt += response + "\n\n" + prompts["2_1"].format(get_correct_or_wrong(condition), score_list[3], q_list[4], score_list[4], q_list[5])    



    response = get_completion(input_prompt, model_name, seed)

    # print("RESPONSE BEGINS")
    # print(response)
    # print("RESPONSE ENDS")
    
    responses_dict[ep_idx]['2_1'] = response
    answer = extract_answer(response)
    pred_answers_dict[ep_idx]['2_1'] = answer

    # print("ANSWER BEGINS")
    # print(answer)
    # print("ANSWER ENDS")        

    condition=False

    assert(score_list[4]!=score_list[5])
    if score_list[5] > score_list[4]:
        if answer.lower()=="higher":
            condition=True
    elif score_list[5] < score_list[4]:
        if answer.lower()=="lower":
            condition=True   

    correct_dict[ep_idx]['2_1'] = condition             

    # 2_2

    input_prompt += response + "\n\n" + prompts["2_2"].format(get_correct_or_wrong(condition), score_list[5], q_list[6], score_list[6], q_list[7])    



    response = get_completion(input_prompt, model_name, seed)

    # print("RESPONSE BEGINS")
    # print(response)
    # print("RESPONSE ENDS")

    responses_dict[ep_idx]['2_2'] = response
    answer = extract_answer(response)
    pred_answers_dict[ep_idx]['2_2'] = answer

    # print("ANSWER BEGINS")
    # print(answer)
    # print("ANSWER ENDS")

    condition=False

    assert(score_list[6]!=score_list[7])
    if score_list[7] > score_list[6]:
        if answer.lower()=="higher":
            condition=True
    elif score_list[7] < score_list[6]:
        if answer.lower()=="lower":
            condition=True   

    correct_dict[ep_idx]['2_2'] = condition

    # 3

    input_prompt += response + "\n\n" + prompts["3"].format(get_correct_or_wrong(condition), score_list[7], q_list[8])



    response = get_completion(input_prompt, model_name, seed)

    # print("RESPONSE BEGINS")
    # print(response)
    # print("RESPONSE ENDS")

    responses_dict[ep_idx]['3'] = response
    answer = extract_answer(response)
    pred_answers_dict[ep_idx]['3'] = answer

    # print("ANSWER BEGINS")
    # print(answer)
    # print("ANSWER ENDS")

    condition = str(np.abs(int(answer) - score_list[8]))

    correct_dict[ep_idx]['3'] = condition

    # 4_1

    input_prompt += response + "\n\n" + prompts["4_1"].format(score_list[8], condition, q_list[9])

    # print("INP BEGINS")
    # print(input_prompt)
    # print("INP ENDS")

    response = get_completion(input_prompt, model_name, seed)

    # print("RESPONSE BEGINS")
    # print(response)
    # print("RESPONSE ENDS")

    responses_dict[ep_idx]['4_1'] = response
    answer_lower, answer_upper = extract_answer(response)
    answer = (answer_lower, answer_upper)
    pred_answers_dict[ep_idx]['4_1'] = answer

    # print("ANSWER BEGINS")
    # print(answer)
    # print("ANSWER ENDS")

    # assert answer_upper - answer_lower == 30, str(answer_lower) + " " + str(answer_upper) + " " + str(answer_upper - answer_lower)

    condition=False    

    if (score_list[9] >= answer_lower) and (score_list[9] <= answer_upper) and (answer_upper - answer_lower==30):
        condition=True

    correct_dict[ep_idx]['4_1'] = condition

    # 4_2

    input_prompt += response + "\n\n" + prompts["4_2"].format(get_correct_or_wrong(condition), score_list[9], q_list[10])

    # print("INP BEGINS")
    # print(input_prompt)
    # print("INP ENDS")

    response = get_completion(input_prompt, model_name, seed)

    # print("RESPONSE BEGINS")
    # print(response)
    # print("RESPONSE ENDS") 

    responses_dict[ep_idx]['4_2'] = response
    answer_lower, answer_upper = extract_answer(response)
    answer = (answer_lower, answer_upper)
    pred_answers_dict[ep_idx]['4_2'] = answer

    # print("ANSWER BEGINS")
    # print(answer)
    # print("ANSWER ENDS")  

    # assert(answer_upper - answer_lower == 20)

    condition=False  

    if (score_list[10] >= answer_lower) and (score_list[10] <= answer_upper) and (answer_upper - answer_lower==20):
        condition=True

    correct_dict[ep_idx]['4_2'] = condition          

    # 4_3

    input_prompt += response + "\n\n" + prompts["4_3"].format(get_correct_or_wrong(condition), score_list[10], q_list[11])

    # print("INP BEGINS")
    # print(input_prompt)
    # print("INP ENDS")

    response = get_completion(input_prompt, model_name, seed)

    # print("RESPONSE BEGINS")
    # print(response)
    # print("RESPONSE ENDS") 

    responses_dict[ep_idx]['4_3'] = response
    answer_lower, answer_upper = extract_answer(response)
    answer = (answer_lower, answer_upper)
    pred_answers_dict[ep_idx]['4_3'] = answer

    # print("ANSWER BEGINS")
    # print(answer)
    # print("ANSWER ENDS")  

    # assert(answer_upper - answer_lower == 10)

    condition=False  

    if (score_list[11] >= answer_lower) and (score_list[11] <= answer_upper) and (answer_upper - answer_lower==10):
        condition=True

    correct_dict[ep_idx]['4_3'] = condition

    input_prompt += response + "\n\n" + "Host: {} The rating for the story was {}.".format(get_correct_or_wrong(condition), score_list[11]) + " Thank you for playing!"             

    # print(input_prompt)

    with open(os.path.join(full_response_save_dir, str(ep_idx) + ".txt"), 'w') as fw:
        fw.write(input_prompt)

    # break
    if ("gpt-" in model_name) or ("o1" in model_name):
        time.sleep(5)
    elif "gemini" in model_name:
        time.sleep(8)

import json

with open(full_response_save_dir + "_RESPONSES.json", 'w') as fw:
    json.dump(responses_dict, fw, indent = 2)

with open(full_response_save_dir + "_PRED_ANSWERS.json", 'w') as fw:
    json.dump(pred_answers_dict, fw, indent = 2)    

with open(full_response_save_dir + "_IS_CORRECT.json", 'w') as fw:
    json.dump(correct_dict, fw, indent = 2)    