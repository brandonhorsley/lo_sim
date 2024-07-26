"""
Code to basically mimic nonlinear boson sampling paper, will start simple with a beamsplitter, then nonlinearity then beamsplitter

- NLtransform needs work, tuple only specific to case of 1 photon on BS, need to enforce basis?
- Could an alternate idea to approach be using SwapOut gate and do U_eff heralding technique
- why does lo_sim demand that photon number equal the number of modes?
- Edited states.py since original is_fixed_photon_number was't working as intended, made a PR to original repo
- More bug problems, so when photon_number input isn't [1,x] or [x,x] then it breaks since it slices out a faulty 
  submatrix which isn't square and so a permanent can't be calculated, this needs to be fixed and ideally in the process 
  keep track of length of mode as that will be if criteria for NLtransform. Also still need to fix n_systems
"""

from photonic_circuit import Circuit
from optical_elements import DFT,BS,SwapOut
from states import PhotonicState, QuditState
from circuit_simulators import FullUnitaryEvolution
from get_amplitude import create_get_amp_from_out_modes
import numpy as np

circuit = Circuit()
d=2 #number of modes
modes=[0,1]
photon_numbers=[3,2] #[1,4] is a special case, why? Because faulty photon_number call says photon_number=1 so 
test=PhotonicState({(mode,)*n : 1 for mode, n in zip(modes, photon_numbers)})
print(test)
#print(test)
print()
#circuit.add_input_state(input_state)
circuit.add_input_state(test)
circuit.add_optical_layer(BS(0))

circuit.draw()
#print(circuit.U)
#print(circuit.photon_number)
sim=FullUnitaryEvolution(circuit)
first_state=sim.full_output_state()
print(first_state)
print()

#original config for NLS:1,0,0,pi
eta=.9
l_NL=0.1
phi=0.2
phi_NL=np.pi
#print(enumerate(first_state.items()))

def NLtransform(photonic_state):
    #print(photonic_state.photon_number)
    iterator=iter(photonic_state.keys())
    for i,(modes,number) in enumerate(photonic_state.items()):
        print(modes)
        #print(photonic_state.photon_number)
        print(number)
        p=len(next(iterator))
        print(p)
        for _ in range(len(modes)):
            if p==0:
                photonic_state[modes]=photonic_state[modes]
            if p==1:
                #print("1 state")
                #print(photonic_state)
                photonic_state[modes]*=np.sqrt(eta*(1-l_NL))*np.exp(1j*phi)
            if p==2:
                photonic_state[modes]*=eta*np.exp(1j*((2*phi)+phi_NL))
    return photonic_state

second_state=NLtransform(first_state)
print(second_state)
print()
circuit2=Circuit()

circuit2.add_input_state(second_state)
circuit2.add_optical_layer(BS(0))
circuit2.add_detectors([0,1])
circuit2.draw()

sim2=FullUnitaryEvolution(circuit2)
output_state=sim2.full_output_state()
print(output_state)