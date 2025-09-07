I am building a project:
AI-Powered Content Repurposing & Localization
Build a system that auto-transforms existing content (lectures, case studies, assignments) into multiple formats—short-form, regional languages, interactive quizzes—without requiring manual rework.

In this project I will only create flask based api's


My DB info:

mongodb+srv://naveen:sahayakpassdb@study.ifzehng.mongodb.net/?retryWrites=true&w=majority&appName=study
collection.database = study.info

For Auth:
there will be username and password jwt token based auth before any futher processing

To take User Input / create new content:
/api/upload
input: type, content(video, pdf or text)

It can be a video, pdf or text 
request will specify the type and the content

for video it will generate transcribe and then use AI to generated a well structured and detailed content
for document ans text it will use its text and search on web if required along with AI to generated a well structured and detailed content
then backend will store it in db with userid, contentid, content and title.

To get all content of that user:
api/list
from userid show all the content for that user.

To get summary:
api/summary, language
input: contentid
generate a summary of a content for that user.


To get summary:
api/summary
input: contentid, language
max question: 50
user input: number of question (if none then any number of questions will work according to the size/detail of content under max question)
generate a quiz from the content for that user.
return proper json format.

To get notes:
api/notes
input: contentid, language
generate well detail and easy to read stuctured notes from the content for that user.
return proper json format.

use genimi api for LLM calls
You need to create backend service which handle all this + testing for all api calls + short document for sample input and output format ask even if you have small doubt.