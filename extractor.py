import course
import assignment
import dataManager
import datetime
import date
import re
import string
import os
import json


from robobrowser import RoboBrowser
from bs4 import BeautifulSoup

re._pattern_type = re.Pattern

# Global variables
studentName = ""
studentID = ""
password = ""
coursesAllMPs = list(map(list(map(course.Course,[])),[]))
periods = ['A','B','C','D','E','F','G','H']


# Get current MP based on current date 
mpStartDates = [[1,9,2019],[2,11,2019],[25,1,2020],[4,4,2020],[17,6,2020]]
leapYr = mpStartDates[len(mpStartDates)-1][2] % 4 == 0 and (mpStartDates[len(mpStartDates)-1][2] % 100 != 0 or (mpStartDates[len(mpStartDates)-1][2] % 100 == 0 and mpStartDates[len(mpStartDates)-1][2] % 400 == 0))
daysInMP = [62,84,70,76]
mp = 3
currentMPindex = 3
currentDate = datetime.datetime.today()
currentDateObj = date.Date(currentDate.day,currentDate.month,currentDate.year)
for i in range(0,4):
    mpStartDate = date.Date(mpStartDates[i][0],mpStartDates[i][1],mpStartDates[i][2])
    if(currentDateObj.compareToDateObj(mpStartDate)<0):
        currentMPindex = i-1
    if(currentMPindex<0): # Outside school year
        currentMPindex = 3


def Convert(lstLbls,lst): 
    res_dct = {lstLbls[i]: lst[i] for i in range(0, len(lst))} 
    return res_dct 


# Body
def main():
    br = RoboBrowser(parser='html.parser')
    mainpageGrades = extractMainPage(br)
    manageData()

def restart(newMP):
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
    for m in range(0,currentMPindex+1):
        for i in range(len(coursesAllMPs[m])):
            code = src[src.find(coursesAllMPs[m][i].courseName[0:7])-90:src.find(coursesAllMPs[m][i].courseName[0:7])+10]
            if(len(code)>0):
                code = code[code.find(",")+2:code.find(")")-1]
                coursesAllMPs[m][i].code = code[0:code.find(":")]
                coursesAllMPs[m][i].section = code[code.find(":")+1:len(code)+1]


    # Create assignment list for each course from course code
    for m in range(1,currentMPindex+2):
        print("MP: " + str(m))
        for i in range(len(coursesAllMPs[m-1])):
            if (len(coursesAllMPs[m-1][i].code)>0): # Does not include study hall
                br.open("https://parents.chclc.org/genesis/parents?tab1=studentdata&tab2=gradebook&tab3=coursesummary&studentid=" + str(studentID) + "&mp=MP" + str(m) +"&action=form&courseCode=" + str(coursesAllMPs[m-1][i].code) + "&courseSection=" + str(coursesAllMPs[m-1][i].section))
                a = str(br.parsed)
                determineWeighting(a,i,m-1)
                createAssignmentList(a,i,m-1)
        print("complete")

    # Deal with study halls
    for m in range(0,currentMPindex+1):
        studyHallIndex = -1
        teachers = []
        # Delete all study halls from coursesAllMPs except the first, but store all teacher names
        cNum = 0
        for c in range(len(coursesAllMPs[m])):
            if (len(coursesAllMPs[m][cNum].code)<=0):
                teachers.append(coursesAllMPs[m][cNum].teacherName)
                if (studyHallIndex<0):
                    studyHallIndex = cNum
                else:
                    coursesAllMPs[m].__delitem__(cNum)
                    cNum-=1
            cNum+=1
        
        tn = ""
        for n in range(len(teachers)):
            tn += teachers[n] + ("; " if n<len(teachers)-1 else "")
        coursesAllMPs[m][studyHallIndex].teacherName = tn
            

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

