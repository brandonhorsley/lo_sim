"""
Code to basically mimic nonlinear boson sampling paper, will start simple with a beamsplitter, then nonlinearity then beamsplitter

- Need to validate KLM CNOT understanding, was under impression that deterministic NLS would make it KLM CNOT deterministic but am getting different states
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
d=2 #dimension

H_gate = np.array([[1, 1], [1, -1]]) / np.sqrt(2)

input_state=PhotonicState()
input_state.n=n
input_state.d=d

input_state[(0,2)]=0 #|00>
input_state[(0,3)]=0 #|01>
input_state[(1,2)]=0 #|10>
input_state[(1,3)]=1 #|11>

circuit.add_input_state(input_state)

#Below hashed out, BS uses imaginary form so not hadamard gate
#circuit.add_optical_layer(BS(R=0.5,offset=2))
#circuit.add_optical_layer(BS(R=0.5,offset=1))
circuit.add_optical_layer(OpticalUnitary(U=H_gate,label="BS", offset=2))
circuit.add_optical_layer(OpticalUnitary(U=H_gate,label="BS", offset=1))

circuit.draw()

sim=FullUnitaryEvolution(circuit)
first_state=sim.full_output_state()

#original config for NLS:1,0,0,pi
eta=1
l_NL=0
phi=0
phi_NL=np.pi

#eta=.9
#l_NL=0.1
#phi=0.2
#phi_NL=np.pi

def NLtransform(photonic_state,rails):
    if isinstance(photonic_state,PhotonicState):
        iterator=iter(photonic_state.keys())
        for i,(modes,number) in enumerate(photonic_state.items()):
            #Need to obtain counts of each mode number, e.g. (0,0) is 2 counts of 0, (0,1) is 1 count of 0 and 1 count of 1
            counter=Counter(modes)
            
            for k,v in counter.items():
                if k in rails:
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

second_state=NLtransform(first_state,rails=[1,2])
#second_state.modes={0,1,2,3} #can't set attribute without modifying lo_sim

"""
Below block is for 'grounding' the state, since circuit number of modes is determined by input state so e.g. if no photons occupy the 0 mode out of 4 modes then the circuit will think there is only three modes which will screw over the detectors line
"""
#Find list of intended modes that aren't reflected in the input state modes
main_list = list(set(range(4)) - set(second_state.modes))
for _ in range(len(main_list)):
    second_state[(main_list[_],0)]=0

circuit2=Circuit()

circuit2.add_input_state(second_state)

#circuit2.add_optical_layer(BS(R=0.5,offset=1))
#circuit2.add_optical_layer(BS(R=0.5,offset=2))
circuit2.add_optical_layer(OpticalUnitary(U=H_gate,label="BS", offset=1))
circuit2.add_optical_layer(OpticalUnitary(U=H_gate,label="BS", offset=2))

circuit2.add_detectors([0,1,2,3])
circuit2.draw()

sim2=FullUnitaryEvolution(circuit2)
output_state=sim2.full_output_state()
print(output_state)