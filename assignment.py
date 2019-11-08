
import datetime
import enum

# Category enum created to represent weighting of assignment
class Category (enum.Enum):
    DistrictAssessment = 10
    MajorAssessment = 45
    MinorAssessment = 45

# Assignment class represents an assignment with name, grade, category, and date posted
class Assignment:
    assignmentName = ""
    numTotalPointsWorth = 0.0
    numPointsReceived = 0.0
    gradePercent = 0.0
    category = Category.MajorAssessment
    datetimePosted = datetime.datetime.today()

    # Assignment constructor 
    def __init__(self, name, info): # info = (pointsWorth, pointsReceived, categoryType, datetimePosted)
        self.assignmentName         = name
        self.numTotalPointsWorth    = info[0]
        self.numPointsReceived      = info[1]
        self.category               = info[2]
        self.datetimePosted         = info[3]

        self.gradePercent = (self.numPointsReceived / self.numTotalPointsWorth) * 100


    
    