def determineWeighting(a,i,m):
    # Determines course weighting system
    a = a[a.find("Grading Information"):a.find("</td></tr></table>")]
    a = a[a.find("nowrap=\"\">Weight")+16:len(a)]
    categories = []
    weights = []

    while (a.__contains__("cellLeft")):
        categories.append(a[a.find("cellLeft")+23:a.find("</b>")])
        a = a[a.find("cellRight"):len(a)]
        weights.append(a[a.find("cellRight")+21:a.find("</td>")])
        weights[len(weights)-1] = weights[len(weights)-1][0:weights[len(weights)-1].find(".")+2]
        a = a[a.find("</tr>"):len(a)]

    coursesAllMPs[m][i].setCategories(categories,weights)


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
    
    #Avoids IndexError (list index out of range)
    tempArr = []
    for x in range(0,currentMPindex+1):
        coursesAllMPs.append(tempArr.copy())


    
    #Create list of Course objects
    for i in range(len(courseSchedule)):
        if courseSchedule[i].startswith("\n"):
            courseSchedule[i] = courseSchedule[i][1:len(courseSchedule[i])]
        courseSchedule[i] = courseSchedule[i].split("\n")
        for m in range(0,currentMPindex+1):
            sem = 1 if (m+1==1 or m+1==2) else 2
            # Only add course if it is for that marking period
            if(courseSchedule[i][2]=="FY" or courseSchedule[i][2]=="S"+str(sem)):
                coursesAllMPs[m].append(course.Course(courseSchedule[i][1],courseSchedule[i][5],courseSchedule[i][0],0 if courseSchedule[i][2]=='FY' else int(courseSchedule[i][2][1:len(courseSchedule[i][2])])))
                coursesAllMPs[m][len(coursesAllMPs[m])-1].assignments = []

def createAssignmentList(a,i,m):
    # Creates a list of assignments for every course
    a2 = a[a.find("<b>Assignments</b>")+18:a.find("Assignments graded as")]

    while(a2.__contains__("<b>")):
        valid = True
        # Find assignment info and store as STRING

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
        if (int(aDate[0:aDate.find("/")])>datetime.date.today().month):
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
            coursesAllMPs[m][i].addAssignment(assignment,intPtsWorth,intPtsRec,aCategory,aDate1)
            # Fix adding-assignment-to-all-courses issue
            for j in range(len(coursesAllMPs[m])):
                if (j!=i):
                    temp = []
                    for x in range(len(coursesAllMPs[m][j].assignments)):
                        if ((str(coursesAllMPs[m][j].assignments[x].assignmentName).__contains__(assignment))==0):
                            temp.append(coursesAllMPs[m][j].assignments[x])
                    coursesAllMPs[m][j].assignments = temp.copy()
            
    
def getCourseList(mp):
    courseList = []
    for i in range(len(coursesAllMPs[mp-1])):
        courseList.append(coursesAllMPs[mp-1][i])
    return courseList

