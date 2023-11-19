from flask import Flask, request,render_template,redirect,session,Response
from pymongo import MongoClient
import datetime
from time import gmtime, strftime
import os
from werkzeug.utils import secure_filename
from bson.objectid import ObjectId
from camera import VideoCamera
import cv2


UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config["SECRET_KEY"] = "a1nbskdgksdgak697auskkdbakjfa8s7f08ajsfbjabsfljf08a7f0asfal"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 *1024

try:
   client = MongoClient("mongodb+srv://eExamSystem:8yUZvK6Z95HNOeJs@eexam-system.f07qvqu.mongodb.net/test")
   print("Mongo Connected successfully!!!")
except:  
    print("Could not connect to MongoDB")

db = client["Exam_system"]
UserDb = db["Users"]
LeftMenuDb = db["LeftMenu"]
BranchDb = db["Branches"]
SubjectDb = db["Subjects"]
QuestionDb = db["QuestionBank"]
ExamPaperDb = db["ScheduleExam"]



@app.context_processor
def context_processor():
    FMdata = []
    SMdata = []
    TDt = datetime.datetime.now();
    MDt = f"({TDt.strftime('%d %b %Y')})"
    if "userroll" in session :
       if  session["userroll"] == "Admin":
           AdMenu = LeftMenuDb.find()
           for item in AdMenu :
               if item["PageType"] == "First" :
                    FMdata.append(item)
               if item["PageType"] == "Second" :
                    SMdata.append(item)
       elif  session["userroll"] == "Faculty":
             AdMenu = LeftMenuDb.find()
             FJson =['Setting',"Faculty List","Subjects","Papers","Exam","Student List","Branches"]
             for item in AdMenu :
                if item["PageTitel"] not in FJson :
                   if item["PageType"] == "First" :
                    FMdata.append(item)
                   if item["PageType"] == "Second" :
                    SMdata.append(item)
       else :
         AdMenu = LeftMenuDb.find()
         FJson =['Setting',"Faculty List","Subjects","Papers","Student List","Add Subject","Add Exam","Add Notice","Schedule Exam","Add questions","Branches"]
         for item in AdMenu :
             if item["PageTitel"] not in FJson :
                if item["PageType"] == "First" :
                    FMdata.append(item)
                if item["PageType"] == "Second" :
                    SMdata.append(item)
    return dict(FLeftDt = FMdata, SLeftDt = SMdata, MDt = MDt)

def LogStatus() :
    return session["LogStatus"]

def DateFormat(x, t):
    fDate = ""
    if t :
       fDate = x.strftime('%d/%m/%Y %H:%M:%S')
    else :
       fDate = x.strftime('%d/%m/%Y')
    return fDate

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

video_stream = VideoCamera()

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')



@app.route('/video_feed', methods=['GET'])
def video_feed():
     return Response(gen(video_stream),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
 
@app.route('/', methods=['GET','POST']) 
def Index():
     return redirect("/login", code=302)
 
@app.route('/logout', methods=['GET','POST']) 
def Logout():
     session.clear()
     session["LogStatus"] = False
     return redirect("/login", code=302)
     
@app.route('/login',  methods=['GET','POST'])
def Login():
    error = None
    if request.method == 'POST':
         user_id = request.form["userid"]
         password = request.form["password"]
         UserData = UserDb.find_one({"user_id": user_id, "password":password})
         if  UserData :
           session["LogStatus"] = True
           session["username"] = UserData["name"]
           session["userid"] = UserData["user_id"]
           session["userroll"] = UserData["roll"]
           session["useremail"] = UserData["email"]
           session["logtime"] = f"{datetime.datetime.now()}"
           session["gender"] = UserData["gender"]
           session["image"] = f'uploads/{UserData["image"]}'
           return redirect("/home",code=302)
         else :  
            error = 'Invalid user id/password'
    return render_template("login.html" ,error = error)

@app.route('/signup',  methods=['GET','POST'])
def Signup():
    error = None
    BranchLst = BranchDb.find()
    if request.method == 'POST':
         branch = request.form["branch"]
         email = request.form["email"]
         name = request.form["username"]
         roll = "Student"
         password = request.form["password"]
         gender = request.form["gender"]
         if 'file' in request.files:
            image = request.files["file"]
            if image and allowed_file(image.filename):
               filename = secure_filename(image.filename)
              
         if UserDb.find_one({"email": email}) :
             error = 'Email Id alredy exist'
         else :
            post = {"name": name,
                   "email": email,
                   "password": password,
                   "roll": roll,
                   "branch": branch,
                   "user_id": f"STU{datetime.datetime.now().strftime('%f')}{email[0:2].upper()}",
                   "date": datetime.datetime.now(),
                   "gender": gender,
                   "image": filename
                   }
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))      
            UserDb.insert_one(post)
            return redirect("/login", code=302)
          
    return render_template("signup.html", error = error, Branchs = BranchLst)

