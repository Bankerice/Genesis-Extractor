
import course
import datetime
import enum


# Assignment class represents an assignment with name, grade, category, date posted, and corresponding course (object)
class Assignment:
    courseFrom = 0 # Course object
    assignmentName = ""
    numTotalPointsWorth = 0.0
    numPointsReceived = 0.0
    gradePercent = 0.0
    extraCredit = False
    category = 0 # Category object
    datetimePosted = datetime.datetime.today().date

    # Assignment constructor 
    def __init__(self, name, info): # info = (pointsWorth, pointsReceived, category, datetimePosted, courseFrom)
        self.assignmentName         = name
        self.numTotalPointsWorth    = info[0]
        self.numPointsReceived      = info[1]
        self.category               = info[2] 
        self.datetimePosted         = info[3]
        self.courseFrom             = info[4]

        try:
            self.gradePercent = round(((self.numPointsReceived / self.numTotalPointsWorth) * 100),2)
        except ZeroDivisionError:
            self.gradePercent = -1
            extraCredit = True
        

    def infoString(self):
        info = ""
        info = "Name:\t" + self.assignmentName + "\nGrade:\t" + str(self.numPointsReceived) + "/" + str(self.numTotalPointsWorth) + " = " + str(self.gradePercent)
        info += "\nCategory:\t" + self.category + "\nDate Posted:\t" + str(datetime.date(self.datetimePosted().year,self.datetimePosted().month,self.datetimePosted().day))
        return info

    
    