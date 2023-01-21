import PyPDF2
from fpdf import FPDF
import openai
from flask import Flask, redirect, render_template, request, url_for, send_file
from unicodedata import *

openai.api_key = "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"
#extra personality things
#cache 

def genPersonality(input):
    response = openai.Completion.create(
            model="text-davinci-003",
            prompt="Make this into main learning type points(seperated by commas):"+ input,
            temperature=0.7,
            max_tokens = 200,
        )
    personality = str(response.choices[0].text)
    
    return personality


app = Flask(__name__)
#content,name
worksheetsGenerated = []
marks = 0
language = "english"

@app.route("/", methods=("GET", "POST"))
def index():
    return render_template("index.html")

@app.route("/question", methods=("GET", "POST"))
def ques():
    return render_template("ques.html")

@app.route("/personality",methods = ("GET", "POST"))
def pers():
    global user

    if request.method == "POST":
        name ="Name is: "+  str(request.form["name"])
        sex = "Gender is: "+str(request.form["sex"])
        grade = "Grade is: "+str(request.form["grade"])
        like = "They like: " +str(request.form["like"])
        hobby = "Hobby: " + str(request.form["hobby"])
        unlike = "They dont like: " +str(request.form["unlike"])
        favsub = "Their favorite subject is: " + str(request.form["favsub"])
        subst = "The subjects they struggle with are: " + str(request.form["subst"])
        concl = "Their liked concepts: " + str(request.form["concl"])

        strper = name+ " "+sex+" "+grade+" "+like+" "+hobby+" "+unlike+" "+favsub+" "+subst+" "+concl

        user = genPersonality(strper)
        print(user)

    return render_template("index.html")

@app.route("/answer", methods=("GET", "POST"))
def ansques():
    if request.method == "POST":
        ques = request.form["ques"]
        response = responseGen("I have a question (if this is not a valid question return INVALID): "+ques,False)
        return redirect(url_for("ansques", result=response))

    result = request.args.get("result")
    return render_template("ques.html", result=result)

@app.route("/display", methods=("GET", "POST"))
def display():
    return render_template("worksheets.html")


@app.route("/worksheet", methods=("GET", "POST"))
def ws():
    w = 0
    if request.method == "POST":
        ws = request.form["ws"]
        w = createWs(ws)
        w = "static/"+w
        

    return send_file(str(w))

@app.route("/handout", methods=("GET", "POST"))
def hout():
    if request.method == "POST":
        hout = request.form["hout"]
        createHandout(hout)
        return redirect(url_for("hout", result = "Handout Made succesfully!"))

    result = request.args.get("result")
    return render_template("ques.html", result=result)






def changeMarks(change):
    marks = (marks+change)/len(worksheetsGenerated)
    
def responseGen(_prompt, biased):
    response = None
    if(biased == False):
        response = openai.Completion.create(
                model="text-davinci-003",
                prompt="in"+language+":"+_prompt,
                temperature=0.7,
                max_tokens = 3800,
                )
    else:
        response = openai.Completion.create(
                model="text-davinci-003",
                prompt="in"+language+":"+_prompt + "(Keep in mind the user has these qualities:"+user+")",
                temperature=0.7,
                max_tokens = 3800,
            )
    return str(response.choices[0].text)

def createWs(_input):
    
    worksheet = responseGen("Generate a worksheet on this: "+_input+". Add question marks in square brackets. Prohibit giving answers",False)

    lines = worksheet.split("\n")
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Times", size = 10)
    
    pdf.multi_cell(200, 10, worksheet, 0, len(lines))
    name = _input[0:3]+".pdf"

    pdf.output("static/"+name, 'F')
    
    worksheetsGenerated.append([worksheet,name,0])

    return name