@app.route('/home')
def Home():
     if request.method == 'GET':
      if LogStatus() :
        return render_template("home.html",name = session["username"])
      return redirect("logout")
     
@app.route('/subject/subject',methods=['Get','POST'])
def Subject():
    if request.method == 'GET':
       if "dltId" in request.args:
            SubjectDb.delete_one({"_id": ObjectId(request.args.get("dltId"))})
       if LogStatus():
          SubData = []
          for item in SubjectDb.find():
             SubData.append(item)
          return render_template("/subject/subject.html",SubjectJson =SubData)  
      
    return redirect("/logout")

@app.route('/subject/add_subject',methods=['GET','POST'])
def AddSubject():
    error = None
    if request.method=='GET':
        if LogStatus():
           EditId = request.args.get("editId")
           editId = SubjectDb.find_one({"_id": ObjectId(EditId)})
           BranchDt = BranchDb.find()
           return render_template("/subject/add_subject.html",BranchDt = BranchDt, editId = editId)
        return redirect("/logout")
    if request.method == 'POST':
       Uid = request.args.get('editId')
       if(Uid):
            updateVal = {
                "_id" : ObjectId(Uid),
                "SubTitel" : request.form["subjectname"],
                "SubCode" : request.form["subjectcode"],
                "Branch" : request.form["branchname"]
                }
            OldData =  SubjectDb.find_one({"_id" : ObjectId(Uid)})
            SubjectDb.update_one(OldData,{"$set":updateVal})
       else :
                 branchName = request.form["branchname"]
                 subjectName = request.form["subjectname"]
                 subjectCode = request.form["subjectcode"]
                 if SubjectDb.find_one({"subTitel" : subjectName}) :
                     error = 'Subject already exist'
                    
                 else :
                      postDt = {
                             "SubTitel" : subjectName,
                             "SubCode" : subjectCode,
                             "Branch" :branchName,
                             }   
                      SubjectDb.insert_one(postDt)
       return redirect("/subject/subject", code=302)  

@app.route('/branch/add_branch',methods=['GET','POST'])
def AddBranch():
    error = None
    if request.method == 'GET':
       if LogStatus():
          Uid = request.args.get("editId")
          editDt = BranchDb.find_one({"_id": ObjectId(Uid)})
          return render_template("/branch/add_branch.html",EditDt = editDt)
       return redirect("/logout")
    if request.method == 'POST':
       Uid = request.form['Id']
       if(Uid):
            updateVal = {
                "_id" : ObjectId(Uid),
                "Bname" : request.form['branchname'],
                "Bcode" : request.form['branchcode'],
                "Cname" :"NIT AGARTALA",
                "Ccode" : "NIT001",
                }
            OldData =  BranchDb.find_one({"_id" : ObjectId(Uid)})
            BranchDb.update_one(OldData,{"$set":updateVal})  
       else :
              
                Branch_name = request.form["branchname"]
                Branch_code = request.form["branchcode"]
                College= "NIT AGARTALA"
                College_code = "NIT001"

                if BranchDb.find_one({"Bname" : Branch_name}) :
                     error = 'Branch already exist'
                elif BranchDb.find_one({"Bcode" : Branch_code}) :
                     error = 'Branch already exist'
                else :
                     postDt = {
                           "Bname" : Branch_name,
                           "Bcode" : Branch_code,
                           "Cname" : College,
                           "Ccode" : College_code,
                           "Date"  : datetime.datetime.now(),
                        }    
                     BranchDb.insert_one(postDt)
       
       return redirect("/branch/branch", code=302)  
           
