# Jelle Caerlen, Kwinten Vanlathem en Pieter-Jan Steeman

import sys
import time
import multiprocessing
import os
import signal
import random
import copy
import math

MAX_ITERATIONS = 500
MAX_T = 5000
MIN_T = 15
ALPHA = 0.7

# ---------------------- Klasses ---------------------- #
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
        self.assigned_veh = None

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

# ---------------------- IO Functies ---------------------- #
def readFile(path):
    # Lege lijsten aanmaken om de objecten in te bewaren
    resList = []
    zoneList = []
    vehList = []

    listIdent = -1
    follower = 0

    file = open(path, "r")

    for line in file:
        # Bij een + karakter naar het volgende soort objecten gaan (Reservaties, Zones en Auto's)
        if(line[0] == "+"):
            listIdent += 1
            follower = 0

            parts = line.split(": ")
            # Het correcte aantal lege objecten van de bijhorende klasse aannmaken
            if(listIdent == 0):
                for i in range(int(parts[1])):
                    resList.append(Reservation())
            if(listIdent == 1):
                for i in range(int(parts[1])):
                    zoneList.append(Zone())
            if(listIdent == 2):
                for i in range(int(parts[1])):
                    vehList.append(Vehicle())

        # Als er geen + staat, de lege objecten vullen met de correcte info
        else:
            # Afhankelijk van de klasse van het object de juiste info verwerken
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

    # De id's van de objecten van string vorm omzetten naar echte objecten
    # Dit kan pas achteraf omdat men in het begin nog niet weet hoeveel objecten er van elke klasse zullen zijn
    for res in resList:
        res.zone = getItem(res.zone, zoneList)
        for id, veh in enumerate(res.vehicles):
            res.vehicles[id] = getItem(veh, vehList)

    file.close()
    return vehList, zoneList, resList

def writeFile(path, vehicles, reservations):
    file = open(path, "w")

    # Schrijf de beste cost weg
    file.write(str(calculateCost(reservations)) + "\n")

    # Schrijf alle voertuig toewizingen weg
    file.write("+Vehicle assignments\n")
    for veh in vehicles:
        file.write(str(veh).rstrip() + ";" + str(veh.zone) + "\n")

    # Schrijf alle vervulde requests weg
    file.write("+Assigned requests\n")
    for res in reservations:
        if(res.checkSet()):
            file.write(str(res).rstrip() + ";" + str(res.assigned_veh) + "\n")

    # Schrijf alle niet vervulde requests weg
    file.write("+Unassigned requests\n")
    for res in reservations:
        if(not res.checkSet()):
            file.write(str(res) + "\n")
    file.close()

# ---------------------- Hulp Functies ---------------------- #
# Geeft een lijst van de wagens in die zone terug
def getVehicleInZone(zone, listVeh):
    listVehInZone = []
    for veh in listVeh:
        if(veh.zone == zone):
            listVehInZone.append(veh)
    return listVehInZone

# Geeft een lijst van de wagens in de buurzone's terug
def getVehicleInNeighbour(zone):
    listVehInNeigh = []
    for zo in zone.adj:
        listVehInNeigh += zo.veh
    return listVehInNeigh

# Berekent de totale kost van een oplossing
def calculateCost(resList):
    cost = 0
    for res in resList:
        cost += res.calcCost()
    return cost

# Controleert of een wagen op dat een bepaald tijdstip en in die zone vrij is
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

# Zet string id's om naar hun corresponderende objecten
def getItem(id, list):
    for item in list:
        if(item.id == id):
            return item
    return None
# ---------------------- Toewijzings Functies ---------------------- #
# Geeft aan alle auto's in de randomAssigList een random zone en past de auto lijsten in de zone en zijn buren aan
def randomAssignment(listZone, listRes, listVeh, randomAssigList = None):
    if(randomAssigList == None):
        randomAssigList = listVeh

    for veh in randomAssigList:
        veh.setZone(listZone[random.randrange(0, len(listZone))])
        # print(str(veh) + " staat in zone " + str(veh.zone))

    for zone in listZone:
        zone.setVeh(getVehicleInZone(zone, listVeh))

    for zone in listZone:
        zone.setVehNeigh(getVehicleInNeighbour(zone))

    return listZone, listRes, listVeh

# Vervult zo veel mogelijk request
def requestFiller(listZone, listRes):
    # Bepaal een random volgorde om de requests te vervullen
    shuffeledList = list(range(len(listRes)))
    random.shuffle(shuffeledList)

    for r_id in shuffeledList:
        # Vervul enkel nog niet geassignde requets
        if listRes[r_id].assigned_veh == None:
            found = False

            # Kijk eerst of er nog een auto binnen de zone vrij is
            if(len(listRes[r_id].zone.veh) != 0):
                random.shuffle(listRes[r_id].zone.veh)
                for veh in listRes[r_id].zone.veh:
                    if(checkCarAvailable(veh, listRes, listRes[r_id])):
                        listRes[r_id].setVehicle(veh)
                        found = True
                        break

            # Kijk of er een auto bij een van de buren vrij is
            if(len(listRes[r_id].zone.vehNeigh) != 0):
                if not found:
                    random.shuffle(listRes[r_id].zone.vehNeigh)
                    for veh in listRes[r_id].zone.vehNeigh:
                        if(checkCarAvailable(veh, listRes, listRes[r_id])):
                            listRes[r_id].setVehicle(veh)
                            break

    return listZone, listRes

