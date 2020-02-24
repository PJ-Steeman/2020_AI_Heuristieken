# Jelle Caerlen, Kwinten Vanlathem en Pieter-Jan Steeman

#TODO: lees aantal dagen in en check of er niet buiten gereserveerd wordt

class Zone:
    def __init__(self, line):
        self.name = line[0]
        self.adj = line[1].split(",")

class Vehicle:
    def __init__(self, line):
        self.name = line[0]

    def setZone(self, zone):
        self.zone = zone

class Reservation:
    def __init__(self, line):
        self.id = line[0]
        self.zone = line[1]
        self.day = line[2]
        self.start = line[3]
        self.lenght = line[4]
        self.vehicles = line[5].split(",")
        self.p1 = line[6]
        self.p2 = line[7]

    def setVehicle(self, vehicle):
        self.assigned_veh = vehicle

    def calcCost(self):
        if(checkSet):
            if(self.zone == self.assigned_veh.zone):
                return 0
            else:
                return p2
        return p1

    def checkSet(self):
        # OPGEPAST BIJ VERKEERD OUTPUT
        return self.assigned_veh is not None

def calculateCost(self, resList):
    cost = 0
    for res in resList:
        cost += res.calcCost()
    return cost

def readFile(self, path):
    reslist = []
    zoneList = []
    vehList = []

    listIdent = -1

    file = open(path, "r")

    for line in file:
         if(line[0] == "+"):
             listIdent += 1
         else:
            if(listIdent == 0):
                reslist.append(Reservation(line.split(";")))
            if(listIdent == 1):
                zonelist.append(Zone(line.split(";")))
            if(listIdent == 2):
                vehlist.append(Vehicle(line.split(";")))

    file.close()
    return resList, zoneList, vehList

def main():
    path = "bleh.csv"
    listVeh = []
    listZone = []
    listRes = []

    listVeh, listZone, listRes = readFile(path)
