from visual import Visualizer, PPM
import numpy as np

class Simulation:
    
    def __init__(self, config, visualizer: Visualizer = PPM()):
        self.config = config
        self.visualizer = visualizer
        self.state = self.config.preset.generate()
        print(self.state)

    def run(self, steps=1):
        #pass intial frame to visualizer
        #self.visualizer.frame(self.state)

        for step in range(steps):
            #calculate neighborhood
            nbs = self.config.neighborhood.calculate(self.state,self.config.width,self.config.height)

            #apply rules
            for rule in self.config.rules:
                self.state = rule.calculate(self.state,nbs)
            
            #pass frame to visualizer
            #self.visualizer.frame(self.state)
            print(f"##### step {step}: #####")
            print(self.state)