@app.route('/branch/branch', methods = ['GET'])
def Branch():
    if request.method =='GET':
         if "dltId" in request.args:
            BranchDb.delete_one({"_id": ObjectId(request.args.get("dltId"))})
         if LogStatus():
            BranchData = []
            for item in BranchDb.find():
                item['Date'] = DateFormat(item['Date'], False)
                BranchData.append(item)
            return render_template("/branch/branch.html",BranchData=BranchData)    
 
@app.route('/student/students', methods = ['GET'])
def Students():
    if request.method == 'GET':
       if "dltId" in request.args:
            UserDb.delete_one({"_id": ObjectId(request.args.get("dltId"))})
       if LogStatus():
          StuData = []
          for item in UserDb.find({"roll":"Student"}):
             item['date'] = DateFormat(item['date'], False)
             StuData.append(item)
          return render_template("/student/students.html",StudentJson =StuData)  
      
    return redirect("/logout")

@app.route('/student/add_student', methods = ['GET','POST'])
def AddStudent():
    error = None
    BranchLst = BranchDb.find()
    if request.method == 'GET':
       if LogStatus():
          return render_template("/student/add_student.html", Branchs = BranchLst)
       return redirect("/logout")
    if request.method == 'POST':
       Branch = request.form["branch"]
       email = request.form["semail"]
       name = request.form["sname"]
       roll = "Student"
       password = request.form["spassword"]
       gender = request.form["sgender"]

       if 'simage' in request.files:
           image = request.files["simage"]
           if image and allowed_file(image.filename):
              filename = secure_filename(image.filename)
       if UserDb.find_one({"email" : email}) :
           error = 'Email Id already exist'
          
       else :
            postDt = {"name" : name,
                   "email" : email,
                   "password" :password,
                   "roll" : roll,
                   "user_id" : f"STU{datetime.datetime.now().strftime('%f')}{email[0:2].upper()}",
                   "branch" :Branch,
                   "date" : datetime.datetime.now(),
                   "gender" :gender,
                   "image" :filename
                   }
            
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))         
            UserDb.insert_one(postDt)
       return redirect("/student/students", code=302) 

@app.route('/setting/pages', methods=['GET','POST'])
def Pages():
    if request.method == 'GET':
        if LogStatus() :
          LFMdata = []
          for menu in LeftMenuDb.find() :
              menu['date'] = DateFormat(menu['date'], False)
              LFMdata.append(menu)
          return render_template("/setting/pages.html", MenuJson = LFMdata)
        return redirect("/logout")
    if request.method == 'POST':
        mode = request.args.get("mode")
        data = request.args.get("data")
        if mode == "delete" :
           LeftMenuDb.delete_one({"PageTitel":data.split(":")[1]})
           return  {"Redirect" : "/setting/pages","message" : "Deleted Successfully"}
        return redirect("/setting/pages")

@app.route('/setting/add_pages', methods=['GET','POST'])
def AddPages():
    if request.method == 'GET':
        if LogStatus() :
         return render_template("/setting/add_pages.html")
        return redirect("/logout")
    if request.method == 'POST':
       PageOrder = request.form["PageOrder"]
       PageTitel = request.form["PageTitel"]
       PageIcon = request.form["PageIcon"]
       PageStatus = request.form["PageStatus"]
       PageUrl = request.form["PageUrl"]
       Pages = {
                "PageOrder": PageOrder,
                "PageTitel": PageTitel,
                "PageIcon": PageIcon,
                "PageStatus": PageStatus,
                "PageUrl": PageUrl,
                "PageType": "First",
                "date": datetime.datetime.now()
               }
       LeftMenuDb.insert_one(Pages)
       return redirect("/setting/pages",code=302) 
       
