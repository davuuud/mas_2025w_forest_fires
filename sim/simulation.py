from visual import VisualizerFactory

class Simulation:
    def __init__(self, config):
        self.config = config
        self.visualizers = VisualizerFactory.get_visualizers(self.config)
        self.state = self.config.preset.generate()
        print(self.state)

    def run(self, steps=1):
        #pass intial frame to visualizer
        for v in self.visualizers:
            v.write_frame(self.state)

        for step in range(steps):
            #calculate neighborhood
            nbs = self.config.neighborhood.calculate(self.state,self.config.width,self.config.height)

            #apply rules
            for rule in self.config.rules:
                self.state = rule.calculate(self.state,nbs)
            
            #pass frame to visualizer
            for v in self.visualizers:
                v.write_frame(self.state)
            print(f"##### step {step}: #####")
            print(self.state)


