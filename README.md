# feedme
Python app which places creatures in a virtual environment populated with food. Creatures search for food using neural network brains, making decisions based on environmental inputs. The most successful are algorithmically selected for ‘breeding.’ Over many generations, the gene pool becomes populated with highly efficient creatures that hunt food with great speed and accuracy.

Run feedme.py to start the simulation. 

![Alt text](Screen Shot 2019-01-08 at 5.01.46 PM.png?raw=true "Title")

With each iteration of the simulation, creatures have a limited amount of time to eat as much food as they can. Throughout the simulation, they accumulate fitness scores based on the amount of food consumed. After each simulation run, the creatures are used to create the next generation, with a bias towards the most fit creatures.

The creatures are selected using a genetic algorithm. A pool of creatures is created, and a number of each creature is added to the pool. The most fit creature appears the most, and the least fit creature appears the least. Two parent creatures are then selected at random from the pool, and the "genes" (weights and biases of the neural network) are mixed. The resulting "child" is part of the next generation.

Pygame was used to create a simple GUI for visuals, as well as for collision detection between creatures and food.