@app.route('/setting/sub_page', methods=['GET','POST'])
def SubPage():
    if request.method == 'GET':
        if LogStatus() :
          ParentPage = request.args.get("parent_page")
          LmSubData = []
          for menu in LeftMenuDb.find() :
             if 'ParentPage' in menu and menu['ParentPage'] == ParentPage :
                menu['date'] = DateFormat(menu['date'], False)
                LmSubData.append(menu)
          return render_template("/setting/sub_page.html", SubMenuJson = LmSubData,PaPage = ParentPage)
        return redirect("/logout")
    if request.method == 'POST':
        mode = request.args.get("mode")
        data = request.args.get("data")
        if mode == "delete" :
           Parent_Page = data.split(",")[1].split(":")[1]
           LeftMenuDb.delete_one({"PageTitel":data.split(",")[0].split(":")[1]})
           return  {"Redirect" : f"/setting/sub_page?parent_page={Parent_Page}","message" : "Deleted Successfully"}
        return redirect(f"/setting/sub_page?parent_page={request.args.get('parent_page')}")
        
@app.route('/setting/add_subpage', methods=['GET','POST'])
def AddSubPages():
    if request.method == 'GET':
        if LogStatus() :
           ParPage = request.args.get("parent_page")
           return render_template("/setting/add_subpage.html",PPage = ParPage) 
        return redirect("/logout")
    if request.method == 'POST':
       ParentPage = request.form["Parentpage"]
       PageOrder = request.form["PageOrder"]
       PageTitel = request.form["PageTitel"]
       PageIcon = request.form["PageIcon"]
       PageStatus = request.form["PageStatus"]
       PageUrl = request.form["PageUrl"]
       Pages = {
                "PageOrder": PageOrder,
                "ParentPage": ParentPage,
                "PageTitel": PageTitel,
                "PageIcon": PageIcon,
                "PageStatus": PageStatus,
                "PageUrl": PageUrl,
                "PageType": "Second",
                "date": datetime.datetime.now()
               }
       LeftMenuDb.insert_one(Pages)
       return redirect(f"/setting/sub_page?parent_page={request.args.get('parent_page')}",code=302) 

@app.route('/setting/Edit_pages', methods=['GET','POST'])
def EditPage():
    if request.method == 'GET':
        if LogStatus() :
          PageTitel =  request.args.get("PageTitel")
          PageIcon =  request.args.get("PageIcon")
          PageStatus =  request.args.get("PageStatus")
          PageUrl =  request.args.get("PageUrl")
          PageOrder =  request.args.get("PageOrder")
          EpBindJson = {
              "PageTitel" : PageTitel,
              "PageIcon" : PageIcon,
              "PageStatus" : PageStatus,
              "PageUrl" : PageUrl,
              "PageOrder" : PageOrder
          }
          return render_template("/setting/Edit_pages.html",EpBindData = EpBindJson)
        return redirect("/logout")
    if request.method == 'POST':
        PPageTitel =  request.form["PageTitel"]
        PPageIcon =  request.form["PageIcon"]
        PPageStatus =  request.form["PageStatus"]
        PPageUrl =  request.form["PageUrl"]
        PPageOrder =  request.form["PageOrder"]
        PPage = {
              "PageTitel" : PPageTitel,
              "PageIcon" : PPageIcon,
              "PageStatus" : PPageStatus,
              "PageUrl" : PPageUrl,
              "PageOrder" : PPageOrder
        }
        OldData = LeftMenuDb.find_one({"PageTitel": request.args.get("PageTitel")})
        LeftMenuDb.update_one(OldData,{"$set": PPage})
        return redirect("/setting/Edit_pages",code=302)

@app.route('/faculty/faculty', methods=['GET'])
def Faculty():
    if request.method == 'GET':
        if "dltId" in request.args:
            UserDb.delete_one({"_id": ObjectId(request.args.get("dltId"))})
        if LogStatus() :
          FacData = []
          for item in UserDb.find({"roll": "Faculty"}) :
              item['date'] = DateFormat(item['date'], False)
              FacData.append(item)
          return render_template("/faculty/faculty.html", FacultyJson = FacData)
        return redirect("/logout")

