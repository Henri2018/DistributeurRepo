#!/usr/bin/python3
import statistics
from hx711 import HX711


class Scale:
    def __init__(self, source=None, samples=20, spikes=4, sleep=0.1):

        self.source = source or [HX711()]
        self.samples = samples
        self.spikes = spikes
        self.sleep = sleep
        self.history = []

    def newMeasure(self):
        value=0
        for sensor in self.source:
            value += sensor.getWeight()
        self.history.append(value)

    def getMeasure(self):
        """Useful for continuous measurements."""
        self.newMeasure()
        # cut to old values
        self.history = self.history[-self.samples:]

        avg = statistics.mean(self.history)
        deltas = sorted([abs(i-avg) for i in self.history])

        if len(deltas) < self.spikes:
            max_permitted_delta = deltas[-1]
        else:
            max_permitted_delta = deltas[-self.spikes]

        valid_values = [val for val in self.history if (abs(val - avg) <= max_permitted_delta)]

        avg = statistics.mean(valid_values)

        return avg

    def getWeight(self, samples=None):
        """Get weight for once in a while. It clears history first."""
        self.history = []
        
        for i in range(samples or self.samples):
            self.newMeasure()

        return self.getMeasure()

    def tare(self, times=25):
        for sensor in self.source:
            sensor.tare(times)

    def calculateReferenceUnitScale(self,masse=1,samples=20,tareBefore=False):
        if tareBefore:
            self.tare()

        reference_unit=[]
        for sensor in self.source:
            reference_unit.append(self.source.REFERENCE_UNIT)
            self.source.REFERENCE_UNIT=1
        
        offset=self.getWeight(samples)
        
        return offset/masse
        
    def setOffset(self, offset):
        for sensor in self.source:
            sensor.setOffset(offset)

    def setReferenceUnit(self, reference_unit):
        try:
            for i in range(len(self.source)):
                self.source[i].setReferenceUnit(reference_unit[i])
        except IndexError:
            print("Il n'y a pas assez de reference de fourni : {} attendus".format(len(self.source)))
            if type(reference_unit)==list:
                for i in range(len(self.source)):
                    self.source[i].setReferenceUnit(reference_unit[0])
            else:
                self.source[i].setReferenceUnit(reference_unit)

    def powerDown(self):
        for sensor in self.source:
            sensor.powerDown()

    def powerUp(self):
        for sensor in self.source:
            sensor.powerUp()

    def reset(self):
        for sensor in self.source:
            sensor.reset()
