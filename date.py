import re
import datetime

class Date():
    date = datetime.date(1,1,1)
    
    def __init__(self,day,month,year):
        self.date = datetime.date(year,month,day)
        
    # Compares this Date object to a datetime.date() object
    # Returns int -1, 0, or 1
    def compareToDatetimeDate(self,date2) -> int:
        y1 = self.date.year
        m1 = self.date.month
        d1 = self.date.day

        y2 = date2.year
        m2 = date2.month
        d2 = date2.day

        return(self.compareTwoDates(d1,m1,y1,d2,m2,y2))

    # Compares this Date object to another Date object
    # Returns int -1, 0, or 1
    def compareToDateObj(self,date2) -> int:
        y1 = self.date.year
        m1 = self.date.month
        d1 = self.date.day

        y2 = date2.date.year
        m2 = date2.date.month
        d2 = date2.date.day

        return(self.compareTwoDates(d1,m1,y1,d2,m2,y2))
        

    # Compares this Date object to a date given by d2,m2,y2 parameters
    # Returns int -1, 0, or 1
    def compareToDMY(self,d2,m2,y2):
        y1 = self.date.year
        m1 = self.date.month
        d1 = self.date.day

        return(self.compareTwoDates(d1,m1,y1,d2,m2,y2))


    # Returns -1 if first date is earlier than second date
    #          0 if both are the same date
    #          1 if first date is later than second date
    @staticmethod
    def compareTwoDates(d1,m1,y1,d2,m2,y2) -> int:
        ret = 2

        # First date is earlier
        if (y1<y2 or (y1==y2 and (m1<m2 or (m1==m2 and d1<d2)))):
            ret = -1
            # print(str(d1)+" "+str(m1)+" "+str(y1)+" is before "+str(d2)+" "+str(m2)+" "+str(y2))

        # Same date
        elif (y1==y2 and m1==m2 and d1==d2):
            ret = 0
            # print(str(d1)+" "+str(m1)+" "+str(y1)+" is the same date as "+str(d2)+" "+str(m2)+" "+str(y2))

        # First date is later
        elif (y2<y1 or (y2==y1 and (m2<m1 or (m2==m1 and d2<d1)))):
            ret = 1
            # print(str(d1)+" "+str(m1)+" "+str(y1)+" is after "+str(d2)+" "+str(m2)+" "+str(y2))
        
        return ret
    
    def toString(self) -> str:
        ret = str(self.date.year)+" "+str(self.date.month)+" "+str(self.date.day)


# Testing
# date1 = Date(13,11,2019)
# date2 = Date(2,11,2019)
# date3 = datetime.date(2019,11,14)
# print(date1.compareToDateObj(date2))
# print(date1.compareToDatetimeDate(date3))
# print(Date.compareTwoDates(13,11,2019,13,11,2019))