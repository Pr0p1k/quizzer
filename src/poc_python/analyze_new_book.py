from src.poc_python import mem
from quiz.chapters import SubChapter
from quiz.questions import Question, OptionQuestion
from quiz.quiz import Quiz
from src.poc_python.markup_splitter import split_markup_text
from src.poc_python.output_utils import get_output, split_outline_list
from src.poc_python.ui.cli.quiz_cli import QuizCliUi


@mem.cache()
def generate_markup(text: str) -> dict:
    # get LLM lazily TODO think about where to get it and should it be a param
    return {"choices": [{"text": "1. aboba\n2. kek\n 3. sees"}]}


@mem.cache()
def generate_key_points(subject: str, topic_content: str, amount: int) -> dict:
    # get LLM lazily
    return {"choices": [{"text": "1. aboba\n2. kek\n 3. sees"}]}


@mem.cache()
def generate_question(topic_content: str, key_point: str, question_type: str) -> dict:
    # get LLM lazily
    return {"choices": [{"text": """
    {
  "type": "OptionQuestion",
  "question": "What type of government does Serbia have?",
  "options": [
    "Monarchy",
    "Presidential republic",
    "Parliamentary republic",
    "Dictatorship"
  ],
  "correct_answer": 2
}
    """}]}

# TODO change text: str to some local type. Can later be pdf, video, etc. Need to create processors per type
# TODO should it be cached?
def generate_full_quiz(text: str) -> Quiz: # TODO add some params
    markup_output = generate_markup(text) # TODO bypass the cache

    chapter_tuples = split_markup_text(get_output(markup_output)) # TODO

    chapters = [] # TODO name

    for chapter in chapter_tuples:
        amount = 10 # TODO set the amount as a global var
        key_points_output = generate_key_points(chapter[0], chapter[1], amount) # TODO class structure for chapter,

        key_points_per_topic = split_outline_list(get_output(key_points_output))

        questions = []

        for point in key_points_per_topic: # TODO possibly yield asynchronously, so can use the output while it's yet in progress
            question_dict = generate_question(chapter[1], point, "OptionQuestion")
            question = Question.from_json_str(get_output(question_dict))
            questions.append(question)

        chapter_obj = SubChapter(chapter[0], chapter[1], questions)
        chapters.append(chapter_obj)

    return Quiz("Aboba", chapters)


quiz = generate_full_quiz("aboba")

QuizCliUi(quiz).start_quiz()
