# coding: utf-8
import sys
import os
from glob import glob,iglob
from os.path import join
from argparse import ArgumentParser
import datetime
#Path_current=sys.argv[0]
#N_iter=sys.argv[1]
#Name_Rmapfile=sys.argv[2]
# parse input arguments

def safe_mkdir(dirname):
    try:
        os.mkdir(dirname)
    except:
        pass

parser = ArgumentParser()
parser.add_argument("-c", dest="control_dir", help="Path of control data",action='store',default='ctrl')
parser.add_argument("-e", dest="exp_dir", help="Path of experiement data",action='store',default='exp')
parser.add_argument("-n", dest="N_iter", help="Number of iteration",action='store',default=100,type=int)
parser.add_argument("-f", dest="Name_Rmapfile", help="File name of Rmap, Default: Rmap_beswarrest.nii",action='store',default='Rmap_beswarrest.nii')
parser.add_argument("-a", dest="allnii", help="Get all nii files, disregarding -f",action='store_true')
args = parser.parse_args()

print(args.N_iter)
#Path_current='/home/tyhuang/FACEmars'
Path_current = os.getcwd()
N_iter=args.N_iter
#Name_Rmapfile='Rmap_beswarrest.nii'
result_dir = join(Path_current,datetime.datetime.now().strftime("stat%m%d%H%M%S"))
safe_mkdir(result_dir)
if args.allnii:
    # 分別讀取 Path_current下面的cont與exp資料夾內的MARS結果資料夾，直接從各資料夾中讀取名稱為 Name_Rmapfile(Rmap_beswarrest.nii)的檔案
    list_control = glob(join(args.control_dir,'*.nii'))
    list_control.extend(glob(join(args.control_dir,'*.nii.gz')))
    list_experim = glob(join(args.exp_dir,'*.nii'))
    list_experim.extend(glob(join(args.exp_dir,'*.nii.gz')))
else:
    list_control = [f for f in iglob(join(args.control_dir,'**',args.Name_Rmapfile),recursive=True)]
    list_experim = [f for f in iglob(join(args.exp_dir,'**',args.Name_Rmapfile),recursive=True)]


print('Control datafiles:')
for ii in range(len(list_control)):print('%d:%s' % (ii,list_control[ii]))
print('Exp datafiles:')
for ii in range(len(list_experim)):print('%d:%s' % (ii,list_experim[ii]))

# 列出control內所有的影像路徑
if len(list_control) > 0:
    str_control = ' '.join(list_control)
    # 把所有control受試者的Rmap合併成一個四維的Rmaps
    str_OSins='fslmerge -t %s %s ' % (join(result_dir,'contRmaps'),str_control)
    os.system(str_OSins)
    # 做出control的One sample t-test結果
    str_OSins='randomise -i %s/contRmaps -o %s/contOnettst -1  -n %d --T2' % (result_dir ,result_dir ,N_iter)
    os.system(str_OSins)


# 列出Expriment內所有的影像路徑
if len(list_experim) > 0:
    str_experim = ' '.join(list_experim)
    # 把所有Expriment受試者的Rmap合併成一個四維的Rmaps
    # str_OSins='fslmerge -t '+ Path_current + '/expRmaps '+ str_experim
    str_OSins='fslmerge -t %s %s ' % (join(result_dir,'expRmaps'),str_experim)
    os.system(str_OSins)
    # 做出Expriment的One sample t-test結果
    str_OSins='randomise -i %s/expRmaps  -o %s/expOnettst -1  -n %d --T2'%(result_dir ,result_dir ,N_iter)
    os.system(str_OSins)







if len(list_experim) > 0:
    # 把兩個群組的Rmaps合併成一個，並且由design.mat決定群組
    str_OSins='fslmerge -t allRmaps '+ result_dir + '/contRmaps ' + result_dir + '/expRmaps '
    os.system(str_OSins)

    # 若兩組資料只是單純的兩群不同受試者比較Two-Sample Unpaired T-test，而非Two-Sample Paired T-test (Paired Two-Group Difference)
    # 可以用 design_ttest2 檔案名稱 群組A數目 群組B數目 來建立design.mat以及design.con
    # design.mat是GLM用來分辨不同群組的矩陣。design.con是不同群組之間的contrast(譬如說A >B 或A<B)
    str_OSins='design_ttest2 %s/design %d %d' % (result_dir , len(list_control),len(list_experim))
    os.system(str_OSins)

    # 執行兩群組之間的Two sample t-test
    str_OSins='randomise -i %s/allRmaps -o %s/twosample -d design.mat -t design.con --T2 -n %d' % (result_dir, result_dir, N_iter)
    os.system(str_OSins)
