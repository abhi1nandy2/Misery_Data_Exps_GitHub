import json
import numpy as np

model_names = ['gpt-3.5-turbo', 'gpt-4-turbo', 'gpt-4o-mini', 'gpt-4o']
seeds = ['12', '123', '1234']

filename_template = "full_responses_MODEL_{}_SEED_{}_IS_CORRECT.json"

str_ = "ModelName,Round 1,Round 2,Bonus Round,Overall,Avg. Distance in Round 3\n"

for model_name in model_names:
    final_acc_1_list = []
    final_acc_2_list = []
    final_dist_3_list = []
    final_acc_4_list = []
    final_acc_list = []    
    for seed in seeds:
        
        acc_1_list = []
        acc_2_list = []
        dist_3_list = []
        acc_4_list = []
        acc_list = []

        filename = filename_template.format(model_name, seed)

        with open(filename, 'r') as fr:
            dict_ = json.load(fr)
        
        for ep_idx in dict_:
            ep_idx=str(ep_idx)
            correct_1 = int(dict_[ep_idx]['1_1']) + int(dict_[ep_idx]['1_2'])
            correct_2 = int(dict_[ep_idx]['2_1']) + int(dict_[ep_idx]['2_2'])
            dist_3 = int(dict_[ep_idx]['3'])
            correct_4 = int(dict_[ep_idx]['4_1']) + int(dict_[ep_idx]['4_2']) + int(dict_[ep_idx]['4_3'])

            acc_1 = correct_1/2
            acc_2 = correct_2/2
            acc_4 = correct_4/3
            acc = (correct_1+correct_2+correct_4)/7

            acc_1_list.append(acc_1*100)
            acc_2_list.append(acc_2*100)
            dist_3_list.append(dist_3)
            acc_4_list.append(acc_4*100)
            acc_list.append(acc*100)

        final_acc_1_list.append(np.mean(acc_1_list))
        final_acc_2_list.append(np.mean(acc_2_list))
        final_dist_3_list.append(np.mean(dist_3_list))
        final_acc_4_list.append(np.mean(acc_4_list))                
        final_acc_list.append(np.mean(acc_list))

    str_ += ",".join([model_name, str(np.mean(final_acc_1_list)), str(np.mean(final_acc_2_list)), str(np.mean(final_acc_4_list)), str(np.mean(final_acc_list)), str(np.mean(dist_3_list))]) + "\n" 

with open("results.csv", 'w') as fw:
    fw.write(str_)