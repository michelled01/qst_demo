import cmath
import numpy as np
import math
import scipy
from scipy.linalg import sqrtm
from numpy.linalg import eig

''' process for calculating fidelity and trace distance:
    # fidelity 
        # theoretical
            # get theta and phi 
            # multiply QWP(phi)*HWP(theta)*|H> = pure state
            # do the outer product = theo density matrix
        # experimental
            # get P_i (Total T)
            # get counts (D,A,R,L,H,V)
            # calculate expectations (<X> = (D-A)/T, <Y> = (R-L)/T, <Z> = (H-V)/T)
            # calculate the exp. density matrix
        # comparison
            # F = <PS| exp.DS |PS>
            # ε = 1-F
        
    # trace distance
        # TD = 0.5*Tr[sqrt((ρ-φ)ᵗ(ρ-φ))] 
        # for subtraction, use the DS's we got from fidelity
        # for square rooting, https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.sqrtm.html '''

### fidelity ###

def HWP(theta):
    tl = math.cos(2*theta)
    tr = math.sin(2*theta)
    bl = math.sin(2*theta)
    br = (-1)*math.cos(2*theta)
    return np.array([[tl, tr], [bl, br]])

def QWP(phi):
    tl = pow(math.cos(phi),2)+1j*pow(math.sin(phi),2)
    tr = (1-1j)*math.sin(phi)*math.cos(phi)
    bl = (1-1j)*math.sin(phi)*math.cos(phi)
    br = pow(math.sin(phi),2)+1j*pow(math.cos(phi),2)
    return np.array([[tl, tr], [bl, br]])

#calculates the final theoretical vector |v>
def pure_state(theta, phi):
    #init
    hwp = HWP(theta)
    qwp = QWP(phi)
    H = np.array([[1.0],[0.0]])
    #calc
    return np.matmul(qwp, np.matmul(hwp,H))
    
def outer_product(PS):
    PS_t = np.conj(np.transpose(PS))
    return np.matmul(PS,PS_t)

#calculate expectation values and computes density matrix
def experimental(T,D,A,R,L,H,V):
    #calc expectation vals
    expX = (D-A)/T
    expY = (R-L)/T
    expZ = (H-V)/T

    #init matricies
    I = np.array([[1.0,0.0],[0.0,1.0]])
    X = np.array([[0.0,1.0],[1.0,0.0]])
    Y = np.array([[0.0,-1j],[1j,0.0]])
    Z = np.array([[1.0,0.0],[0.0,-1.0]])
    
    #density matrix calc
    return 0.5*(I + expX*X + expY*Y + expZ*Z)

def fidelity(PS, exp_DS):
    bra = np.conj(np.transpose(PS))
    mid = exp_DS
    ket = PS
    return np.matmul(bra,np.matmul(mid,ket))

def error(f):
    return 1-f


### trace distance ###

def traceDist(theo_DS, exp_DS):
    diff = theo_DS - exp_DS
    diff_t = np.conj(np.transpose(diff))
    square = np.matmul(diff,diff_t)
    sqrt_matrix = sqrtm(square)
    mat = sqrt_matrix
    sum = 0
    for i in range(len(mat)):
       sum += mat[i][i]
    return sum/2

### eigenvalue check ###
def get_eigs(theo_DS):
    return eig(theo_DS)

#Testing WebApp
def go(theta, phi,totalPower,Dcounts,Acounts,Rcounts,Lcounts,Hcounts,Vcounts):
    PS = pure_state(math.radians(theta),math.radians(phi))
    theo_DS = outer_product(PS)
    exp_DS = experimental(totalPower,Dcounts,Acounts,Rcounts,Lcounts,Hcounts,Vcounts)

    e_value,e_vector = get_eigs(theo_DS) # experimental matrix value imprecise
    err = error(fidelity(PS,exp_DS)[0][0])
    trD = traceDist(exp_DS, theo_DS)
    
    # formatting
    e_value[0] = '%.3f'%(e_value[0])
    e_value[1] = '%.3f'%(e_value[1])
    a = str(e_value[0])
    a = a.strip('(')
    a = a.strip(')')
    b = str(e_value[1])
    b = b.strip('(')
    b = b.strip(')')
    err = '%.3f'%(err)
    trD = '%.3f'%(trD)    
    return [a,b, err, trD]


''' manual testing: 
theta=80
phi=50
total power = 5.6 µW
H = 3.2 
V = 2.574
D = 0.654
A = 4.9
R = 1
L = 4.52

# testing fidelity (input in degrees)
print("enter preparation theta: ")
theta = float(input())
theta = math.radians(theta)
print("enter preparation phi: ")
phi = float(input())
phi = math.radians(phi)

print("enter total power: ")
totalPower = float(input())
print("enter recorded H count: ")
Hcounts = float(input()) 
print("enter recorded V count: ")
Vcounts = float(input()) 
print("enter recorded D count: ")
Dcounts = float(input()) 
print("enter recorded A count: ")
Acounts = float(input()) 
print("enter recorded R count: ")
Rcounts = float(input()) 
print("enter recorded L count: ")
Lcounts = float(input()) 

PS = pure_state(theta,phi)
#testing experimental
exp_DS = experimental(totalPower,Dcounts,Acounts,Rcounts,Lcounts,Hcounts,Vcounts)
print("error: ", error(fidelity(PS,exp_DS)[0][0]))

#testing trace
print("trace distance: ",str(traceDist(experimental(totalPower,Dcounts,Acounts,Rcounts,Lcounts,Hcounts,Vcounts), outer_product(PS))))

'''