import re
import datetime
import extractor2021 as extractor
import course
import assignment
import date

class DataManager():
    mp = 1
    courses = [] #list(map(course.Course,[]))
    studentID = ""
    studentName = ""
    
    def __init__(self,name,ID,courses,mp):
        self.studentName = name
        self.studentID = ID
        self.mp = mp
        self.courses = []

        for i in range(len(courses)):
            self.courses.append(courses[i])

    # Returns the overall course grade as of a date entered by the user
    def getCourseStatsOnDay(self,i,day,month,year,mp):
        # Store complete (original) list of assignments
        originalAssign = [] 
        for x in range(len(self.courses[i].assignments)):
            originalAssign.append(self.courses[i].assignments[x])
        
        # Consider only assignments in that marking period
        d1 = extractor.mpStartDates[mp][0]
        m1 = extractor.mpStartDates[mp][1]
        y1 = extractor.mpStartDates[mp][2]
        mpStartDate = date.Date(d1,m1,y1)

        # Create array of only assignments posted before inputted date
        tempAssign = []
        
        for x in range(len(self.courses[i].assignments)):
            d = self.courses[i].assignments[x].datetimePosted
            d = date.Date(d.day,d.month,d.year)

            # If assignment date posted is before date specified in parameters
            if ((d.date.year<year) | ((d.date.year == year) & ((d.date.month < month) | ((d.date.month == month) & (d.date.day <= day))))):
            # if (mpStartDate.compareToDateObj(d)<=0):
                tempAssign.append(self.courses[i].assignments[x])
                                    
        # Get course grade as of the entered date
        self.courses[i].assignments = tempAssign
        self.courses[i].calculateCurrentMPGrade()
        grade = round(self.courses[i].currentMPGrade*100,2)
        numPtsRec = self.courses[i].getTotalPointsRec()
        numPtsWorth = self.courses[i].getTotalPointsWorth()
        retArr = [grade,numPtsRec,numPtsWorth]

        # Restore course assignments list to original 
        self.courses[i].assignments = originalAssign
        return retArr
    
    # Returns array of course grades as of every day in an interval entered by the user
    def getDailyCourseGrades(self,i,d1,m1,y1,d2,m2,y2): # returns [date, grade]
        arr = [[]]
        intervalLength = 0 # number of days in interval
        date1 = datetime.date(y1,m1,d1)
        date2 = datetime.date(y2,m2,d2)

        if ((y2>y1) | ((y2==y1)&((m2>m1)|((m2==m1)&(d2>d1))))):
            intervalLength += (date2.__sub__(date1)).days
        else:
            print("Second endpoint date must take place after the first. \nFirst date: " + str(date1) + "\tSecond Date: " + str(date2))
            return 0

        for x in range(0,intervalLength+1):
            date = date1.__add__(datetime.timedelta(x))
            grade = self.getCourseStatsOnDay(i,date.day,date.month,date.year,self.mp)
            arr1 = [date,grade[0],grade[1],grade[2]]
            arr.append(arr1)
        arr.pop(0)
        return arr
            
    # Get daily course grades assuming self.courses is accurate for exactly one MP
    def getDailyCourseGradesForMP(self,i,mp): 
        # date1 = date.Date(extractor.mpStartDates[mp-1][0],extractor.mpStartDates[mp-1][1],extractor.mpStartDates[mp-1][2])
        startDate = date.datetime.date(extractor.mpStartDates[mp][2],extractor.mpStartDates[mp][1],extractor.mpStartDates[mp][0])
        if (mp<extractor.currentMPindex):
            endDate = date.datetime.date(extractor.mpStartDates[mp+1][2],extractor.mpStartDates[mp+1][1],extractor.mpStartDates[mp+1][0]-1)
        else:
            endDate = datetime.date.today()
        return self.getDailyCourseGrades(i,startDate.day,startDate.month,startDate.year,endDate.day,endDate.month,endDate.year)

    def clear(self):
        self.courses = []
        