@app.route('/faculty/add_faculty', methods=['GET','POST'])
def AddFaculty():
    error = None
    if request.method == 'GET':
        if LogStatus() :
           return render_template("/faculty/add_faculty.html") 
        return redirect("/logout")
    if request.method == 'POST':
         user_id = request.form["fid"]
         email = request.form["femail"]
         name = request.form["fname"]
         roll = "Faculty"
         password = request.form["fpassword"]
         gender = request.form["fgender"]
         if 'fimage' in request.files:
            image = request.files["fimage"]
            if image and allowed_file(image.filename):
               filename = secure_filename(image.filename)
              
         if UserDb.find_one({"user_id": user_id}) :
             error = 'User Id alredy exist'
         else :
            post = {"name": name,
                   "email": email,
                   "password": password,
                   "roll": roll,
                   "user_id": user_id,
                   "date": datetime.datetime.now(),
                   "gender": gender,
                   "image": filename
                   }
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))      
            UserDb.insert_one(post)
            return redirect("/faculty/faculty", code=302)     

@app.route('/exams/exam', methods=['GET','POST'])
def Exam():
    error = None
    if request.method == 'GET':
        if LogStatus() :
            if request.args.get("Flag") == "A":
                OldQplst = ExamPaperDb.find_one({'_id' : ObjectId(request.args.get("QpId"))})
                msg = ExamPaperDb.update_one(OldQplst,{"$set": {
                    f"Attend.{session['userid']}" : {
                        "User_Id" : session['userid'],
                        "StartTime": datetime.datetime.now(),
                        "EndTime" : None ,
                        "AttendQsList" : [],
                        "Proctored_img" : []
                    }
                    }})
                return Response(f"/exams/new_exam/{request.args.get('QpId')}")
            UsBranch = UserDb.find_one({"user_id" : session["userid"]})["branch"]
            ExamPapers = ExamPaperDb.find()
            ExamPapersArr = []
            for item in ExamPapers :
                if item['Branch'] == UsBranch :
                   item['CreatedDate'] = DateFormat(item['CreatedDate'], False)
                   if item['StartDate'] != "" :  item['StartDate'] = DateFormat(item['StartDate'], True)
                   if item['EndDate'] != "" :  item['EndDate'] = DateFormat(item['EndDate'], True)
                   ExamPapersArr.append(item)
            return render_template("/exams/exam.html", Qsppr = ExamPapersArr) 
        return redirect("/logout")
    if request.method == 'POST':
         
        return render_template("/exams/exam.html")      

@app.route('/exams/new_exam/<QpId>', methods=['GET','POST'])
def NewExam(QpId):
    print(QpId)
    error = None
    if request.method == 'GET':
        if LogStatus() :
           return render_template("/exams/startexam.html") 
        return redirect("/logout")
    if request.method == 'POST':
         
        return render_template("/exams/startexam.html")      

@app.route('/exams/add_exam', methods=['GET','POST'])
def AddExam():
    error = None
    if request.method == 'GET':
        if LogStatus() :
           BranchDt = BranchDb.find()
           Branch = request.args.get("Branch")
           if Branch != None and Branch != "" :
              FSubjects = SubjectDb.find({"Branch" : Branch})
              SubjectDt = []
              for item in FSubjects :
                  item['_id'] = str(item['_id'])
                  SubjectDt.append(item)   
              return SubjectDt
           return render_template("/exams/add_exam.html" ,BranDt = BranchDt) 
        return redirect("/logout")
    if request.method == 'POST':
       EBranch = request.form["Branch"]
       ESubject = request.form["Subject"]
       EQSPCode = request.form["QSPCode"]
       EQsType= request.form["QsType"]
       EQsCategory= request.form["QsCategory"]
       EQuestion = request.form["Question"]
       EOption1 = request.form["Option1"] if "Option1" in request.form else None
       EOption2 = request.form["Option2"] if "Option2" in request.form else None
       EOption3 = request.form["Option3"] if "Option3" in request.form else None
       EOption4 = request.form["Option4"] if "Option4" in request.form else None
       EQsAnswar = request.form["QsAnswar"] if "QsAnswar" in request.form else None
       EQSCode = f"{EQSPCode}{datetime.datetime.now().strftime('%f')}"
       EQustion = {
           "CreatedDate" : datetime.datetime.now(),
           "Branch" :  EBranch,
           "Subject" : ESubject,
           "QSPCode" : EQSPCode,
           "QSCode" : EQSCode,
           "QsType" :  EQsType,
           "QsCategory" :  EQsCategory,
           "Question" :EQuestion,
           "Option1" : EOption1,
           "Option2" : EOption2,
           "Option3" : EOption3,
           "Option4" : EOption4,
           "QsAnswar" : EQsAnswar
       }
       QuestionDb.insert_one(EQustion)
       return redirect("/exams/add_exam", code=302)     

