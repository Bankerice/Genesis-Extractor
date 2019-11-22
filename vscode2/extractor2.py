import course
import assignment
import datetime
import re
import string


from robobrowser import RoboBrowser
from bs4 import BeautifulSoup

re._pattern_type = re.Pattern

# Global variables
studentName = ""
studentID = ""
courses = list(map(course.Course,[]))
periods = ['A','B','C','D','E','F','G','H']

# Body
def main():
    br = RoboBrowser(parser='html.parser')

    mainpageGrades = extractMainPage(br)


def extractMainPage(robo):
    br = robo
    br.open("https://parents.chclc.org/genesis/sis/view?gohome=true")
    form = br.get_form()
    form["j_username"] = "3006633@chclc.org"
    form["j_password"] = "jklamchops"
    br.submit_form(form)

    #Converts the HTML of the Summary page into a string and uses it to create courses list of Course objects
    studentID = "3006633"
    br.open("https://parents.chclc.org/genesis/parents?tab1=studentdata&tab2=studentsummary&action=form&studentid="+studentID)
    src = str(br.parsed())
    studentID = src[src.find("Student ID")+34:src.find("Student ID")+41]
    
    courseSchedule = src[src.find('Teacher'):len(src)]
    courseSchedule = courseSchedule[courseSchedule.find('>A<')+1:courseSchedule.find('listheading')]
    soup = BeautifulSoup(courseSchedule,"lxml")
    courseSchedule = ''.join(soup.findAll(text=True))
    createCourseList(courseSchedule)
    # for i in range(len(courses)):
    #     print(courses[i].period+": " + courses[i].courseName + "\t" + courses[i].teacherName)

    #Converts the HTML of the grade page into a string
    #br.open("document.frmHome.action='parents?tab1=studentdata&tab2=gradebook&tab3=listassignments&studentid="+studentID+"&action=form&date="+)
    br.open("https://parents.chclc.org/genesis/parents?tab1=studentdata&tab2=gradebook&tab3=weeklysummary&action=form&studentid="+studentID)
    src = str(br.parsed)
    
    
    links = br.get_links()
    urls = [link.get("href") for link in links]
    for i in range(len(links)):
        #print(links[i])
        if str(links[i]).__contains__("listassignments"):
            br.follow_link(links[i])
            a = str(br.parsed)
            a = " ".join(a.split())
            
            #print(a)
            courseN = a[a.find("name=\"fldCourse\""):len(a)]
            courseN = courseN[courseN.find("option selected"):courseN.find("</select>")]
            courseN = courseN[courseN.find(">")+1:courseN.find("<")-1]
            if (len(courseN)>0):
                courseN = " ".join(courseN.split())
            
            assignment = a[a.find("<b>"):a.find("</b>")]
            assignment = assignment[3:len(assignment)]
            
            aCategory = a[a.find("Close Window"):len(a)]
            aCategory = aCategory[aCategory.find("</div>")+6:aCategory.find("<td")]
            aCategory = " ".join(aCategory.split())
            aCategory = aCategory[0:aCategory.find("</td>")-1]
            
            aDate = a[a.find("listroweven"):len(a)]
            aDate = aDate[aDate.find("</div>")+1:aDate.find("style")]
            aDate = aDate[aDate.find("<div>")+5:aDate.find("</div>")]
            if (len(aDate)>0):
                yr = 0
                if (int(datetime.datetime.today().month) >= int(aDate[0:aDate.find("/")])):
                    yr = datetime.datetime.today().year
                else:
                    yr = datetime.datetime.today().year - datetime.timedelta(365)
                aDate = datetime.datetime(yr,int(aDate[0:aDate.find("/")]),int(aDate[aDate.find("/")+1:len(aDate)]))
            
            aGrade = a[(a.find(" / "))-5:(a.find(" / "))+5]
            aGrade = " ".join(aGrade.split())
            aPtsRec = aGrade[aGrade.find(">")+2:aGrade.find(" / ")]
            aPtsWorth = aGrade[aGrade.find(" / ")+3:len(aGrade)]
            if (len(aPtsWorth)>0):
                intPtsWorth = int(aPtsWorth)
                intPtsRec = int(aPtsRec)
                for i in range(len(courses)):
                    if (str(courses[i].courseName) == courseN):
                        courses[i].addAssignment(assignment,intPtsWorth,intPtsRec,aCategory,aDate.date)
                        print(courses[i].courseName)
                        print(courses[i].assignments[0].assignmentName + "\t" + str(courses[i].assignments[0].numPointsReceived))
            


    # Failed attempt to change course to view another course's assignments
    # forms = br.get_forms()
    # f = forms[0]
    # f['fldCourse'].value = "130A:3"
    # br.submit_form(f)
    
    


    #Removes initial Javascript
    src = src[src.find('<!-- Start of Header-->')+len('<!-- Start of Header-->'): len(src)]

    #Removes all HTML tags
    soup = BeautifulSoup(src,"lxml")
    src = ''.join(soup.findAll(text=True))

    #Removes all tabs and newlines
    src = " ".join(src.split())
    #studentName = src[src.index("Select Student:")+16:src.index("Weekly Summary")-1]    
    
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

        # Create course - unnecessary if already created from Summary page
        # for i in courses:
        #     if(str(courses[i].courseName) == cName):
        #         print("already there: " + cName)
        #     else:
        #         c = course.Course(cName,cTeacher,"P",True)
        # # Add assignments from List Assignments tab (click on link) 
        # # Example: c.addAssignment("a1",10,10,assignment.Category.MajorAssessments,datetime.datetime.today().date)
        #         courses.append(c)
        #         print(cName)
    
    # Test by printing info
    #print("Student: " + studentName)
    # for i in range(len(courses)):
    #     print(str(courses[i].currentMPGrade) + " in " + courses[i].courseName 
    #     + " with " + courses[i].teacherName + " during " + courses[i].period)

    
   
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
        #print(courseSchedule[i])
        # for j in range(len(courses)):
        #     if (str(courses[j].courseName) == str(courseSchedule[i][1]) & courses[j].fullYear)==False:
        courses.append(course.Course(courseSchedule[i][1],courseSchedule[i][5],courseSchedule[i][0],True if courseSchedule[i][2]=='FY' else False))
    # for i in range(len(courses)):
    #     print(courses[i].period + ": " + courses[i].courseName + "\t" + courses[i].teacherName)
    for i in range(len(courses)):
        print(courses[i].courseName)

if __name__ == '__main__':
    main()


