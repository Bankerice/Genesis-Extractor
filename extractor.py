import course
import assignment
import userActions
import datetime
import date
import re
import string
import os

from robobrowser import RoboBrowser
from bs4 import BeautifulSoup

re._pattern_type = re.Pattern

# Global variables
studentName = ""
studentID = ""
password = ""
courses = list(map(course.Course,[]))
periods = ['A','B','C','D','E','F','G','H']
mp = 2
mpStartDates = [[1,9,2019],[2,11,2019],[25,1,2020],[4,4,2020]]

# Body
def main():
    br = RoboBrowser(parser='html.parser')
    mainpageGrades = extractMainPage(br)
    userAct()

def restart(newMP):
    # Clear arrays
    # courses = []
    # mp = newMP

    br = RoboBrowser(parser='html.parser')
    mainpageGrades = extractMainPage(br)

def initUserData():
    if not os.path.exists("config.ini"):  
        file = open("config.ini","w")

        file.write(input("Student ID: ")+"\n")
        file.write(input("Password: ")+"\n")

        file.close()


def extractMainPage(robo):
    br = robo
    br.open("https://parents.chclc.org/genesis/sis/view?gohome=true")


    while br.url == "https://parents.chclc.org/genesis/sis/view?gohome=true":
        initUserData()

        form = br.get_form()

        file = open("config.ini","r")
        text = file.readlines()
        studentID = text[0].strip("\n")
        password = text[1].strip("\n")
        form["j_username"] = studentID+ "@chclc.org"
        form["j_password"] = password
        br.submit_form(form)
        file.close()

        if(br.url == "https://parents.chclc.org/genesis/sis/view?gohome=true"):
            initUserData()
            os.remove("config.ini")
            
    #Converts the HTML of the Summary page into a string and uses it to create courses list of Course objects
    br.open("https://parents.chclc.org/genesis/parents?tab1=studentdata&tab2=studentsummary&action=form&studentid="+studentID)
    src = str(br.parsed())
    courseSchedule = src[src.find('Teacher'):len(src)]
    courseSchedule = courseSchedule[courseSchedule.find('>A<')+1:courseSchedule.find('listheading')]
    soup = BeautifulSoup(courseSchedule,"lxml")
    courseSchedule = ''.join(soup.findAll(text=True))
    createCourseList(courseSchedule)
    


    #Converts the HTML of the grade page into a string
    br.open("https://parents.chclc.org/genesis/parents?tab1=studentdata&tab2=gradebook&tab3=weeklysummary&action=form&studentid="+studentID)
    src = str(br.parsed)
    links = br.get_links()
    urls = [link.get("href") for link in links]
    for i in range(len(links)):
        if str(links[i]).__contains__("listassignments"):
            br.follow_link(links[i])
            a = str(br.parsed)
            a = " ".join(a.split())

    # CREATE ASSIGNMENT LIST
    # Determine course codes for each course
    for i in range(len(courses)):
        code = src[src.find(courses[i].courseName[0:7])-90:src.find(courses[i].courseName[0:7])+10]
        if(len(code)>0):
            code = code[code.find(",")+2:code.find(")")-1]
            courses[i].code = code[0:code.find(":")]
            courses[i].section = code[code.find(":")+1:len(code)+1]

    # Create assignment list for each course from course code
    for i in range(len(courses)):
        if (len(courses[i].code)>0): # Does not include study hall
            br.open("https://parents.chclc.org/genesis/parents?tab1=studentdata&tab2=gradebook&tab3=coursesummary&studentid=" + str(studentID) + "&mp=MP" + str(mp) +"&action=form&courseCode=" + str(courses[i].code) + "&courseSection=" + str(courses[i].section))
            a = str(br.parsed)
            createAssignmentList(a,i)
    

    #Removes initial Javascript
    src = src[src.find('<!-- Start of Header-->')+len('<!-- Start of Header-->'): len(src)]

    #Removes all HTML tags
    soup = BeautifulSoup(src,"lxml")
    src = ''.join(soup.findAll(text=True))

    #Removes all tabs and newlines
    src = " ".join(src.split())
    
    #Cuts the string into the important parts
    notDone = True
    i = src.find('Fri')+3 #Consistent and close reference point
    while(notDone):
        i += 1
        if(ord(src[i])>=57):
            notDone = False
    src = src[i+2:src.rfind('%')+1]
    
    #Parses the text
    courseInfo = src.split('%')
    courseInfo.pop()
    for i in range(len(courseInfo)):
        courseInfo[i] = courseInfo[i].split("Email:")
        if(i != 0):
            courseInfo[i][0] = courseInfo[i][0][11:len(courseInfo[i][0])]
    
        # Separate info
        cInfo = courseInfo[i][0]
        cName = cInfo[0:cInfo[0:cInfo.index(",")].rfind(" ")]
        cTeacher = cInfo[cInfo[0:cInfo.index(",")].rfind(" ")+1:len(cInfo)-1]


    
   