@app.route('/exams/schedule_exam', methods=['GET','POST'])
def ScheduleExam():
    SuccessMsg = None
    BranchDt = BranchDb.find()
    if request.method == 'GET':
        if LogStatus() :
           if "DltId" in request.args:
            QuestionDb.delete_one({"_id": ObjectId(request.args.get("DltId"))})
            SuccessMsg = "Question Deleted !!!"
            
           Branch = request.args.get("Branch")
           if Branch != None and Branch != "":
              FSubjects = SubjectDb.find({"Branch" : Branch})
              SubjectDt = []
              for item in FSubjects :
                  item['_id'] = str(item['_id'])
                  SubjectDt.append(item)   
              return SubjectDt
           
           Subject = request.args.get("Subject")
           BName = request.args.get("BName")
           if (BName != None and BName != "" ) and (Subject != None and Subject != "" ):
              Qspapers = QuestionDb.find({"Branch" : BName, "Subject" : Subject})
              QSPCodeArr = []
              for item in Qspapers :
                  if QSPCodeArr.count(item["QSPCode"]) == 0 :
                     QSPCodeArr.append(item["QSPCode"])
              return QSPCodeArr
           return render_template("/exams/schedule_exam.html",BranDt = BranchDt, SuccessMsg = SuccessMsg) 
        return redirect("/logout")
    if request.method == 'POST':
        ScBranch = request.form["Branch"]
        ScSubject = request.form["Subject"]
        ScPaperCode = request.form["PaperCode"]
        QsCheckList = request.form["QsCheckDt"]
        if(QsCheckList != "" ):
            QsListDt = {
              "Branch" : ScBranch,
              "Subject" :ScSubject,
              "PaperCode" : ScPaperCode,
              "QuestionList" : QsCheckList.split(","),
              "CreatedDate" : datetime.datetime.now(),
              "StartDate"  : "",
              "EndDate"  : "",
              "Active_Ind"  :  0,
              "Status" : "Pending",
              "QsP_Code" : f"{ScBranch[0 : 2]}{datetime.datetime.now().strftime('%f')}{ScSubject[0 : 2]}",
              "Attend" : {},
              "Max_Hour" : request.form["MHour"],
              "Max_Min" : request.form["MMinute"],
              "Max_Sec" : request.form["MSecond"]
             }
            ExamPaperDb.insert_one(QsListDt)
            return redirect("/papers/paper",code=302)
        if ScPaperCode != None or ScBranch != None or ScSubject != None:
            QsJson = QuestionDb.find({"Branch" : ScBranch, "Subject" : ScSubject, "QSPCode" : ScPaperCode })
            QsJsonArr = []
            for item in QsJson :
              item['CreatedDate'] = DateFormat(item['CreatedDate'], False)
              QsJsonArr.append(item)
            print(QsJsonArr)
            return render_template("/exams/schedule_exam.html", BranDt = BranchDt, QsJson = QsJsonArr)  
        return render_template("/exams/schedule_exam.html", BranDt = BranchDt)     
    
