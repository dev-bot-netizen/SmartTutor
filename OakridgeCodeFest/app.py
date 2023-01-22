import PyPDF2
from fpdf import FPDF
import openai
from flask import Flask, redirect, render_template, request, url_for, send_file
from unicodedata import *
from fileinput import filename
import re
import math

openai.api_key = "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"
global user
user = ''

#content,name, worksheetDataName
worksheetsGenerated = []

worksheetNames = []
language = "urdu"
global marks
marks = 0

#to do for akki
#extra personality textbox
#cache personality inputs and load next time user opens website
#remove the hard coded scroll view items
# remove the hard coded current ws displau
#submit ws button functionality
#communication
#name of site
#laungeage personalization

#me
#implement hindi chars
#test grading ws 
#format ws data
#text recog

global w;
w = 0

app = Flask(__name__)

@app.route("/", methods=("GET", "POST"))
def index():
    return render_template("index.html",score = marks)

@app.route("/question", methods=("GET", "POST"))
def ques():
    return render_template("ques.html",score = marks)
    
@app.route("/display", methods=("GET", "POST"))
def display():
    
    return render_template("worksheets.html",list = worksheetNames[-1],score = marks)

@app.route("/personality",methods = ("GET", "POST"))
def pers():

    global language
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
        language = str(request.form["lang"])
        strper = name+ " "+sex+" "+grade+" "+like+" "+hobby+" "+unlike+" "+favsub+" "+subst+" "+concl
        
        genPersonality(strper)
        print(user)

    return render_template("index.html",score = marks)

@app.route("/answer", methods=("GET", "POST"))
def ansques():
    if request.method == "POST":
        ques = request.form["ques"]
        response = responseGen("I have a question (if this is not a valid question return INVALID): "+ques,False)
        return redirect(url_for("ansques", result=response))

    result = request.args.get("result")
    return render_template("ques.html", result=result,score = marks)

@app.route("/submit", methods=["POST"])
def submit():
    if request.method == "POST":
        title = worksheetsGenerated[-1][1]
        title = title.replace(".pdf","")
        file = request.files["file"]
        file.save(title+"_answer.pdf")
        checkWorksheet(title)
        return render_template("index.html",result = file.filename,score = marks)


@app.route("/worksheet", methods=("GET", "POST"))
def ws():
    if request.method == "POST":
        global w
        ws = request.form["ws"]
        w = createWs(ws)
        w = "static/"+w
        

    return send_file(str(w))

@app.route("/displayws")
def displayws():
    global w
    print("\n\n\n\n", w, "Lmao\n\n\n\n\n")
    return send_file(str(w))
    

@app.route("/handout", methods=(["POST", "GET"]))
def hout():
    hout = ''
    if request.method == "POST":
        hout = str(request.form["hout"])
        createHandout(hout)
        name = "static/"+hout[0:3]+".pdf"
        return send_file(name )
    
    return redirect(url_for("hout", result = "Handout Made succesfully!"))

    




#----------------------------------------------------------------------------------------------------------------------------#



def percentageObtained(answerScheme, answeredWorksheet):
    response =  responseGen("Grade this worksheet using the answer scheme, return only a percentage value without the percentage charecter in square brackets:"+answeredWorksheet + "\nAnswer Scheme:"+answerScheme, False, tokens=3400)
    value = 0
    
    match = re.search(r'\[(.*?)\]', response)
    if match:
        value = match.group(1)
        print("\n\n\n"+value+"\n\n\n")

    
    return math.floor(int(value))

def generateAnswerScheme(content):
    return responseGen("Generate an answer Scheme for this worksheet (key points to be present for each answer, marks per question):"+content,False,tokens=3400) 

def generateFeedback(answeredWorksheet,answerScheme):
    response = responseGen("Generate feedback for the user answer using the answer scheme to check the answers. User answer:"+ answeredWorksheet+"\nAnswer Scheme: "+answerScheme, True,tokens = 3400)
    response.replace("\n","")
    return response


def genPersonality(input):
    response = openai.Completion.create(
            model="text-davinci-003",
            prompt="Make this into main learning type points(seperated by commas):"+ input,
            temperature=0.7,
            max_tokens = 200,
        )
    personality = str(response.choices[0].text)
    global user
    user = personality



def changeMarks(change):
    global marks
    marks = (int(marks)+int(change))/len(worksheetsGenerated)
    