def createHandout(_input):
    
    subtopics = responseGen("generate 5 subtopics for "+_input+".Seperate them with commas",False)
    pdf = FPDF()
    pdf.add_page()
        
    pdfText = ""
    tableOfContents = responseGen("Generate A table of contents with these subtopics"+subtopics,False)
    tocLines = tableOfContents.split("\n")
    
    pdf.set_font("Times",'B', size = 13)
    pdf.multi_cell(200, 10, tableOfContents, 0, len(tocLines))
    pdfText += tableOfContents
    subtopics = subtopics.split(",")
    

    pdf.add_page()
    for _subtopic in subtopics:
        pdf.set_font("Times",'B', size = 15)
        pdf.cell(200, 15, _subtopic, ln=1, align="L")
        
        subtopic = responseGen("Elaborate on this subtopic give rich amounts of information:"+_subtopic +" of this topic:"+_input+"Dont use any quotation marks",True)
        lines = subtopic.split("\n")
        
        pdf.set_font("Times", size = 10)

        pdf.multi_cell(200, 10, subtopic, 0, len(lines))
        pdfText += subtopic

    name = _input[0:3]+".pdf"
    name = name.encode('cp1252')
    print(pdfText)
    pdf.output(name, 'F')
    
def percentageObtained(answerScheme, answeredWorksheet):
    response =  responseGen("Grade this worksheet using the answer scheme, return the percentage value:"+answeredWorksheet + "Answer Scheme:"+answerScheme, False)
    response = int(response[0:2].replace("%",""))
    return response

        
    
def generateFeedback(worksheet,answeredWorksheet,answerScheme):
    response = responseGen("Generate constructive feedback for the answers the user gave for this worksheet:"+worksheet,"This is the answer scheme:"+answerScheme+"This is the answers the user gave"+answeredWorksheet, True)
    response.replace("\n","")
    
    return response
def generateAnswerScheme(content):
    return responseGen("Generate an answer Scheme for this worksheet (key points to be present for each answer, marks per question):"+content,False) 

def checkWorksheet(ogworksheetName):
    
    ans = open(ogworksheetName+"_answer.pdf", "rb")
    pdfReader = PyPDF2.PdfReader(ans)
    answeredWorksheet = ""
    
    for i in range(len(pdfReader.pages)):
        text+=(pdfReader.pages[i]).extract_text()

    print(text)
    
    for i in range(len(worksheetsGenerated)):
        if(worksheetsGenerated[i][1] == ogworksheetName):
            index = i
    
    ws = worksheetsGenerated[index]
    
    answerScheme = generateAnswerScheme(ws[0])
    percentageObtained = percentageObtained(answerScheme,answeredWorksheet)
    feedback = generateFeedback(ws[0], answeredWorksheet, answerScheme)
    
    changeMarks(percentageObtained)
    ws[2] = percentageObtained
    
    generatewWsDataPDF(ws[0],answeredWorksheet,answerScheme,feedback,ogworksheetName)
    
    return [percentageObtained,feedback]

def generatewWsDataPDF(ws,ansWs,answerScheme,feedback,wsName):
    pdf = FPDF()
    
    #og ws
    pdf.add_page()
    pdf.set_font("Times",'B', size = 15)
    pdf.cell(200, 15, "Worksheet", ln=1, align="L")
    
    pdf.set_font("Times", size = 10)

    lines = ws.split("\n")
    pdf.multi_cell(200, 10, ws, 0, len(lines))
    
    #userAnswers
    pdf.add_page()
    pdf.set_font("Times",'B', size = 15)
    pdf.cell(200, 15, "Your Answers", ln=1, align="L")
    
    lines = ansWs.split("\n")
    pdf.multi_cell(200, 10, ansWs, 0, len(lines))
    
    #answer scheme
    pdf.add_page()
    pdf.set_font("Times",'B', size = 15)
    pdf.cell(200, 15, "Answer Scheme", ln=1, align="L")
    
    lines = answerScheme.split("\n")
    pdf.multi_cell(200, 10, answerScheme, 0, len(lines))
    
    #feedback
    pdf.add_page()
    pdf.set_font("Times",'B', size = 15)
    pdf.cell(200, 15, "Feedback", ln=1, align="L")
    
    lines = feedback.split("\n")
    pdf.multi_cell(200, 10, feedback, 0, len(lines))
    
    #name
    name = wsName+"WorksheetData.pdf"
    pdf.output(name, 'F')
    return name 
    