#!/usr/bin/env python3
import random
import numpy 

## Some useful constants
Healthy = 0
Infected = 1
Infectious = 2
Quarantined = 3

## Assumptions: a person starts healthy
## Becomes infected based on p0 and on p1, and contact with someone infectious
## Then becomes infectious after serialLatency
## Some number of infectious people are then quarantined

def CountInfectious(team):
   count = 0
   for i in range(0, len(team)):
      if (team[i] == Infectious and atOffice[i]):  ## Infected and not quarantined
         count = count + 1
   return count

def CountHealthy(team):
   count = 0
   for i in range(0, len(team)):
      if (team[i] == Healthy):
         count += 1
   return count

def ListNonQuarantined(team):
   workTeam = []
   for i in range(0, len(team)):
      if (team[i] != Quarantined):
         workTeam.append(i)
   return workTeam
      

# Python program to calculate rates of infection


iterations = 100      ## Number of iterations in the simulation
days = 100            ## Number of days to simulate
teamSize = 20         ## Number of people on the whole team

p0 = 0.005            ## Probability of infection from the population at large
p1 = 0.50             ## Probability of infection from the office, from an infected co-worker

incubationTime = 5.2  ## Mean num of days before symptoms appear
incubationSigma = 4.0 ## Sigma for IT
                      ## the mean is from published studies of COVID 19.  Follows gamma (erlang distribution)

pQ = 0.98             ## Probability of quarantine after first symptoms (exponential distribution)
                      ## Estimate

serialInterval = 4.0  ## Mean num of days between infection and infecting another 
serialSigma = 3.20    ## Standard deviation for serialLatency
                      ## Both values are latest estimates from published studies.  Gamma distribution

alternatingPeriod = 2 ## number of days before switching teams

mode = 3              ## 1 = single team (everyone)
                      ## 2 = two fixed teams, periodic switching days
                      ## 3 = two fixed teams, random days
                      ## 4 = two random teams, with periodic switching


# Seed the random number generate.  If omitted, the default is a seed with millisecond timer
random.seed(1023)

# Calculate distribution parameters
# Both serial interval and incubation interval are Gamma (Erlang) distributed
thetaSerial = (serialSigma**2) / serialInterval 
alphaSerial = serialInterval/thetaSerial
betaSerial  = 1 / thetaSerial
thetaAsym = (incubationSigma**2) / incubationTime
alphaAsym = incubationTime / thetaAsym
betaAsym = 1/thetaAsym 


print("Days, Mode, Period, TeamSize, Work, Healthy")
for mode in range(1, 5):
   for alternatingPeriod in range (1, 11):
      for teamSize in range (10, 110, 10):

         # Aggregate Statistics
         numHealthy = 0;
         personDays = 0

         for i in range(0, iterations):

            # Initialize everything

            team = [0] * teamSize
            dayInfected = [0] * teamSize      # day of infection
            atOffice = [False] * teamSize     # who is the office on a given day (teams)
            infectedInterval = [0] * teamSize # For an individual, how many days between infection and being infectious
            asymptomInterval = [0] * teamSize # For an individual, how many days before symptoms appear

            # Initialize who is at work
            if (mode == 1):
               atOffice = [True] * teamSize   # Everyone at the office 
            elif (mode == 2 or mode == 3):
               for j in range(0, int(len(team)/2)):
                  atOffice[j] = True          # teamA is at work on day 0

            ## Simulate each work day
            for d in range(0, days):

               # Determine which people are at work
               # Time to switch teams!
               if (d % alternatingPeriod == 0):  
                  # Fixed teams, periodic days
                  if (mode == 2):
                     for j in range (0, len(team)):
                        atOffice[j] = not atOffice[j]

                  # Fixed teams, random days
                  elif (mode == 3):
                     # Swap teams based on a coin flip
                     if (random.random() > 0.5):  
                        for j in range (0, len(team)):
                           atOffice[j] = not atOffice[j]

                  # Random teams, random days
                  elif (mode == 4):
                     atOffice = [False] * teamSize
                     nonQuarantined = ListNonQuarantined(team)
                     teamList = random.sample(nonQuarantined, int(len(nonQuarantined)/2))
                     for i in teamList:
                        atOffice[i] = True

               # Update intervals
               for j in range(0, len(team)):
                  if (infectedInterval[j] > 0):
                     infectedInterval[j] -= 1 
                  if (asymptomInterval[j] > 0):
                     asymptomInterval[j] -= 1

               # Transtions from Healthy to Infected
               numInfected = CountInfectious(team)
               for j in range (0, len(team)):
                     if (team[j] == Healthy):
                        if (random.random() < p0):  ## New external infection
                           team[j] = Infected
                           infectedInterval[j] = int(round(numpy.random.gamma(alphaSerial, 1/betaSerial)))
                           asymptomInterval[j] = int(round(numpy.random.gamma(alphaAsym, 1/betaAsym)))
                        elif (atOffice[j]):         ## Infection at work!
                           for k in range (0, numInfected):
                              if (random.random() < p1):
                                 team[j] = Infected
                                 infectedInterval[j] = int(round(numpy.random.gamma(alphaSerial, 1/betaSerial)))
                                 asymptomInterval[j] = int(round(numpy.random.gamma(alphaAsym, 1/betaAsym)))

               # Transition from Infected to Infectious
               for j in range(0, len(team)):
                  if (team[j] == Infected and infectedInterval[j] == 0):
                     team[j] = Infectious
               
               # Transition from Infected/Infectious to Quarantined
               for j in range(0, len(team)):
                  if ((team[j] == Infected or team[j] == Infectious) and
                      (asymptomInterval[j]==0) and
                      (random.random() > (1.0-pQ))):
                      team[j] = Quarantined

               #print(team)
               #print(atOffice)
               #print("PersonDays: ", personDays)

               for j in range(0, len(team)):
                  if ((team[j] == Healthy or team[j] == Infected) and atOffice[j]):
                     personDays += 1

            for j in range(0, len(team)):      
               if (team[j] == Healthy):
                  numHealthy += 1
                  
         print(days,", ", mode,", ", alternatingPeriod, ", ", teamSize, ", ", (personDays/iterations)/(teamSize*days), ", ", (numHealthy/iterations)/teamSize)
         
