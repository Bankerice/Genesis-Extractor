import datetime
import assignment

class Course():
    courseName = ""         # title of course
    teacherName = ""        # name of teacher
    period = "A"            # block period
    currentMPGrade = 0.0    # grade during current marking period as of current date
    categories = [0.10,0.45,0.45]
    numInEachCategory = [0,0,0]
    totalAssignedWeights = 0
    bool fullSemester = True

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
    def __init__(self, name, teacher, period, fullSem):
        self.courseName = name
        self.teacherName = teacher
        self.period = period
        self.fullSemester = fullSem

    # Add an assignment to this course
    def addAssignment (self,name, ptsWorth, ptsReceived, category, date):
        infoArray = []
        infoArray.append(ptsWorth)
        infoArray.append(ptsReceived)
        infoArray.append(category)
        infoArray.append(date)
        newAssignment = assignment.Assignment(name,infoArray)
        self.assignments.append(newAssignment)
        
        total = 0
        for i in range(0,self.assignments.__len__()):
            total += self.assignments[i].gradePercent

        self.currentMPGrade = total / len(self.assignments)
        
    
# course1 = Course("Name","Teacher","A",True)
# course1.addAssignment("a",10,8,assignment.Category.MajorAssessment,datetime.datetime.today().date)
# course1.addAssignment("b",10,10,assignment.Category.MajorAssessment,datetime.datetime.today().date)
# print(course1.assignments[0].gradePercent)
# print(course1.assignments[1].gradePercent)
# print(course1.currentMPGrade)