def responseGen(_prompt, biased,tokens = 3800, frequency = 1, presence = 1):
    response = None
    if(biased == False):
        response = openai.Completion.create(
                model="text-davinci-003",
                prompt="in"+language+" script:"+_prompt,
                temperature=0.7,
                max_tokens = tokens,
                top_p = 1,
                frequency_penalty = frequency,
                presence_penalty = presence,
                )
    else:
        response = openai.Completion.create(
                model="text-davinci-003",
                prompt="in"+language+" script:"+_prompt + "(Keep in mind the user has these qualities:"+user+")",
                temperature=0.7,
                max_tokens = tokens,
                top_p = 1,
                frequency_penalty = 1,
                presence_penalty = 1,
            )
    return str(response.choices[0].text)

def createWs(_input):
    print(_input)
    worksheet = responseGen("Create a worksheet on the topic of:"+ _input+" include instructions,topic, name and date on top, min 5 questions, enough space under to answer the question, and DO NOT ANSWER THE QUESTIONS.",False,3800,0,0)
    
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font('NotoSans', '', 'static/NotoSans-Black.ttf', uni=True)
    pdf.set_font('NotoSans', '', 14)

    
    pdf.write(10, worksheet)
    name = _input[0:3]+".pdf"

    pdf.output("static/"+name, 'F')
    
    worksheetsGenerated.append([worksheet,name,""])
    worksheetNames.append(name)
    return name

def createHandout(_input):
    subtopics = responseGen("generate 5 subtopics for "+_input+".Seperate them with commas",False)
    pdf = FPDF()
    pdf.add_font('NotoSans', '', 'static/NotoSans-Black.ttf', uni=True)
    pdf.set_font('NotoSans', '', 14)
    pdf.add_page()
        
    tableOfContents = responseGen("Generate A table of contents with these subtopics"+subtopics,False)
    tocLines = tableOfContents.split("\n")
    
    
    pdf.multi_cell(200, 10, tableOfContents, 0, len(tocLines))
    
    subtopics = subtopics.split(",")
    

    pdf.add_page()
    for _subtopic in subtopics:
        pdf.set_font('NotoSans', '', 13)
        
        pdf.cell(200, 15, _subtopic, ln=1, align="L")
        
        subtopic = responseGen("Elaborate on this subtopic to give rich amounts of information:"+_subtopic +" of this topic:"+_input,True)
        
        pdf.set_font('NotoSans', '', 10)

        pdf.write(10, subtopic)
        pdf.ln()
    name = _input[0:3]+".pdf"
    pdf.output("static/"+name, 'F')
    

def generatewWsDataPDF(ws,ansWs,answerScheme,feedback,wsName, percentage):
    pdf = FPDF()
    
    #userAnswers
    pdf.add_page()
    pdf.add_font('NotoSans', '', 'static/NotoSans-Black.ttf', uni=True)
    pdf.set_font('NotoSans', '', 14)
    pdf.cell(200, 15, "Worksheet. You got "+str(percentage)+"%", ln=1, align="L")
    
    lines = ansWs.split("\n")
    pdf.multi_cell(200, 10, ansWs, 0, len(lines))
        
    #answer scheme
    pdf.add_page()
    pdf.cell(200, 15, "Answer Scheme", ln=1, align="L")
    
    lines = answerScheme.split("\n")
    pdf.multi_cell(200, 10, answerScheme, 0, len(lines))
    
    #feedback
    pdf.add_page()
    pdf.cell(200, 15, "Feedback", ln=1, align="L")
    
    lines = feedback.split("\n")
    pdf.multi_cell(200, 10, feedback, 0, len(lines))
    
    #name
    name = wsName.replace(".pdf","")+"Data.pdf"
    pdf.output("static/"+name, 'F')
    return name 

def checkWorksheet(ogworksheetName):
    
    ans = open(ogworksheetName+"_answer.pdf", "rb")
    pdfReader = PyPDF2.PdfReader(ans)
    answeredWorksheet = ""
    

    for i in range(len(pdfReader.pages)):
        answeredWorksheet+=(pdfReader.pages[i]).extract_text()

    print(answeredWorksheet)
    
    ws = worksheetsGenerated[-1]
    
    answerScheme = generateAnswerScheme(ws[0])
    percentObtained = percentageObtained(answerScheme,answeredWorksheet)
    feedback = generateFeedback(answeredWorksheet, answerScheme)
    
    changeMarks(percentObtained)
    ws[2] = ogworksheetName.replace(".pdf","")+"Data.pdf"
    
    generatewWsDataPDF(ws[0],answeredWorksheet,answerScheme,feedback,ogworksheetName, percentObtained)
    
    return [percentObtained,feedback]



