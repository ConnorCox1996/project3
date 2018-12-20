
import tensorflow as tf 
tf.enable_eager_execution()

from tensorflow import linalg

import argparse
import math
import numpy as np
#Check if this messes with coverage??
#definitely FIX FORMATTING OF COMMENTS ABOVE FN
'''HANDLING INPUT TABLE
this takes the input table of position & potential energy values,
these values must be stored, either as:
.txt or .csv files
*Note: if .txt, values must be separated commas (see EXAMPLE)
.................................................................
-->position & potential energy Table must be saved in the same directory this Schrodinger.py file is saved to & run from
.................................................................

Position & Potential Energy Values are stored in 'positions' & 'potentialEnergy' arrays
to make values accessible for calculations
'''

import csv
with open('potential_energy.2.dat', 'r') as file:
    reader = csv.DictReader(file)
    positions=[]
    potentialEnergy=[]
    for row in reader:
        positions.append(float(row['position']))
        potentialEnergy.append(float(row['Potential Energy']))

#Just printing for my use
#
#
print('OUTSIDE')
print('pos')
print(positions)
print('Ep')
print(potentialEnergy)

c=1

#Arg Parse Stuff left out because it causes tests to fail...
'''
def commandLineArgParse():
    parser=argparse.ArgumentParser()
    parser.add_argument('--c', type = int, default = 1, help = 'c, a constant, default value is 1')
    parser.add_argument('--bs', type=int, default = 3, help = 'the size of the basis set, default is 3')
    args = parser.parse_args()
    constant=args.c
    basisSize=args.bs
    return constant, basisSize

print('OUTSIDE')
commandLineArguments=commandLineArgParse()
c=commandLineArguments[0]
sizeOfBasis=commandLineArguments[1]
print(c)
print(sizeOfBasis)
'''
print('')
print('')
print('')

''' deltaSquareFunc
 -----------------------------------------------------------------------------------------------
    function computes del**2 of each element in the basis set
    where the basis set is the Fourier series of n # of terms, where n is the specified basis size
    -----------------------------------------------------------------------------------------------
Please Note: Complications with handling lambda functions generated via iteration
               have caused unusual form of these values (components of values stored amongst 2 arrays) 

**The fourier series is written as follows:
    = a0 + [summation(from 0 to N) aNsin(aN)] + [summation(from 0 to M) aMcos(aM)]
** del**2 of each term (exclusive of the first, where del**2 of term =0) is written as follows:
    = [summation(from 0 to N) -(aN**2)*sin(aN)] + [summation from(0 to M) -(aM**2)*cos(aM)]


INPUT-->size of basis set
RETURNS--> 2 arrays, Array 1: a list of aN & aM terms (see above)
                     Array 2: lambda functions which take x & y inputs, where y is an aN or aM value, & x is the value which the function is evaluated at 

'''
def deltaSquareFunc(size):
    delt=[lambda y,x: 0]
    yValues=[0]
    terms=math.ceil( (size-1)/2)

    for i in range(1,terms+1):
        yValues.append(i)
        yValues.append(i)
    if (len(yValues)>size):
        yValues.pop(-1)

    for i in range(1,terms+1):
        delt.append(lambda y,x: -(y**2)*math.sin(y*x))
        delt.append(lambda y,x: -(y**2)*math.cos(y*x))
    if(len(delt)>size):
        delt.pop(-1)   

    return yValues, delt
   


'''
Applying Operator to basis, finding H_hat,
allows us to represent operator as matrix
'''

c=3
def operatorMatrix (positions, potentialEnergy, yValues, deltaList,c):
    matrix = np.zeros((len(positions), len(deltaList)))

    for i in range(0,len(yValues)):
        # Ham.append('NEW')
        del2=deltaList[i]
        for j in range(0, len(positions)):
            opEval = (-c*del2(yValues[i],positions[j]))+potentialEnergy[j]
            matrix[j][i]=opEval
            dim=[len(deltaList),len(positions)]
    return matrix,dim

source=deltaSquareFunc(7)
ys=source[0]
fns=source[1]
first = operatorMatrix(positions, potentialEnergy, ys, fns,c)

def generateTfMatrix(Matrix):
    matr=Matrix[0]
    col=Matrix[1][0]
    rows=Matrix[1][1]

    hold=[]
    for i in range(0,rows):
        row=matr[i,:]
        hold.extend(row)

    tens=tf.Variable(tf.zeros(col*rows))
    tens=tf.assign(tens,hold)
    tens=tf.reshape(tens,[rows,col])
    tens=tf.cast(tens, tf.float64)
    return tens

matrixgen=generateTfMatrix(first)
print('MATRIXGEN')
#print(matrixgen)
#print(matrixgen[0])
#print(matrixgen[:,0])

def eigen(tensorMatrix):
    e,v=tf.linalg.eigh(tensorMatrix)
    eigenValue=e[0]
    print('Lowest Energy State of Hamiltonian : ')
    print(e[0])
    print('')
    print('Basis Set Coefficients for wavefunction correspondin to lowest-energy state')
    print(v[0])
    return e,v

tfm=generateTfMatrix(first)
res=eigen(tfm)
#print(res)
