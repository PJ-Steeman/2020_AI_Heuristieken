# Jelle Caerlen, Kwinten Vanlathem en Pieter-Jan Steeman

#TODO:  lees aantal dagen in en check of er niet buiten gereserveerd wordt
#       Seed voor random number generator

import sys
import time
import random

class Zone:
    def __init__(self, line):
        self.id = line[0]
        self.adj = line[1].split(",")
        self.veh = []
        self.vehNeigh = []

    def setVeh(self, list):
        self.veh = list

    def setVehNeigh(self, list):
        self.vehNeigh = list

    def __str__(self):
        return self.id

class Vehicle:
    def __init__(self, line):
        self.id = line[0]
        self.zone = "test zone"

    def __str__(self):
        return self.id

    def setZone(self, zone):
        self.zone = str(zone)

class Reservation:
    def __init__(self, line):
        self.id = line[0]
        self.zone = line[1]
        self.day = int(line[2])
        self.start = int(line[3])
        self.lenght = int(line[4])
        self.vehicles = line[5].split(",")
        self.p1 = int(line[6])
        self.p2 = int(line[7])
        self.assigned_veh = None

    def __str__(self):
        return self.id

    def setVehicle(self, vehicle):
        self.assigned_veh = vehicle

    def calcCost(self):
        print(self.checkSet())
        print("----------")
        if(self.checkSet()):
            if(self.zone == self.assigned_veh.zone):
                return 0
            else:
                return self.p2
        return self.p1

    def checkSet(self):
        # OPGEPAST BIJ VERKEERD OUTPUT
        return self.assigned_veh is not None

def calculateCost(resList):
    cost = 0
    for res in resList:
        cost += res.calcCost()
    return cost

def readFile(path):
    resList = []
    zoneList = []
    vehList = []

    print("ok")

    listIdent = -1

    file = open(path, "r")

    for line in file:
         if(line[0] == "+"):
             listIdent += 1
         else:
            if(listIdent == 0):
                resList.append(Reservation(line.split(";")))
            if(listIdent == 1):
                zoneList.append(Zone(line.split(";")))
            if(listIdent == 2):
                vehList.append(Vehicle(line.split(";")))

    file.close()
    return vehList, zoneList, resList

def writeFile(path, vehicles, reservations):
    file = open(path, "w")

    file.write(str(calculateCost(reservations)) + "\n")
    file.write("+Vehicle assignments\n")
    for veh in vehicles:
        file.write(str(veh).rstrip() + ";" + veh.zone + "\n")
    file.write("+Assigned requests\n")
    for res in reservations:
        if(res.checkSet()):
            file.write(str(res).rstrip() + ";" + res.assigned_veh + "")
    file.write("+Unassigned requests\n")
    for res in reservations:
        if(not res.checkSet()):
            file.write(str(res) + "\n")
    file.close()

def randomZoneAssignment(listVeh, listZone):
    for veh in listVeh:
        veh.setZone("z" + str(random.randrange(0, len(listZone))))
        print(veh.zone)

# def requestAssignment(listVeh, listZone, listRes):
    # for req in listRes

# def checkCarFree():

def getVehicleInZone(zone, listVeh):
    listVehInZone = []
    for veh in listVeh:
        if(veh.zone == str(zone)):
            listVehInZone.append(veh)
    return listVehInZone

def getVehicleInNeighbour(zone):
    listVehInNeigh = []
    for zo in zone.adj:
        listVehInNeigh += zo.veh
    return listVehInNeigh

def getItem(id, list):
    for item in list:
        if(item.id == id):
            return item
    return None

def main():
    pathIn = sys.argv[1]
    pathOut = sys.argv[2]
    maxTime = int(sys.argv[3])
    if(len(sys.argv) > 4):
        random.seed(sys.argv[4])
    else:
        random.seed(None)

    print(pathIn)
    print(pathOut)
    print(maxTime)

    listVeh = []
    listZone = []
    listRes = []

    listVeh, listZone, listRes = readFile(pathIn)

    start_time = time.time()

    randomZoneAssignment(listVeh, listZone)

    for zone in listZone:
        zone.setVeh(getVehicleInZone(zone, listVeh))
    for zone in listZone:
        zone.setVehNeigh(getVehicleInNeighbour(zone))

    print(listVeh[1])

    while(time.time() - start_time) < maxTime:
        # OPTIMALISTAIE
        print("ok")

    #print(listVeh)
    #print(listZone)
    #print(listRes)

    writeFile(pathOut, listVeh, listRes)

main()
