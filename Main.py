from LearningSystems.GPLearnSystem import GPLearnSystem
from Trainer import Trainer


func_set = ['add', 'mul', 'sub', 'div', 'exp', 'sqrt', 'sin', 'cos', 'tan']

trainer = Trainer(path="data//", save=True, load=True, noise_range=(-0.025, 0.025), master_file="OtherEquations.csv")
gp = GPLearnSystem(func_set=func_set)
print(trainer.predict_equations(gp, no_samples=10, eqs=None, input_range=(-200, 200)))
