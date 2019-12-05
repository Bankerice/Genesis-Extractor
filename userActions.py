import re
import datetime
import extractor
import course
import assignment

class UserActions():
    courses = []
    studentID = ""
    studentName = ""
    
    numDaysInMonth = {31,30,31,30,31,30,31,31,30,31,30,31}

    def __init__(self,name,ID,courseList):
        self.studentName = name
        self.studentID = ID
        for i in range(len(courseList)):
            self.courses.append(courseList[i])


    # Returns the overall course grade as of a date entered by the user
    def getCourseGradeOnDay(self,i,day,month,year):
        # Store complete (original) list of assignments
        originalAssign = [] 
        for x in range(len(self.courses[i].assignments)):
            originalAssign.append(self.courses[i].assignments[x])

        # Create array of only assignments posted before inputted date
        tempAssign = []
        for x in range(len(self.courses[i].assignments)):
            d = self.courses[i].assignments[x].datetimePosted
            #print(str(d.month)+"\t"+str(d.day) + "\t" + str(d.year))
            if ((d.year<year) | ((d.year == year) & ((d.month < month) | ((d.month == month) & (d.day < day))))):
                tempAssign.append(self.courses[i].assignments[x])
                    
        # Get course grade as of the entered date
        self.courses[i].assignments = tempAssign
        self.courses[i].calculateCurrentMPGrade()
        grade = self.courses[i].currentMPGrade

        # Restore course assignments list to original 
        self.courses[i].assignments = originalAssign
        return grade
            
    
    # Returns array of course grades as of every day in an interval entered by the user
    def getDailyCourseGrades(self,i,d1,m1,y1,d2,m2,y2): # returns [date, grade]
        arr = [[]]
        intervalLength = 0 # number of days in interval
        date1 = datetime.date(y1,m1,d1)
        date2 = datetime.date(y2,m2,d2)

        if ((y2>y1) | ((y2==y1)&((m2>m1)|((m2==m1)&(d2>d1))))):
            intervalLength += (date2.__sub__(date1)).days
        else:
            print("Second endpoint date must take place after the first")
            return 0


        for x in range(0,intervalLength+1):
            date = date1.__add__(datetime.timedelta(x))
            grade = self.getCourseGradeOnDay(i,date.day,date.month,date.year)
            arr1 = [date,grade]
            arr.append(arr1)
            
        return arr
            
        
        
        
        
    