def manageData():
    # Get current MP based on current date
    currentDate = datetime.datetime.today()
    currentDateObj = date.Date(currentDate.day,currentDate.month,currentDate.year)
    currentMPindex = 3

    for i in range(0,4):
        mpStartDate = date.Date(mpStartDates[i][0],mpStartDates[i][1],mpStartDates[i][2])
        if(currentDateObj.compareToDateObj(mpStartDate)<0):
            currentMPindex = i-1
    if(currentMPindex<0): # Current date is outside of school year
        currentMPindex = 3 # 4th marking period
    
    numDaysInSchoolYear = 0
    for mp in range(len(coursesAllMPs)):
        # print("MP: " + str(mp+1))
        startDate = date.datetime.date(mpStartDates[mp][2],mpStartDates[mp][1],mpStartDates[mp][0])
        endDate = date.datetime.date(mpStartDates[mp+1][2],mpStartDates[mp+1][1],mpStartDates[mp+1][0]-1)
        daysInMP[mp] = endDate.__sub__(startDate).days
        numDaysInSchoolYear += daysInMP[mp]#endDate.__sub__(startDate).days
    firstDay = datetime.date(mpStartDates[0][2],mpStartDates[0][1],mpStartDates[0][0])

    # for mp in range(len(coursesAllMPs)):
    #     for c in range(len(coursesAllMPs[mp])):
    #         print(coursesAllMPs[mp][c].courseName)
    #     print("\n")
    # exit(0)




    data = [[[list]]]*(numDaysInSchoolYear+1)
    for m in range(len(coursesAllMPs)):
        courseDataAllMPs = [[]]
        dm = dataManager.DataManager(studentName,studentID,coursesAllMPs[m],m+1)
        for c in range(len(coursesAllMPs[m])):
            dailyGrades = dm.getDailyCourseGradesForMP(c,m)
            for d in range(len(dailyGrades)):
                daysSinceStartOfYear = dailyGrades[d][0].__sub__(firstDay).days - 1
                try:
                    data[daysSinceStartOfYear-1].append(dailyGrades[d])
                except IndexError:
                    print("IndexError")
                

    allData = [[[[]]]]  # [course][[[date,grade,ptsRec,ptsW],...] for mp1, [[date,grade,ptsRec,ptsW],...] for mp2, ...]
                        # allData[0][0][0][1] = [AP ENG/LANG & COMP][mp1][2019-09-01][grade]

    for c in range(0,len(coursesAllMPs[0])):
        courseDataAllMPs = [[[]]]
        for x in range(0,currentMPindex+1):
            mp = x
            dm = dataManager.DataManager(studentName,studentID,coursesAllMPs[mp],mp)
            dailyGrades = dm.getDailyCourseGradesForMP(c,mp)
            courseDataAllMPs.append(dailyGrades)
        
        courseDataAllMPs.pop(0)
        allData.append(courseDataAllMPs)
    allData.pop(0)

    # allData2 = [list]*len(allData[0][0])
    allData2 = [[[]]] # [[date[course[infotype]]]...for all dates]

    for m in range(0,len(allData[0])):
        for d in range(len(allData[0][m])): # for every day in MP
            if(d<=numDaysInSchoolYear):
                arrC = []
                for c in range(len(coursesAllMPs[m])): # for every course
                    arr = [allData[c][m][d][1],allData[c][m][d][2],allData[c][m][d][3]]
                    arrC.append(arr)
                arrDC = [allData[0][m][d][0], arrC] # [date,[info1,info2,info3]]
                allData2.append(arrDC)
    allData2.pop(0)
    


    # OUTPUT DATA TO FILE
    try:
        outfile = open("dailyGradesFile.txt","x")
    except FileExistsError:
        outfile = open("dailyGradesFile.txt","w")

    with open("gradesDictionary.txt",'a') as json_outfile:
        json_outfile.write("[")

    mpIndexPlus1 = 1
    for d in range(len(allData2)):
        dDate = date.Date(allData2[d][0].day,allData2[d][0].month,allData2[d][0].year)
        endDate = date.Date(mpStartDates[4][0],mpStartDates[4][1],mpStartDates[4][2])
        if(dDate.compareToDateObj(endDate)>=0):
            break # Stop at last day of school
        print(str(allData2[d][0]))
        outfile.write(str(allData2[d][0])+"\n") # write date
        

        for c in range(len(allData2[d][1])):
            try:
                        
                if (date.Date(allData2[d][0].day,allData2[d][0].month,allData2[d][0].year).compareToDMY(mpStartDates[mpIndexPlus1][0],mpStartDates[mpIndexPlus1][1],mpStartDates[mpIndexPlus1][2])>=0):
                    mpIndexPlus1 += 1
                
                lstLbls = ["Date","Course","Grd","PR","PW"]
                lst = []
                if (len(coursesAllMPs[mpIndexPlus1-1][c].code)>0):
                    lst = [str(allData2[d][0]),coursesAllMPs[mpIndexPlus1-1][c].courseName, allData2[d][1][c][0],allData2[d][1][c][1],allData2[d][1][c][2]]
                    print("\t{0:30} {1:15} {2:15} {3:15}".format(coursesAllMPs[mpIndexPlus1-1][c].courseName+":: ","Grd:"+str(allData2[d][1][c][0]),"PR:"+str(allData2[d][1][c][1]),"PW:"+str(allData2[d][1][c][2])))
                    outfile.write("\t{0:30} {1:15} {2:15} {3:15}\n".format(coursesAllMPs[mpIndexPlus1-1][c].courseName+":: ","Grd:"+str(allData2[d][1][c][0]),"PR:"+str(allData2[d][1][c][1]),"PW:"+str(allData2[d][1][c][2])))
                else:
                    lst = [str(allData2[d][0]), coursesAllMPs[mpIndexPlus1-1][c].courseName, "----","----","----"]
                    print("\t{0:30} {1:15} {2:15} {3:15}".format(coursesAllMPs[mpIndexPlus1-1][c].courseName+":: ","Grd:----","PR:----","PW:----"))
                    outfile.write("\t{0:30} {1:15} {2:15} {3:15}\n".format(coursesAllMPs[mpIndexPlus1-1][c].courseName+":: ","Grd:----","PR:----","PW:----"))
                with open("gradesDictionary.txt",'a') as json_outfile:
                    json.dump(Convert(lstLbls,lst),json_outfile,indent=2)
                    if (d<len(allData2) or c<len(allData2[d][1])):
                        json_outfile.write(",\n")
            except IndexError:
                break

    with open("gradesDictionary.txt",'a') as json_outfile:
        json_outfile.write("]")
    outfile.close()


if __name__ == '__main__':
    main()