@app.route("/papers/paper",methods=['GET','POST'])
def papers():
    SuccessMsg = None
    BranchList = BranchDb.find()
    SubjectList = SubjectDb.find()
    QsCodeList = QuestionDb.find()
    QsCodetArr = []
    for code in QsCodeList : 
        if {"QSPCode" : code["QSPCode"]} not in QsCodetArr :  QsCodetArr.append({"QSPCode" : code["QSPCode"]})
     
    if request.method == 'GET':
       if LogStatus() :
            if "DltId" in request.args:
                ExamPaperDb.delete_one({"_id": ObjectId(request.args.get("DltId"))})
                SuccessMsg = "QuestionPaper Deleted !!!"

            QspId = request.args.get("QpId")
            Flag = request.args.get("Flag")
            if Flag == "P" : 
                OldQpDt = ExamPaperDb.find_one({"_id" : ObjectId(QspId)})
                ExamPaperDb.update_one(OldQpDt,{"$set": {"Status" : "Ongoing","StartDate": datetime.datetime.now()}})
            if Flag == "O" : 
                OldQpDt = ExamPaperDb.find_one({"_id" : ObjectId(QspId)})
                ExamPaperDb.update_one(OldQpDt,{"$set": {"Status" : "Success","EndDate": datetime.datetime.now()}})


            ExamPapers = ExamPaperDb.find()
            ExamPapersArr = []
            for item in ExamPapers :
                item['CreatedDate'] = DateFormat(item['CreatedDate'], False)
                if item['StartDate'] != "" :  item['StartDate'] = DateFormat(item['StartDate'], True)
                if item['EndDate'] != "" :  item['EndDate'] = DateFormat(item['EndDate'], True)
                ExamPapersArr.append(item)

            return render_template("/papers/paper.html", Qsppr = ExamPapersArr,
                 Message = SuccessMsg, Branchs = BranchList, Subjects = SubjectList, QsCodes = QsCodetArr)
       return redirect("/logout")
    if request.method == 'POST':
        Branch = request.form["Branch"]
        Subject = request.form["Subject"]
        PaperCode = request.form["PaperCode"]
        Query = {}
        if Branch : Query["Branch"] = Branch
        if Subject : Query["Subject"] = Subject
        if PaperCode : Query["PaperCode"] = PaperCode
        if Branch or Subject or PaperCode : 
            ExamPapers = ExamPaperDb.find(Query)
        else : 
            ExamPapers = ExamPaperDb.find()
        ExamPapersArr = []
        for item in ExamPapers :
            item['CreatedDate'] = DateFormat(item['CreatedDate'], False)
            if item['StartDate'] != "" :  item['StartDate'] = DateFormat(item['StartDate'], True)
            if item['EndDate'] != "" :  item['EndDate'] = DateFormat(item['EndDate'], True)
            ExamPapersArr.append(item)
        return render_template("/papers/paper.html", Qsppr = ExamPapersArr,
                           Branchs = BranchList, Subjects = SubjectList, QsCodes = QsCodetArr)

@app.route("/editfac",methods=['GET','POST'])
def Edit():
    if request.method=='GET':
       Uid = request.args.get("id")
       editDt = UserDb.find_one({"_id": ObjectId(Uid)})
       return render_template('editfac.html', EditDt = editDt) 
    
    if request.method=='POST':
       id = request.form['Id']
       updateVal = {
              "_id"  : ObjectId(id),
              "name" : request.form['fname'],
              "email" :request.form['femail'],
              "password" : request.form['fpassword'],
              "user_id"  :request.form['fid'],
              "image" :request.form['fimage'],
              "gender" :request.form['fgender'],
        }
       OldData = UserDb.find_one({"_id": ObjectId(id)})
       UserDb.update_one(OldData,{"$set":updateVal})
       return redirect("/faculty/faculty", code=302)

@app.route("/updatestu",methods=['GET','POST'])
def Update():
    if request.method=='GET':
       Uid = request.args.get("id")
       editDt = UserDb.find_one({"_id": ObjectId(Uid)})
       return render_template('updatestu.html', EditDt = editDt) 
    
    if request.method=='POST':
       id = request.form['Id']
       updateVal = {
              "_id"  : ObjectId(id),
              "name" : request.form['fname'],
              "email" :request.form['femail'],
              "password" : request.form['fpassword'],
              "user_id"  :request.form['fid'],
              "image" :request.form['fimage'],
              "gender" :request.form['fgender'],
        }
       OldData = UserDb.find_one({"_id": ObjectId(id)})
       UserDb.update_one(OldData,{"$set":updateVal})
       return redirect("/student/students", code=302)






if __name__ == "__main__":
   print(__name__)
   app.run(host='0.0.0.0',port=3000,debug=True)