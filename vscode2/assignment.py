
import datetime
import enum

# Category enum created to represent weighting of assignment
class Category (enum.Enum):
    DistrictAssessment = 1
    MajorAssessments = 2
    MinorAssessments = 3

# Assignment class represents an assignment with name, grade, category, and date posted
class Assignment:
    assignmentName = ""
    numTotalPointsWorth = 0.0
    numPointsReceived = 0.0
    gradePercent = 0.0
    category = Category.MajorAssessments
    datetimePosted = datetime.datetime.today().date

    # Assignment constructor 
    def __init__(self, name, info): # info = (pointsWorth, pointsReceived, categoryType, datetimePosted)
        self.assignmentName         = name
        self.numTotalPointsWorth    = info[0]
        self.numPointsReceived      = info[1]
        self.category               = info[2]
        self.datetimePosted         = info[3]

        self.gradePercent = (self.numPointsReceived / self.numTotalPointsWorth) * 100

    def infoString(self):
        info = ""
        info = "Name:\t" + self.assignmentName + "\nGrade:\t" + str(self.numPointsReceived) + "/" + str(self.numTotalPointsWorth) + " = " + str(self.gradePercent)
        info += "\nCategory:\t" + self.category + "\nDate Posted:\t" + str(datetime.date(self.datetimePosted().year,self.datetimePosted().month,self.datetimePosted().day))
        return info

    
    