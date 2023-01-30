import numpy as np
import fastdtw as fd
import argparse
import csv
import matplotlib.pyplot as plt
from scipy.spatial.distance import euclidean
from scipy.ndimage.filters import gaussian_filter
from scipy.signal import medfilt
from terminalPrintColors import tcolors 

parser = argparse.ArgumentParser(
        description='Select best example for using it in the classifier')
parser.add_argument('--actionprefix', '-ap', default='a1_', help='Action prefix in CSV file name (e.g. \'a1_s1_\')')
parser.add_argument('--varthresh', '-vt', default='0.05', help='Min. variance to use dimension in DTW')
parser.add_argument('--sigma', '-s', default='0.5', help='Sigma for Gaussian smoothing')
args = parser.parse_args()

file_name_suffix = '_color.avi.csv'

full_file_names = [args.actionprefix + 't1' + file_name_suffix, args.actionprefix + 't2' + file_name_suffix, args.actionprefix + 't3' + file_name_suffix, args.actionprefix + 't4' + file_name_suffix]

print(full_file_names)


for fn in full_file_names:
    totalDistSum = 0
    for fnn in full_file_names:
    
        if fn == fnn:
            continue

        coordSequences1 = [[] for _ in range(36)] # two dim. list with list for every coordinate
        coordSequences2 = [[] for _ in range(36)]
        normCoordSequences1 = [[] for _ in range(36)]
        normCoordSequences2 = [[] for _ in range(36)]

        # read csv file of first sequence to list
        with open(fn, 'r') as csvfile:
            reader_seq1 = csv.reader(csvfile, delimiter=',')
            for row in reader_seq1:
                row_f = [float(e) for e in row] # contains strings, cast to float explicitly
                for i in range(36): # 18 key points -> 36 coordinates
                    coordSequences1[i].append(row_f[i])

        # read csv file of second sequence to list
        with open(fnn, 'r') as csvfile:
            reader_seq2 = csv.reader(csvfile, delimiter=',')
            for row in reader_seq2:
                row_f = [float(e) for e in row] # contains strings, cast to float explicitly
                for i in range(36): # 18 key points -> 36 coordinates
                    coordSequences2[i].append(row_f[i])

        compareDimensions = set() # add all dimensions to set that have a variance > threshold in either sequence

        if float(args.sigma) > 0.1:
            for i,s in enumerate(coordSequences1):
                s = medfilt(s, 5)
                coordSequences1[i] = s

            for i,s in enumerate(coordSequences2):
                s = medfilt(s, 5)
                coordSequences2[i] = s

        for i,kps in enumerate(coordSequences1):
            varSeq = np.var(kps)
            mean = np.mean(kps)
            std = np.std(kps)
            nmkps = [x-mean for x in kps]
            nmstdkps = [x/std for x in nmkps] # TODO: this might divide by zero
            normCoordSequences1[i] = nmstdkps
            #print('S1: Variance Signal ', i, ': ' , varSeq)
            if varSeq > float(args.varthresh):
                compareDimensions.add(i)

        for i,kps in enumerate(coordSequences2):
            varSeq = np.var(kps)
            mean = np.mean(kps)
            std = np.std(kps)
            nmkps = [x-mean for x in kps]
            nmstdkps = [x/std for x in nmkps] # TODO: this might divide by zero
            normCoordSequences2[i] = nmstdkps
            #print('S2: Variance Signal ', i, ': ' , varSeq)
            if varSeq > float(args.varthresh):
                compareDimensions.add(i)

        print(compareDimensions)
        
        ''' 
        For some reason, the commumative property is violated if the dimensions
        are in a different order... possibly rounding errors. Therefore they have
        to be sorted before performing the  DTW. 
        '''
        compareDimensions = sorted(compareDimensions)

        f = plt.figure()

        plt.subplot(2,1,2)
        for i in range(36):
            plt.plot(normCoordSequences1[i], 'xkcd:grey', label=i)

        for i in compareDimensions:
            plt.plot(normCoordSequences1[i], 'xkcd:black', label=i, linewidth=4.0)
            plt.plot(normCoordSequences1[i], label=i, linewidth=3.0)

        plt.subplot(2,1,1)
        for i in range(36):
            plt.plot(normCoordSequences2[i], 'xkcd:grey', label=i)

        for i in compareDimensions:
            plt.plot(normCoordSequences2[i], 'xkcd:black', label=i, linewidth=4.0)
            plt.plot(normCoordSequences2[i], label=i, linewidth=3.0)

        f.savefig('signals.pdf', bbox_inches='tight')

        distSum = 0.0

        for dim in compareDimensions:
            distance, path = fd.fastdtw(normCoordSequences1[dim], normCoordSequences2[dim], dist=euclidean)
            distSum += distance
            #print(distance)
        print(tcolors.HEADER + "NORMALIZED DISTANCE: " + tcolors.ENDC + str(distSum))
        totalDistSum += distSum
    print(tcolors.ERR + fn + ':' + str(totalDistSum) + tcolors.ENDC)

