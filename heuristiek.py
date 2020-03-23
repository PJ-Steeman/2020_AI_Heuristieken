# Jelle Caerlen, Kwinten Vanlathem en Pieter-Jan Steeman

#TODO:  lees aantal dagen in en check of er niet buiten gereserveerd wordt
#       Seed voor random number generator

import sys
import time
import random
import copy

STUCK_VALUE = 20

class Zone:
    def __init__(self):
        self.id = None
        self.adj = None
        self.veh = []
        self.vehNeigh = []

    def setInit(self, id, adjList):
        self.id = id
        self.adj = adjList

    def setVeh(self, list):
        self.veh = list

    def setVehNeigh(self, list):
        self.vehNeigh = list

    def __str__(self):
        return self.id

class Vehicle:
    def __init__(self):
        self.id = None
        self.zone = None

    def setInit(self, line):
        self.id = line[0].rstrip("\n\r")

    def __str__(self):
        return self.id

    def setZone(self, zone):
        self.zone = zone

class Reservation:
    def __init__(self):
        self.id = None
        self.zone = None
        self.day = None
        self.start = None
        self.lenght = None
        self.vehicles = None
        self.p1 = None
        self.p2 = None

    def setInit(self, line):
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
        if(self.checkSet()):
            if(self.zone == self.assigned_veh.zone):
                return 0
            else:
                return self.p2
        return self.p1

    def checkSet(self):
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
    follower = 0
    file = open(path, "r")

    for line in file:
        if(line[0] == "+"):
            listIdent += 1
            follower = 0

            parts = line.split(": ")
            if(listIdent == 0):
                for i in range(int(parts[1])):
                    resList.append(Reservation())
            if(listIdent == 1):
                for i in range(int(parts[1])):
                    zoneList.append(Zone())
            if(listIdent == 2):
                for i in range(int(parts[1])):
                    vehList.append(Vehicle())

        else:
            if(listIdent == 0):
                resList[follower].setInit(line.split(";"))

            if(listIdent == 1):
                splitLine = line.split(";")
                splitItems = splitLine[1].split(",")
                place = "".join(splitItems)
                zones = place.split("z")[1:]
                tempList = []
                for zone in zones:
                    tempList.append(zoneList[int(zone)])

                zoneList[follower].setInit(splitLine[0], tempList)

            if(listIdent == 2):
                vehList[follower].setInit(line.split(";"))
            follower += 1

    for res in resList:
        res.zone = getItem(res.zone, zoneList)
        for id, veh in enumerate(res.vehicles):
            res.vehicles[id] = getItem(veh, vehList)

    file.close()
    return vehList, zoneList, resList

def writeFile(path, vehicles, reservations):
    file = open(path, "w")

    file.write(str(calculateCost(reservations)) + "\n")
    file.write("+Vehicle assignments\n")
    for veh in vehicles:
        file.write(str(veh).rstrip() + ";" + str(veh.zone) + "\n")
    file.write("+Assigned requests\n")
    for res in reservations:
        if(res.checkSet()):
            file.write(str(res).rstrip() + ";" + str(res.assigned_veh) + "\n")
    file.write("+Unassigned requests\n")
    for res in reservations:
        if(not res.checkSet()):
            file.write(str(res) + "\n")
    file.close()

def randomZoneAssignment(listVeh, listZone):
    for veh in listVeh:
        veh.setZone(listZone[random.randrange(0, len(listZone))])
        print(veh.zone)

def requestAssignment(listZone, listRes):
    request = listRes[random.randrange(0, len(listRes))]

    found = False

    if(len(request.zone.veh) != 0):
        random.shuffle(request.zone.veh)
        for veh in request.zone.veh:
            if(checkCarAvailable(veh, listRes, request)):
                request.setVehicle(veh)
                found = True
                break

    if(len(request.zone.vehNeigh) != 0):
        if not found:
            random.shuffle(request.zone.vehNeigh)
            for veh in request.zone.vehNeigh:
                if(checkCarAvailable(veh, listRes, request)):
                    request.setVehicle(veh)
                    break

def iteration(listZone, listRes, iteration):
    listBackup = copy.deepcopy(listRes)
    costBefore = (calculateCost(listRes))
    requestAssignment(listZone, listRes)
    costAfter = (calculateCost(listRes))

    if(costBefore < costAfter):
        return listBackup, 0

    return listRes, iteration + 1

def checkCarAvailable(veh, listRes, req):
    if (veh not in req.vehicles):
        return False
    vehRange = range(req.start, req.start + req.lenght)
    for fixed in listRes:
        if (veh == fixed.assigned_veh):
            if (req.day != fixed.day):
                continue
            fixedRange = range(fixed.start, fixed.start + fixed.lenght)
            if (len(list(set(vehRange) & set(fixedRange))) > 1):
                return False
    return True

def getVehicleInZone(zone, listVeh):
    listVehInZone = []
    for veh in listVeh:
        if(veh.zone == zone):
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

    start_time = time.time()

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

    listVeh, listZone, listRes = readFile(pathIn)

    randomZoneAssignment(listVeh, listZone)

    for zone in listZone:
        zone.setVeh(getVehicleInZone(zone, listVeh))

    for zone in listZone:
        zone.setVehNeigh(getVehicleInNeighbour(zone))

    lastCost = calculateCost(listRes)
    it = 0

    while(time.time() - start_time) < maxTime:
        # OPTIMALISATIE
        listRes, it = iteration(listZone, listRes, it)
        if(it >= STUCK_VALUE):
            print()
            print(lastCost, calculateCost(listRes))
            if(lastCost > calculateCost(listRes)):
                zoneBackup = copy.deepcopy(listZone)
                resBackup = copy.deepcopy(listRes)
                vehBackup = copy.deepcopy(listVeh)
                lastCost = calculateCost(listRes)

            randomZoneAssignment(listVeh, listZone)
            for zone in listZone:
                zone.setVeh(getVehicleInZone(zone, listVeh))
            for zone in listZone:
                zone.setVehNeigh(getVehicleInNeighbour(zone))

            for res in listRes:
                res.assigned_veh = None
            it = 0

    writeFile(pathOut, vehBackup, resBackup)

main()