# ---------------------- Random Functies ---------------------- #
def randomChange(listRes, listZone, listVeh):
    i = random.randrange(4)
    if (i < 2):
        # Unassign een request
        listZone, listRes = requestUnassignment(listZone, listRes)
        listZone, listRes = requestFiller(listZone, listRes)
    return True, listRes, listZone, listVeh
    # if (i >= 2):
    #     # Assign wagen aan andere zone
    #     listZone, listRes, listVeh = zoneReassignment(listZone, listRes, listVeh)
    #     listZone, listRes = requestFiller(listZone, listRes)
    #     return True, listRes, listZone, listVeh

def zoneReassignment(listZone, listRes, listVeh):
    veh = listVeh[random.randrange(0, len(listVeh))]
    listZone, listRes, listVeh = randomAssignment(listZone, listRes, listVeh, [veh])

    for res in listRes:
        if str(res.assigned_veh) == str(veh):
            res.setVehicle(None)

    return listZone, listRes, listVeh

def requestUnassignment(listZone, listRes):
    request = listRes[random.randrange(0, len(listRes))]
    request.setVehicle(None)
    return listZone, listRes

# ---------------------- SOLVER ---------------------- #
def solver(queue: multiprocessing.Queue, listZone, listRes, listVeh):

    total_best_cost = None
    total_best_zone = None
    total_best_res = None
    total_best_veh = None

    stop = False

    while not stop:
        # Maak een initiële oplossing (volledig random)
        listZone, listRes, listVeh = randomAssignment(listZone, listRes, listVeh)

        best_cost = calculateCost(listRes)

        # Backups maken waar uiteindelijk de best oplossing in zal komen
        zoneBackup = copy.deepcopy(listZone)
        resBackup = copy.deepcopy(listRes)
        vehBackup = copy.deepcopy(listVeh)

        T = MAX_T

        # initiële random toewijzing van requests
        listZone, listRes = requestFiller(listZone, listRes)

        try:
            # Simulated annealing
            while T >= MIN_T:
                for it in range(MAX_ITERATIONS):
                    # Voer een verandering uit
                    changeWorked, listRes, listZone, listVeh = randomChange(listRes, listZone, listVeh)
                    if(changeWorked):
                        current_cost = calculateCost(listRes)
                        dE = current_cost - best_cost

                        # Als de nieuwe oplossing beter is of gelukt heeft werken we er op verder
                        if (dE <= 0) or (math.exp((-dE)/T) > random.random()):
                            best_cost = current_cost
                            zoneBackup = copy.deepcopy(listZone)
                            resBackup = copy.deepcopy(listRes)
                            vehBackup = copy.deepcopy(listVeh)

                        # Als er geen verbetering is en de oplossing heeft geen geluk, zullen we verdergaan van onze laatster beste oplossing
                        else:
                            listZone = copy.deepcopy(zoneBackup)
                            listRes = copy.deepcopy(resBackup)
                            listVeh = copy.deepcopy(vehBackup)

                T = ALPHA * T

        except (KeyboardInterrupt, TimeoutError):
            stop = True

        print(best_cost)

        if (total_best_cost is None or best_cost < total_best_cost):
            print("verbetering van " + str(total_best_cost) + " naar " + str(best_cost))
            total_best_cost = best_cost
            total_best_res = copy.deepcopy(listRes)
            total_best_zone = copy.deepcopy(listZone)
            total_best_veh = copy.deepcopy(listVeh)

            queue.put((total_best_cost, total_best_res, total_best_zone, total_best_veh))

# ---------------------- MAIN ---------------------- #
def main():
    # Start de timer
    start_time = time.time()

    # Verwerking van de argumenten
    pathIn = sys.argv[1]
    pathOut = sys.argv[2]
    max_time = int(sys.argv[3])

    # Als er een seed wordt meegegeven, gebruik hem. Anders wordt een random seed gebruikt
    if(len(sys.argv) > 4):
        random.seed(sys.argv[4])
    else:
        random.seed(None)

    if(len(sys.argv) == 6):
        max_thread = int(sys.argv[5])
    else:
        max_thread = 1

    print("Input file: " + pathIn + "   -----   Output file: " + pathOut + "   -----   Maximum runtime: " + str(max_time) + "   -----   Aantal threads: " + str(max_thread))

    # Het inlezen van de inpufile en in een lijst van objecten zetten
    listVeh, listZone, listRes = readFile(pathIn)

    read_time = time.time() - start_time
    print("Tijd gebruikt om file in te lezen: " + str(read_time) + " sec.")

    # Maak een queue voode communicatie met de main en maak de verschillende threads
    queue = multiprocessing.Queue()
    threads = [multiprocessing.Process(target = solver, args=(queue, listZone, listRes, listVeh)) for i in range (max_thread)]

    for t in threads:
        t.start()

    # Kill de threads iets voor de tijd verlopen is
    sleep_time = max_time - 4 * read_time

    if(sleep_time < 0):
        sleep_time = 60*60

    try:
        time.sleep(sleep_time)
    except (KeyboardInterrupt, TimeoutError):
        pass

    for t in threads:
        os.kill(t.pid, signal.SIGINT)

    # Haal alle oplossingen op
    solutions = [queue.get() for _ in threads]

    for s in solutions:
        print(s[0])

    # Bepaal de beste oplossing en output deze
    best_cost, best_listRes, best_listZone, best_listVeh = min(solutions, key=lambda x: x[0])

    print(best_cost)
    writeFile(pathOut, best_listVeh, best_listRes)

if __name__ == '__main__':
    main()
