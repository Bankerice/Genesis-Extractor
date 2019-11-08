import datetime
import assignment

class Course():
    courseName = ""         # title of course
    teacherName = ""        # name of teacher
    period = "A"            # block period
    currentMPGrade = 0.0    # grade during current marking period as of current date
    
    # Array representing all assignments with corresponding dates
    assignments = list(map(assignment,[]))

    # Course constructor
    def __init__(self, name, teacher, period):
        courseName = name
        teacherName = teacher
        period = period

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
        self.currentMPGrade = total / self.assignments.__len__()
        