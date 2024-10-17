import json
import glob
import subprocess
import shlex
import os
import pandas as pd

cov_seq_csv = dict()

for log in glob.glob("./random_myth_*.log"):
    cov_seq_csv[log+ "-random"] = []
    cov_seqs = cov_seq_csv[log+ "-random"]
    log_name = os.path.basename(log)
    print(log_name)
    cat_cmd = "cat {0}.log|grep coverage > {0}.cov.list".format(
        log_name.split(".")[0])
    os.system(cat_cmd)
    cov_list = open(
        "./{0}.cov.list".format(
            log_name.split(".")[0])).readlines()

    all_cov_infos = []
    for cov in cov_list:
        item = cov.strip().split("coverage file: ")[-1].strip()
        # print(item)
        all_cov_infos.append(json.load(open(item))[-1])

    if len(all_cov_infos) == 0:
        continue
    code_cov = all_cov_infos[0]["code_cov"]
    for cov_info in all_cov_infos:
        cur_code_cov = cov_info["code_cov"]
        assert code_cov[0] == cur_code_cov[0], "the number of instruction are not the same, please check"
        code_cov[1] = [cur_code_cov[1][i] or code_cov[1][i]
                       for i in range(code_cov[0])]
        # print("current test coverage: {0}%".format(cov_info["cov_percentage"]))
        cov_seqs.append(sum(code_cov[1])/float(code_cov[0])*100)
    print("Achieved coverage: {0}%".format(
        sum(code_cov[1])/float(code_cov[0])*100))

    print("****************************************************************")


for log in glob.glob("./mbt_myth_*.log"):
    cov_seq_csv[log+ "-mbt"] = []
    cov_seqs = cov_seq_csv[log+ "-mbt"]
    log_name = os.path.basename(log)
    print(log_name)
    cat_cmd = "cat {0}.log|grep coverage > {0}.cov.list".format(
        log_name.split(".")[0])
    os.system(cat_cmd)
    cov_list = open(
        "./{0}.cov.list".format(
            log_name.split(".")[0])).readlines()

    all_cov_infos = []
    for cov in cov_list:
        item = cov.strip().split("coverage file: ")[-1].strip()
        # print(item)
        all_cov_infos.append(json.load(open(item))[-1])

    if len(all_cov_infos) == 0:
        continue
    code_cov = all_cov_infos[0]["code_cov"]
    for cov_info in all_cov_infos:
        cur_code_cov = cov_info["code_cov"]
        assert code_cov[0] == cur_code_cov[0], "the number of instruction are not the same, please check"
        code_cov[1] = [cur_code_cov[1][i] or code_cov[1][i]
                       for i in range(code_cov[0])]
        # print("current test coverage: {0}%".format(cov_info["cov_percentage"]))
        cov_seqs.append(sum(code_cov[1])/float(code_cov[0])*100)
    print("Achieved coverage: {0}%".format(
        sum(code_cov[1])/float(code_cov[0])*100))

    print("****************************************************************")

df = pd.DataFrame(dict([(key, pd.Series(value)) for key, value in cov_seq_csv.items()]))
print(df)
print(df.to_csv("cov_seq.csv"))

# for log in glob.glob("./parametric_myth_*.log"):
#     log_name = os.path.basename(log)
#     print(log_name)
#     cat_cmd = "cat {0}.log|grep coverage > {0}.cov.list".format(
#         log_name.split(".")[0])
#     os.system(cat_cmd)
#     cov_list = open(
#         "./{0}.cov.list".format(
#             log_name.split(".")[0])).readlines()

#     all_cov_infos = []
#     for cov in cov_list:
#         item = cov.strip().split("coverage file: ")[-1].strip()
#         # print(item)
#         all_cov_infos.append(json.load(open(item))[-1])

#     if len(all_cov_infos) == 0:
#         continue
#     code_cov = all_cov_infos[0]["code_cov"]
#     for cov_info in all_cov_infos:
#         cur_code_cov = cov_info["code_cov"]
#         assert code_cov[0] == cur_code_cov[0], "the number of instruction are not the same, please check"
#         code_cov[1] = [cur_code_cov[1][i] or code_cov[1][i]
#                        for i in range(code_cov[0])]
#         # print("current test coverage: {0}%".format(cov_info["cov_percentage"]))

#     print("Achieved coverage: {0}%".format(
#         sum(code_cov[1])/float(code_cov[0])*100))

#     print("****************************************************************")
