"""
Notes for understanding:

Qudit is basically just reassigning modes, current mentality is kind of like coupled systems so both may be in zero state but tensored together, so transforming to photonic state is just relabelling rails

Code breaks at add_optical_layer() saying got unexpected keyword argument, will try putting offset term in optical element

I think lo_sim doesn't work for number changing operations. This is because circuit photon number is defined by input state photon number which is defined by n_systems property of QuantumState which comes from len(next(iter(self.keys()))) which broke when past used but let me try and replicate in this code
"""

import numpy as np

# lo_sim modules
#from lo_sim.photonic_circuit import Circuit
#from lo_sim.optical_elements import BS, DFT, SwapOut, I, Swap, PhaseShift, OpticalUnitary
#from lo_sim.circuit_simulators import FullUnitaryEvolution, LayeredEvolution
#from lo_sim.states import QuditState, PhotonicState

from photonic_circuit import Circuit
from optical_elements import BS, DFT, SwapOut, I, Swap, PhaseShift, OpticalUnitary
from circuit_simulators import FullUnitaryEvolution, LayeredEvolution
from states import QuditState, PhotonicState

# testing fusion between 8 rail and 2 rail with measurement on fused qubit
d = 3  # dimension
n = 2  # number of photons

# psi_in = np.random.rand(d**n)
psi_in = np.arange(d**n)*1.0
print(psi_in)
psi_in /= np.linalg.norm(psi_in)
print(psi_in)
psi_in = psi_in.reshape(tuple([d]*n))
print(psi_in)

input_state = QuditState()
input_state.n = n  # number of photons
input_state.d = d  # dimension

input_state[(0,0)] = psi_in[0,0]
input_state[(1,0)] = psi_in[0,1]
input_state[(2,0)] = psi_in[0,2]
input_state[(0,1)] = psi_in[1,0]
input_state[(1,1)] = psi_in[1,1]
input_state[(2,1)] = psi_in[1,2]
input_state[(0,2)] = psi_in[2,0]
input_state[(1,2)] = psi_in[2,1]
input_state[(2,2)] = psi_in[2,2]
logical_systems = {0: (0, 1, 2), 1:(3, 4, 5)}  # mapping set of modes to qudit number

#print(logical_systems[0])

#for modes, amp in input_state.items():
    #print(modes)
    #for i, mode in enumerate(modes):
        #new_modes = tuple(logical_systems[i][mode] for i, mode in enumerate(modes))
        #print(i)
        #print(mode)
        #print(logical_systems[i])
        #print(logical_systems[i][mode])
        #state[new_modes] = amp 


photonic_state = input_state.to_photonic_state(logical_systems)

print("Input state, qudit:")
print(input_state)
print()
print("Input state, photonic:")
print(photonic_state)
print()
print("###########################################")
# alternative definition, directly photonic state
# might not necessarily correspond to a qudit state.
psi_in_bis = np.array([1,2,3], dtype=float)
psi_in_bis /= np.linalg.norm(psi_in_bis)
photonic_state_bis = PhotonicState()
photonic_state_bis[(0, 0)] = psi_in_bis[0]  # two photons in mode 0
photonic_state_bis[(0, 1)] = psi_in_bis[1]  # one photon in mode 0 and one in mode 1
photonic_state_bis[(1, 2)] = psi_in_bis[2]  # one photon in mode 1 and one in mode 2

print("Input state bis, photonic:")
print(photonic_state_bis)
print()

# TODO see here this is causing an error, all components from the state must have the same photon number
# if you comment it out, then it is fine, the 2 photon interference is computed
#photonic_state_bis[(1, 2, 2)] = 0  # here three photon state, one in 1 and two in 2; will cause an error later
#photonic_state_bis[(1, 2, 2)] = 1  # here three photon state, one in 1 and two in 2; will cause an error later
#print(photonic_state_bis) #as expected the above line breaks the code

H_gate = np.array([[1, 1], [1, -1]]) / np.sqrt(2)

# photonic simulation
circuit = Circuit()
circuit.add_input_state(photonic_state_bis)

# some linear optical circuit
#circuit.add_optical_layer(*[OpticalUnitary(U=H_gate, label="BS")] * 1, offset=0)
#circuit.add_optical_layer(*[PhaseShift(np.pi/2), PhaseShift(np.pi/3), PhaseShift(np.pi/4)]* 1 , offset=0)
#circuit.add_optical_layer(*[OpticalUnitary(U=H_gate, label="BS")] * 1, offset=1)
circuit.add_optical_layer(*[OpticalUnitary(U=H_gate, label="BS", offset=0)] * 1)
circuit.add_optical_layer(*[PhaseShift(np.pi/2), PhaseShift(np.pi/3), PhaseShift(np.pi/4)]* 1)
circuit.add_optical_layer(*[OpticalUnitary(U=H_gate, label="BS", offset=1)] * 1)


u = np.arange(d*n)  # input modes
v = np.array([3,4,5, 0,1,2])  # output modes. eg: swap first and second system
#circuit.add_optical_layer(*[Swap(u, v)], offset=0)
#circuit.add_optical_layer(*[OpticalUnitary(U=H_gate, label="BS")] * 1, offset=d)

#circuit.add_optical_layer(*[Swap(u, v), offset=0])
circuit.add_optical_layer(*[Swap(u, v)])
circuit.add_optical_layer(*[OpticalUnitary(U=H_gate, label="BS", offset=d)] * 1)


fig, ax = circuit.draw()
fig.savefig('out_example.png')

# run simulation
sim = FullUnitaryEvolution(circuit)
#print(sim.fock_basis())
#combinations_with_replacement(range(sim.N), sim.photon_number)
print(sim.N)
print(range(sim.N))
print(sim.photon_number) #Outputs 2 despite (1,2,2) term, need to make all state terms reflect it.  

from itertools import combinations_with_replacement
print(list(combinations_with_replacement(range(sim.N), sim.photon_number)))
photonic_state = sim.full_output_state()

print('Output state, photonic')
print(photonic_state)
print()

qudit_state, qudit_system = photonic_state.to_qudit_state()
print('Output state, qudit')
print(qudit_state)
print()