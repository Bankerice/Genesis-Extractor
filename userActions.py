import re
import datetime
import extractor
import course
import assignment
import date

class UserActions():
    mp = 1
    courses = []
    studentID = ""
    studentName = ""
    d1 = m1 = y1 = d2 = m2 = y2 = 0
    
    numDaysInMonth = {31,30,31,30,31,30,31,31,30,31,30,31}

    def __init__(self,name,ID,mp):
        self.studentName = name
        self.studentID = ID

        # Set MP
        self.mp = mp
        self.courses = []
        extractor.mp = mp
        extractor.courses = []
        extractor.restart(mp)

        self.courses = []
        self.getData()

    def getData(self):
        self.courses = []
        # Get courses data
        courseList = extractor.getCourseList()

        for i in range(len(courseList)):
            self.courses.append(courseList[i])

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
            #print(str(d.month)+"\t"+str(d.day) + "\t" + str(d.year))
            # print(str(d.toString()) + "\t" + str(mpStartDate.toString()))
            if ((d.date.year<year) | ((d.date.year == year) & ((d.date.month < month) | ((d.date.month == month) & (d.date.day <= day))))): # before/on inputted date
                # if ((d.date.year>y1) | ((d.date.year == y1) & ((d.date.month > m1) | ((d.date.month == m1) & (d.date.day <= d1))))): # before/on inputted date
            # If MP start date is before or the same as assignment date posted
            # if (mpStartDate.compareToDateObj(d)<=0):
                tempAssign.append(self.courses[i].assignments[x])
            # print(self.courses[i].assignments[x].assignmentName)
                # print(self.courses[i].assignments[x])
                    
        # Get course grade as of the entered date
        # print(tempAssign)
        extractor.courses[i].assignments = tempAssign
        extractor.courses[i].calculateCurrentMPGrade()
        grade = round(extractor.courses[i].currentMPGrade,2)
        # print("TPW: " + str(extractor.courses[i].totalPointsWorth))
        numPtsRec = extractor.courses[i].getTotalPointsRec()
        numPtsWorth = extractor.courses[i].getTotalPointsWorth()
        retArr = [grade,numPtsRec,numPtsWorth]
        # print(retArr[2])

        # Restore course assignments list to original 
        extractor.courses[i].assignments = originalAssign
        return retArr
            
    
    # Returns array of course grades as of every day in an interval entered by the user
    def getDailyCourseGrades(self,i,d1,m1,y1,d2,m2,y2): # returns [date, grade]
        self.d1 = d1
        self.m1 = m1
        self.y1 = y1 
        self.d2 = d2
        self.m2 = m2
        self.y2 = y2
        
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
            grade = self.getCourseStatsOnDay(i,date.day,date.month,date.year,self.mp)
            arr1 = [date,grade[0],grade[1],grade[2]]
            arr.append(arr1)
        arr.pop(0)

        # for x in range(len(arr)):
        #     print(str(arr[x][0])+"\t"+str(arr[x][1]))

            
        return arr
            
    def setMP(self, mp):
        self.mp = mp
        extractor.mp = mp
        # extractor.restart(mp)
        self.getData()

    def clear(self):
        self.courses = []
    # def outputData(self, i, arr, first): # Output course data as a text file
    #     try:
    #         # Create new file for output
    #         outFile = open("dataOutput2.txt","x")
    #     except FileExistsError:
    #         # Edit existing file
    #         outFile = open("dataOutput2.txt","a")
        
    #     # Print data to file
    #     # for i in range(len(self.courses)):

    #     if (first):
    #         # Print general course information
    #         outFile.write("Period "+str(self.courses[i].period)+": "+str(self.courses[i].courseName)+"\n")
    #         outFile.write(str(self.courses[i].teacherName)+"\n")
        
    #     # Print date-grade array
    #     #arr = self.getDailyCourseGrades(i,self.d1,self.m1,self.y1,self.d2,self.m2,self.y2)
    #     for a in range(len(arr)):
    #         outFile.write(str(arr[a][0]) + "\t\t" + str(arr[a][1]) + "\n")
        
    #     outFile.close()
        
    