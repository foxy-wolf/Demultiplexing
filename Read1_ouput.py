#! /usr/bin/env python
#-*-coding:utf-8-*-
import sys
import os
import json
from numpy import mean
from os import path

def main(work_dir, run_id, order_dic):

        eList = []
        out_dic = {}
        rna_dic = {}
        laneOut_dic = {}
        rna_stat = {}
        laneOut_stat = {}
        xlsStr = ""

        with open(work_dir + "/R1_Demultiplexed/" + run_id + "_Output.xls", 'w+') as outXls:
                outXls.write("Sample ID" + '\t' + " Index ID" + '\t' + "Original Novo ID" + '\t' + "Contract Number" + '\t' + " Requested Output (G)" + '\t' + "Raw Output (G)" + '\t' + "Productivity (%)" + '\t' + "rRNA Content (%)" + '\t' + "Project Coordinator" +'\n')

                with open(work_dir + "/R1_Demultiplexed/production.txt", 'w+') as prodFile: 
                        prodFile.write("Sample ID\tRequested Data (G)\tRaw Output (G)\tProductivity (%)\n")

                        samSheet = open(work_dir + "/clean/SampleList", 'r')
                        for samLine in samSheet:
                                samLine = samLine.strip('\n')
                                lane = samLine[-1]
                                samArray = samLine.split("_")
                                sample = samArray[0]

                                order = order_dic[lane]

                                data_req = 1e60

                                with open(work_dir + "/R1_Demultiplexed/data.txt", 'r') as f_data:
                                        for dataLine in f_data:
                                                dataLine = dataLine.strip('\n')
                                                sam_ID = dataLine.split("\t")[0]
                                                sam_data = dataLine.split("\t")[1]
                                                if samLine == sam_ID:
                                                        data_req = sam_data
                                                        sam_ind = dataLine.split("\t")[2]
                                                        sam_ori = dataLine.split("\t")[3]
                                                        sam_proj = dataLine.split("\t")[4]
                                                        sam_pc = dataLine.split("\t")[5]
                                f_data.close

                                f_email = open("/HWPROJ1/XJ/demultiplex/PC-list-new.txt", 'r')

                                for emLine in f_email:
                                        emLine = emLine.strip("\n")
                                        emArr = emLine.split("_")
                                        if sam_pc == emArr[0]:
                                                pc_email = emArr[1]

                                f_email.close

                                f_json = open(work_dir[:-1] + order + "/R1_Demultiplexed/Stats/Stats.json", 'r')

                                output_dic = json.loads(f_json.read())

                                output = ""
                                prod = ""

                                for i in range(len(output_dic['ConversionResults'][0]['DemuxResults'])):
                                        if sample == output_dic['ConversionResults'][0]['DemuxResults'][i]['SampleId']:
                                                output = 2 * output_dic['ConversionResults'][0]['DemuxResults'][i]['Yield']/1e9
                                                prod = 100 * output/float(data_req)

                                prodFile.write(samLine + "\t" + data_req + "\t" + str(output) + "\t" + str(prod) + "\n")

                                f_json.close

                                rrna = ""
                                if sample[:4] == "CRRA":
                                        f_rrna = open(work_dir + "/rRNA.summary.txt", 'r')
                                        for rnaLine in f_rrna:
                                                rnaLine = rnaLine.strip('\n')
                                                rnaArr = rnaLine.split('\t')
                                                if samLine == rnaArr[0]:
                                                        rrna = rnaArr[1]
                                                        if lane in rna_dic.keys():
                                                                rna_dic[lane].append(float(rrna))
                                                        else:
                                                                rna_dic[lane] = [float(rrna)]
                                        f_rrna.close


                                if sample[:4] != "CKDL":
                                        xlsStr += samLine + '\t' + sam_ind + '\t' + sam_ori + '\t' + sam_proj + '\t' + data_req + '\t' + str(output) + '\t' + str(prod) + '\t' + rrna + '\t' + sam_pc + '\n'
                                        if lane in laneOut_dic.keys():
                                                laneOut_dic[lane].append(prod)
                                        else:
                                                laneOut_dic[lane] = [prod]


                                if lane in out_dic.keys() and sample[:4] != "CKDL":
                                        color = "black"
                                        if prod < 100:
                                                color = "red"
                                                try:
                                                        eList.append(pc_email)
                                                except Exception:
                                                        pass
                                        if rrna != "":
                                                if float(rrna) > 15:
                                                        rrna = rrna + "*" 
                                        out_dic[lane] += "                  <tr style=\"text-align:center; color:" + color + ";\">\n" + "                          <td>" + samLine + '</td>\n' + "                          <td>" + sam_ind + '</td>\n' + "                          <td>" + sam_ori + '</td>\n'  + "                          <td>" + sam_proj + '</td>\n' +  "                          <td>" + data_req + '</td>\n'  + "                          <td>" + str(output) + '</td>\n'  + "                          <td>" + str(prod) + '</td>\n'  + "                          <td>" + rrna + '</td>\n'  + "                          <td>" + sam_pc + "</td>" + '\n' + "                   </tr>" + '\n'
                                elif sample[:4] != "CKDL":
                                        color = "black"
                                        if prod < 100:
                                                color = "red"
                                        if rrna != "":
                                                if float(rrna) > 15:
                                                        rrna = rrna + "*"
                                        out_dic[lane] = "                  <tr style=\"text-align:center; color:" + color + ";\">\n" + "                          <td>" + samLine + '</td>\n' + "                           <td>" + sam_ind + '</td>\n' + "                          <td>" + sam_ori + '</td>\n'  + "                          <td>" + sam_proj + '</td>\n' +  "                          <td>" + data_req + '</td>\n'  + "                          <td>" + str(output) + '</td>\n'  + "                          <td>" + str(prod) + '</td>\n'  + "                          <td>" + rrna + '</td>\n'  + "                          <td>" + sam_pc + "</td>" + '\n'


                        samSheet.close
                prodFile.close

                outXls.write(xlsStr)
        outXls.close

        for keys in rna_dic.keys():
                rna_mean = mean(rna_dic[keys])
                rna_min = min(rna_dic[keys])
                rna_max = max(rna_dic[keys])
                rna_stat[keys] = [rna_mean, rna_min, rna_max]

        for keys in laneOut_dic.keys():
                laneOut_mean = mean(laneOut_dic[keys])
                laneOut_min = min(laneOut_dic[keys])
                laneOut_max = max(laneOut_dic[keys])
                laneOut_stat[keys] = [laneOut_mean, laneOut_min, laneOut_max]


        with open(work_dir + '/R1_Demultiplexed/output.html', 'w+') as outFile:
                outFile.write("<html>\n  <body>\n          <br style=\"font-weight: bold\">Run ID: " + run_id + "<br><br>Lane Summary (in-house only):<br><br>\n")
                for lane in sorted(laneOut_stat.keys()):
                        outFile.write("Lane " + str(lane) + ": Average %Productivity = " + str(laneOut_stat[lane][0]) + ", Min %Productivity = " + str(laneOut_stat[lane][1]) + ", Max %Productivity = " + str(laneOut_stat[lane][2]) + "<br>\n")
                outFile.write("<br>")
                for keys in sorted(rna_stat.keys()):
                        outFile.write("Lane " + str(keys) + ": Average %rRNA = " + str(rna_stat[keys][0]) + ", " + "Min %rRNA = " + str(rna_stat[keys][1]) + ", " +  "Max %rRNA: = " + str(rna_stat[keys][2]) + "<br>\n")

                outFile.write("<br><br>          <table style=\"width:100%\">\n                  <tr style=\"font-weight: bold\">\n                          <th>Sample ID</th>\n                          <th>Index ID</th>\n                          <th>Original Novo ID</th>\n                          <th>Contract Number</th>\n                          <th>Requested Output (G)</th>\n                          <th>Raw Output (G)</th>\n                          <th>Productivity (%)</th>\n                          <th>rRNA Content  (%)</th>\n                          <th>Project Coordinator</th>\n                  </tr>\n")

                for keys in sorted(out_dic.keys()):
                        outFile.write(out_dic[keys])

                outFile.write("          </table>\n  </body>\n</html>")
        outFile.close

        eList = list(dict.fromkeys(eList))

        with open(work_dir + '/R1_Demultiplexed/eList.txt', 'w+') as emailFile:
                for j in eList:
                        emailFile.write(j + '\n')
        emailFile.close



if __name__== "__main__":
        workDir = sys.argv[1]
        RunID = sys.argv[2]
        orderDict = sys.argv[3:]
        ordDic = {}
        orderList = list(orderDict[0])
        for i in range(0,len(orderList)/2):
                ordDic[orderList[i*2]] = orderList[i*2 + 1]

        main(workDir, RunID, ordDic)