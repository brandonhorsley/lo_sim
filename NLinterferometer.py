"""
Code to basically mimic nonlinear boson sampling paper, will start simple with a beamsplitter, then nonlinearity then beamsplitter

- NLtransformation could be tidier since it is specific if cases rather than being general
"""

from photonic_circuit import Circuit
from optical_elements import DFT,BS,SwapOut
from states import PhotonicState, QuditState
from circuit_simulators import FullUnitaryEvolution
from get_amplitude import create_get_amp_from_out_modes
import numpy as np

from collections import Counter

circuit=Circuit()
n=2 #Number of photons
d=2 #number of modes

input_state=PhotonicState()
input_state.n=n
input_state.d=d

psi_in = np.arange(d**n)*1.0
#print(psi_in)
psi_in /= np.linalg.norm(psi_in)
#print(psi_in)
psi_in = psi_in.reshape(tuple([d]*n))
#print(psi_in)

#input_state[(0,0)]=psi_in[0,0]
input_state[(0,1)]=1
#input_state[(0,1)]=psi_in[1,0] #same state
#input_state[(1,0)]=psi_in[0,1] #same state
#input_state[(1,1)]=psi_in[1,1]

print(input_state)
print()
circuit.add_input_state(input_state)
circuit.add_optical_layer(BS(R=0.5)) 

circuit.draw()
#print(circuit.U)
#print(circuit.photon_number)
sim=FullUnitaryEvolution(circuit)
first_state=sim.full_output_state()
print(first_state)
print()

#original config for NLS:1,0,0,pi
eta=1
l_NL=0
phi=0
phi_NL=np.pi

#eta=.9
#l_NL=0.1
#phi=0.2
#phi_NL=np.pi

#print(enumerate(first_state.items()))
"""
def NLtransform(photonic_state):
    if isinstance(photonic_state,PhotonicState):
        iterator=iter(photonic_state.keys())
        for i,(modes,number) in enumerate(photonic_state.items()):
            print(modes)
            #Need to obtain counts of each mode number, e.g. (0,0) is 2 counts of 0, (0,1) is 1 count of 0 and 1 count of 1
            count0=modes.count(0)
            count1=modes.count(1)
            #count(modes,2)
            if count0==0:
                pass
            if count0==1:
                photonic_state[modes]*=np.sqrt(eta*(1-l_NL))*np.exp(1j*phi)
            if count0==2:
                photonic_state[modes]*=eta*np.exp(1j*((2*phi)+phi_NL))
            if count1==0:
                pass
            if count1==1:
                photonic_state[modes]*=np.sqrt(eta*(1-l_NL))*np.exp(1j*phi)
            if count1==2:
                photonic_state[modes]*=eta*np.exp(1j*((2*phi)+phi_NL))
        return photonic_state
    else:
        print("The state isn't a photonic state. Skipping transformation")
        return photonic_state
print(Counter((0,0)))
"""

def NLtransform(photonic_state):
    if isinstance(photonic_state,PhotonicState):
        iterator=iter(photonic_state.keys())
        for i,(modes,number) in enumerate(photonic_state.items()):
            print(modes)
            #Need to obtain counts of each mode number, e.g. (0,0) is 2 counts of 0, (0,1) is 1 count of 0 and 1 count of 1
            counter=Counter(modes)
            
            for k,v in counter.items():
                if v==0:
                    pass
                if v==1:
                    photonic_state[modes]*=np.sqrt(eta*(1-l_NL))*np.exp(1j*phi)
                if v==2:
                    photonic_state[modes]*=eta*np.exp(1j*((2*phi)+phi_NL))
        return photonic_state
    else:
        print("The state isn't a photonic state. Skipping transformation")
        return photonic_state

second_state=NLtransform(first_state)
print(second_state)
print()

#test=PhotonicState()
#test[(0,0)]=1
#print("test")
#print(NLtransform(test))

circuit2=Circuit()

circuit2.add_input_state(second_state)
circuit2.add_optical_layer(BS(R=0.5))
circuit2.add_detectors([0,1])
circuit2.draw()

sim2=FullUnitaryEvolution(circuit2)
output_state=sim2.full_output_state()
print(output_state)