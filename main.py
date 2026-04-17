from CircuitCalculator.Circuit.circuit import Circuit
import CircuitCalculator.Circuit.Components.components as ccp
from CircuitCalculator.Circuit.solution import dc_solution

# Define the circuit
circuit = Circuit([
    ccp.dc_voltage_source(V=1, id='Vs', nodes=('1', '0')),
    ccp.resistor(R=1, id='R', nodes=('1', '0'))
])

# Solve the circuit
solution = dc_solution(circuit)
print("Test 1:")
print(type(solution.solution), repr(solution.solution))
print("Test 2:")
print(dir(solution.solution)[:50])

print(f'I(R)={solution.get_current("R"):2.2f}A')
print(f'V(R)={solution.get_voltage("R"):2.2f}V')