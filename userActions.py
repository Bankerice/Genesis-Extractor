import re
import datetime
import extractor
import course
import assignment

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
        tempMP = self.mp
        # # val = False
        # # while (val==0):
        # #     try:
        # tempMP = int(input("Choose MP: "))
        # val = True
        #     # except ValueError:
        #     #     val = False
        self.mp = tempMP
        extractor.mp = mp
        
        extractor.restart()
        
        # Get courses data
        courseList = extractor.getCourseList()

        for i in range(len(courseList)):
            self.courses.append(courseList[i])


    # Returns the overall course grade as of a date entered by the user
    def getCourseGradeOnDay(self,i,day,month,year,mp):
        # Store complete (original) list of assignments
        originalAssign = [] 
        for x in range(len(self.courses[i].assignments)):
            originalAssign.append(self.courses[i].assignments[x])

        # Consider only assignments in that marking period
        d1 = extractor.mpStartDates[mp][0]
        m1 = extractor.mpStartDates[mp][1]
        y1 = extractor.mpStartDates[mp][2]

        # Create array of only assignments posted before inputted date
        tempAssign = []
        for x in range(len(self.courses[i].assignments)):
            d = self.courses[i].assignments[x].datetimePosted
            #print(str(d.month)+"\t"+str(d.day) + "\t" + str(d.year))
            # if ((d.year<y1) | ((d.year == y1) & ((d.month < m1) | ((d.month == m1) & (d.day <= d1))))): # only during that MP
            if ((d.year<year) | ((d.year == year) & ((d.month < month) | ((d.month == month) & (d.day <= day))))): # before/on inputted date
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
            grade = self.getCourseGradeOnDay(i,date.day,date.month,date.year,self.mp)
            arr1 = [date,grade]
            arr.append(arr1)
        arr.pop(0)

        # for x in range(len(arr)):
        #     print(str(arr[x][0])+"\t"+str(arr[x][1]))

            
        return arr
            
    def setMP(self, mp):
        extractor.mp = mp
        
    def outputData(self, i, arr, first): # Output course data as a text file
        try:
            # Create new file for output
            outFile = open("dataOutput2.txt","x")
        except FileExistsError:
            # Edit existing file
            outFile = open("dataOutput2.txt","a")
        
        # Print data to file
        # for i in range(len(self.courses)):

        if (first):
            # Print general course information
            outFile.write("Period "+str(self.courses[i].period)+": "+str(self.courses[i].courseName)+"\n")
            outFile.write(str(self.courses[i].teacherName)+"\n")
        
        # Print date-grade array
        #arr = self.getDailyCourseGrades(i,self.d1,self.m1,self.y1,self.d2,self.m2,self.y2)
        for a in range(len(arr)):
            outFile.write(str(arr[a][0]) + "\t\t" + str(arr[a][1]) + "\n")
        
        outFile.close()
        
    