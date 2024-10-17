import csv 
import re  

# output_csv_path = "Dapp-Automata-data/rq1-result-simplified.csv"
# csv_path = "Dapp-Automata-data/rq1-result.csv"

output_csv_path = "Dapp-Automata-data/rq1-result-simplified-fix.csv"
csv_path = "Dapp-Automata-data/rq1-result-fix.csv"
reader = csv.reader(open(csv_path))
SMCON = r"FSM-([0-9]+)\.gv"
RPNI = r"BlueFringeMDLDFA\.dot"
KTAIL_one = r"Ktail-1\.gv"
KTAIL_two = r"Ktail-2\.gv"
SEKT_one = r"SEKT-1\.gv"
SEKT_two = r"SEKT-2\.gv"
CONTRACTOR_PLUS = r"contractorplus\.gv"


result_smcon = dict()
result_rpni = dict()
result_one = dict()
result_two = dict()
resutl_sekt_one = dict()
resutl_sekt_two = dict()
result_contractor = dict()
cnt = 0 
for line in reader:
    if cnt == 0:
        cnt += 1
        continue
    else:
        cnt += 1
    project, g_state_number, g_transition_number, result_file, m_state_number, m_transition_number, recall, precision, test_case_accuracy = line
    project = "PingPongGame" if project == "Starter" else project
    
    result_file = result_file.strip()
    recall =  float(recall)
    precision = float(precision)
    test_case_accuracy = float(test_case_accuracy)
    
    m = re.match(SMCON, result_file)
    if m is not None:
        count = int(m.group(1))
        if project not in result_smcon:
            result_smcon[project] = dict()
        result_smcon[project][count] = [m_state_number, recall, precision, 2*recall*precision/(recall+precision), test_case_accuracy]
    else:
        m = re.match(RPNI, result_file)
        if m is not None:
            result_rpni[project] = [m_state_number, recall, precision, 2*recall*precision/(recall+precision), test_case_accuracy]
        else:
            m = re.match(KTAIL_one, result_file)
            if m is not None:
                result_one[project] = [m_state_number, recall, precision, 2*recall*precision/(recall+precision), test_case_accuracy]
            else:
                m = re.match(KTAIL_two, result_file)
                if m is not None:
                    result_two[project] = [m_state_number, recall, precision, 2*recall*precision/(recall+precision), test_case_accuracy]
                else:
                    
                    m = re.match(SEKT_one, result_file)
                    if m is not None:
                        resutl_sekt_one[project] = [m_state_number, recall, precision, 2*recall*precision/(recall+precision), test_case_accuracy]
                    else:
                        m = re.match(SEKT_two, result_file)
                        if m is not None:
                            resutl_sekt_two[project] = [m_state_number, recall, precision, 2*recall*precision/(recall+precision), test_case_accuracy]
                        else:
                            m = re.match(CONTRACTOR_PLUS, result_file)
                            if m is not None:
                                result_contractor[project] = [m_state_number, recall, precision, 2*recall*precision/(recall+precision), test_case_accuracy]
                            else:
                                assert False, f"{result_file} is not supported"

rows = []
for project in result_smcon:
    final_smcon_result = result_smcon[project][max(result_smcon[project].keys())]
    # rpni_result = result_rpni[project]
    ktail_one_result = result_one[project]
    ktail_two_result = result_two[project]
    sekt_one_result = resutl_sekt_one[project]
    sekt_two_result = resutl_sekt_two[project]
    contractor_result = result_contractor[project]
    rows.append([project] + ktail_one_result + ktail_two_result + sekt_one_result + sekt_two_result + contractor_result + final_smcon_result)

writer = csv.writer(open(output_csv_path, "w"))
writer.writerow(["project"] + ["1-Tail"] + [""]*4 + ["2-tail"]  + [""]*4 + ["sekt-1"] + [""]*4  + ["sekt-2"] + [""]*4  + ["contractor++"] + [""]*4 + ["SMCON"] + [""]*4)
writer.writerow(["", "result state", "recall", "precision", "F-measure", "test_case_accuracy", "result state", "recall", "precision", "F-measure", "test_case_accuracy", "result state", "recall", "precision", "F-measure", "test_case_accuracy", "result state", "recall", "precision", "F-measure", "test_case_accuracy", "result state", "recall", "precision", "F-measure", "test_case_accuracy", "result state", "recall", "precision", "F-measure", "test_case_accuracy"])
writer.writerows(rows)