def createCourseList(courseSchedule):
    #Creates courses list of Course objects from info on Summary page
    
    #Ignore LBs
    while(courseSchedule.__contains__("L1\n")):
        lb1 = courseSchedule[courseSchedule.find('L1\n'):len(courseSchedule)]
        lb1 = lb1[0:lb1.find("\n\n")+3]
        courseSchedule = courseSchedule[0:courseSchedule.find('L1\n')] + courseSchedule[courseSchedule.find('L1\n')+len(lb1):len(courseSchedule)]
    while(courseSchedule.__contains__("L2\n")):
        lb2 = courseSchedule[courseSchedule.find('L2\n'):len(courseSchedule)]
        lb2 = lb2[0:lb2.find("\n\n")+3]
        courseSchedule = courseSchedule[0:courseSchedule.find('L2\n')] + courseSchedule[courseSchedule.find('L2\n')+len(lb2):len(courseSchedule)]

    courseSchedule = courseSchedule[0:len(courseSchedule)-3]
    courseSchedule = courseSchedule.split("\n\n")
    
    #Create list of Course objects
    for i in range(len(courseSchedule)):
        if courseSchedule[i].startswith("\n"):
            courseSchedule[i] = courseSchedule[i][1:len(courseSchedule[i])]
        courseSchedule[i] = courseSchedule[i].split("\n")
        courses.append(course.Course(courseSchedule[i][1],courseSchedule[i][5],courseSchedule[i][0],True if courseSchedule[i][2]=='FY' else False))
        courses[i].assignments = []

def createAssignmentList(a,i):
    # Creates a list of assignments for every course
    
    a2 = a[a.find("<b>Assignments</b>")+18:a.find("Assignments graded as")]

    while(a2.__contains__("<b>")):
        valid = True

        # Assignment Name
        assignment = a2[a2.find("<b>")+3:a2.find("</b>")]
        a2 = a2[a2.find("</b>")+4:len(a2)]
        
        # Assignment Category
        aCategory = a[a.find("Close Window")+10:len(a)]
        aCategory = aCategory[aCategory.find("</div>")+6:aCategory.find("<td")]
        aCategory = " ".join(aCategory.split())
        aCategory = aCategory[0:aCategory.find("</td>")]

        # Assignment Date Posted
        aDate = a[a.find("listrow"):len(a)]
        aDate = aDate[aDate.find("</div>")+1:aDate.find("style")]
        aDate = aDate[aDate.find("<div>")+5:aDate.find("</div>")]
        year = datetime.date.today().year
        if (int(aDate[0:aDate.find("/")])>datetime.date.today().year):
            year -= 1
        aDate1 = datetime.date(year,int(aDate[0:aDate.find("/")]),int(aDate[aDate.find("/")+1:len(aDate)]))
        a = a[a.find("Close Window")+10:len(a)]

        # Assignment Grade
        a2 = " ".join(a2.split())
        
        aGrade = a2[a2.find("nowrap="):a2.find("nowrap=")+30]
        aGrade = aGrade[0:aGrade.find("<")]
        if(aGrade.__contains__("/")): # Found " / " marker indicating a grade
            aPtsRec = aGrade[aGrade.find(">")+2:aGrade.find(" / ")]
            aPtsWorth = aGrade[aGrade.find(" / ")+3:len(aGrade)]
        else:
            continue # Assignments marked as "DONE," etc.
        try: 
            intPtsWorth = float(aPtsWorth)
            intPtsRec = float(aPtsRec)
        except ValueError:
            valid = False
            
        # Add assignment to course assignments list 
        if (valid):
            courses[i].addAssignment(assignment,intPtsWorth,intPtsRec,aCategory,aDate1)
            # Fix adding-assignment-to-all-courses issue
            for j in range(len(courses)):
                if (j!=i):
                    temp = []
                    for x in range(len(courses[j].assignments)):
                        if ((str(courses[j].assignments[x].assignmentName).__contains__(assignment))==0):
                            temp.append(courses[j].assignments[x])
                    courses[j].assignments = temp
            
    
