import datetime
import assignment

class Course():
    code = ""               # course code
    section = ""            # course section
    courseName = ""         # title of course
    teacherName = ""        # name of teacher
    period = "A"            # block period
    currentMPGrade = 0.0    # grade during current marking period as of current date
    categories = [0.10,0.45,0.45]
    numInEachCategory = [0,0,0]
    totalAssignedWeights = 0
    fullYear = True

    # Array representing all assignments with corresponding dates
    assignments = list(map(assignment.Assignment,[]))

    # Array representing database of grades as of each day in the year
    months = []
    for i in range (0,10):
        dailyGrades = []
        for j in range (1,31 if i%2==0 else 32):
            dailyGrades.append(100)
        months.append(dailyGrades)

    # Course constructor
    def __init__(self, name, teacher, period, FYSEM):
        self.courseName = name
        self.teacherName = teacher
        self.period = period
        self.fullYear = FYSEM

    # Add an assignment to this course
    def addAssignment (self,name, ptsWorth, ptsReceived, category, date):
        infoArray = []
        infoArray.append(ptsWorth)
        infoArray.append(ptsReceived)
        infoArray.append(category)
        infoArray.append(date)
        newAssignment = assignment.Assignment(name,infoArray)
        self.assignments.append(newAssignment)
        
        self.calculateCurrentMPGrade()

    # Calculate the current marking period grade for this course ---- Super inefficient and weighting calculations are off
    def calculateCurrentMPGrade (self):
        total = 0
        totalR = [0.0,0.0,0.0]
        totalW = [0.0,0.0,0.0]
        weight = [0.5,0.4,0.1]
        weights = [0.0,0.0,0.0]
        
        for i in range(len(self.assignments)):
            if (self.assignments[i].gradePercent >= 0):
                totalR[self.assignments[i].category.value-1] += float(self.assignments[i].numPointsReceived)
                weights[self.assignments[i].category.value-1] = weight[self.assignments[i].category.value-1]
                totalW[self.assignments[i].category.value-1] += float(self.assignments[i].numTotalPointsWorth)
                
            if ((self.assignments[i].numTotalPointsWorth == 0) & (self.assignments[i].numPointsReceived > 0)):
                totalR[self.assignments[i].category.value-1] += float(self.assignments[i].numPointsReceived)
        
        for i in range(0,3):
            if (totalW[i]>0):
                total += weights[i] * (totalR[i]/totalW[i])
        
        weightSum = weights[0]+weights[1]+weights[2]
        if (weightSum==0):
            self.currentMPGrade = 0
        else:
            self.currentMPGrade = total / (weights[0]+weights[1]+weights[2])
        
                