import enum
import datetime
import assignment

class Course():
    Category = enum.Enum("Category",[]) # Category enum created to represent weighting of assignment

    code = ""               # course code
    section = ""            # course section
    courseName = ""         # title of course
    teacherName = ""        # name of teacher
    period = "A"            # block period
    currentMPGrade = 0.0    # grade during current marking period as of current date
    categories = []
    weights = []
    totalPointsWorth = 0
    semesters = 0           # 0 for full year, otherwise 1 for S1 only, 2 for S2 only
    
    # Array representing all assignments with corresponding dates
    assignments = [] #list(map(assignment.Assignment,[]))

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
        self.semesters = FYSEM

    # Set categories
    def setCategories(self,cats,weighs):
        self.categories = []
        self.weights = []

        for c in range(len(cats)):
            self.categories.append(cats[c])
            self.weights.append(float(weighs[c])/100.0)
        
        if (len(self.categories)<=0):
            self.categories.append("TotalPoints")
            self.weights.append(1.0)

        self.Category = enum.Enum("Category",self.categories)
        

    # Add an assignment to this course
    def addAssignment (self,name, ptsWorth, ptsReceived, category, date):
        infoArray = []
        infoArray.append(ptsWorth)
        infoArray.append(ptsReceived)
        for i in range(1,len(self.Category)+1):
            if(category.__contains__(str(self.Category(i).name)) or str(self.Category(i).name).__contains__("TotalPoints")):
                infoArray.append(self.Category(i))
                
        infoArray.append(date)
        infoArray.append(self)

        newAssignment = assignment.Assignment(name,infoArray)
        self.assignments.append(newAssignment)
        
        self.calculateCurrentMPGrade()

    # Get sum of points received for every assignment in this course (in this MP)
    def getTotalPointsRec (self) -> int:
        sum = 0
        for i in range(len(self.assignments)):
            sum += self.assignments[i].numPointsReceived
        return sum
    
    # Get sum of points worth for every assignment in this course (in this MP)
    def getTotalPointsWorth (self) -> int:
        sum = 0
        for i in range(len(self.assignments)):
            sum += self.assignments[i].numTotalPointsWorth
        return sum

    # Calculate the current marking period grade for this course with weighting ---- WORKS!!! YAY!!!
    def calculateCurrentMPGrade (self):
        total = 0
        totalR = [] # total points received per category
        totalW = []
        for i in range(len(self.Category)):
            totalR.append(0.0)
            totalW.append(0.0)
         
        weights = self.weights.copy()
        
        self.totalPointsWorth = 0
        for i in range(len(self.assignments)):
            if (self.assignments[i].gradePercent >= 0):
                self.totalPointsWorth += self.assignments[i].numTotalPointsWorth
                totalR[self.assignments[i].category.value-1] += float(self.assignments[i].numPointsReceived)
                totalW[self.assignments[i].category.value-1] += float(self.assignments[i].numTotalPointsWorth)
                
            if ((self.assignments[i].numTotalPointsWorth == 0) & (self.assignments[i].numPointsReceived > 0)):
                totalR[self.assignments[i].category.value-1] += float(self.assignments[i].numPointsReceived)
        # print("TOTAL POINTS WORTH: " + str(self.totalPointsWorth))

        weightSum = 0
        for i in range(len(self.Category)):
            if (totalW[i]>0):
                weightSum += weights[i]
                total += weights[i] * (totalR[i]/totalW[i])
        
        if (weightSum==0):
            self.currentMPGrade = 0
        else:
            self.currentMPGrade = total / weightSum
        
                