def getCourseList():
    courseList = []
    for i in range(len(courses)):
        courseList.append(courses[i])
    return courseList

def userAct():
    # Get current MP based on current date
    currentMP = 2
    currentDate = datetime.datetime.today()
    currentDateObj = date.Date(currentDate.day,currentDate.month,currentDate.year)
    for i in range(0,4):
        mpStartDate = date.Date(mpStartDates[i][0],mpStartDates[i][1],mpStartDates[i][2])
        if(currentDateObj.compareToDateObj(mpStartDate)<0):
            currentMP = i-1
    
    interface = userActions.UserActions(studentName,studentID,2)



    allData = [[[[]]]] # [course][[[date,grade,ptsRec,ptsW],...] for mp1, [[date,grade,ptsRec,ptsW],...] for mp2, ...]
        # allData[0][0][0][1] = [AP ENG/LANG & COMP][mp1][2019-09-01][grade]
    interfaces = []
    for c in range(0,len(courses)):
        courseDataAllMPs = [[[]]]
        for x in range(1,currentMP+1):
            m = x
            mp = m
            interfaces.append(userActions.UserActions(studentName,studentID,m))
            endDates = []
            mpEndDate = date.Date(mpStartDates[m][0]-1,mpStartDates[m][1],mpStartDates[m][2])
            if (mpEndDate.compareToDateObj(currentDateObj)>0):
                mpEndDate = currentDateObj
            dailyGrades = interfaces[len(interfaces)-1].getDailyCourseGrades(c,mpStartDates[m-1][0],mpStartDates[m-1][1],mpStartDates[m-1][2],mpEndDate.date.day,mpEndDate.date.month,mpEndDate.date.year)
            courseDataAllMPs.append(dailyGrades)
        
        courseDataAllMPs.pop(0)
        allData.append(courseDataAllMPs)
    allData.pop(0)

    print("-------------------------------------------------------------------")
    
    # allData2 = [list]*len(allData[0][0])
    allData2 = [[[]]] # [[date[course[infotype]]]...for all dates]

    for m in range(0,len(allData[0])):
        for d in range(len(allData[0][m])): # for every day in first MP
            arrC = []
            for c in range(len(courses)): # for every course
                arr = [allData[c][m][d][1],allData[c][m][d][2],allData[c][m][d][3]]
                arrC.append(arr)
            arrDC = [allData[0][m][d][0], arrC] # [date,[info1,info2,info3]]
            allData2.append(arrDC)
    allData2.pop(0)



    # OUTPUT DATA TO FILE
    try:
        outfile = open("outfile.txt","x")
    except FileExistsError:
        outfile = open("outfile.txt","w")

    
    for d in range(len(allData2)):
        print(str(allData2[d][0]))
        outfile.write(str(allData2[d][0])+"\n") # write date
        for c in range(len(allData2[d][1])):
            print("\t{0:30} {1:15} {2:15} {3:15}".format(courses[c].courseName+":: ","Grd:"+str(allData2[d][1][c][0]),"PR:"+str(allData2[d][1][c][1]),"PW:"+str(allData2[d][1][c][2])))
            outfile.write("\t{0:30} {1:15} {2:15} {3:15}\n".format(courses[c].courseName+":: ","Grd:"+str(allData2[d][1][c][0]),"PR:"+str(allData2[d][1][c][1]),"PW:"+str(allData2[d][1][c][2])))
    
    outfile.close()


if __name__ == '__main__':
    main()


