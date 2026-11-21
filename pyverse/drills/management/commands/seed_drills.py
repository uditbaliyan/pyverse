"""Create the Drills pages and starter Parsons puzzles (idempotent).

    manage.py seed_drills

Puts /drills/ -> /drills/parsons/ -> topic pages under the site's home page and
upserts the puzzles from ``seed_data``. Existing pages and edits to puzzles'
positions are left alone; puzzle content is refreshed from the seed.
"""

from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from django.utils.text import slugify
from wagtail.models import Site

from pyverse.drills.models import DrillsHubPage
from pyverse.drills.models import DrillTopicPage
from pyverse.drills.models import DrillTypePage
from pyverse.drills.models import ParsonsProblem
from pyverse.drills.seed_data import PUZZLES
from pyverse.drills.seed_data import QUIZ_TOPICS
from pyverse.drills.seed_data import QUIZZES
from pyverse.drills.seed_data import TOPICS
from pyverse.quiz.models import Choice
from pyverse.quiz.models import Question
from pyverse.quiz.models import QuestionType
from pyverse.quiz.models import Quiz


def _child(parent, model, slug, **fields):
    page = parent.get_children().filter(slug=slug).first()
    if page:
        return page.specific
    page = model(slug=slug, **fields)
    parent.add_child(instance=page)
    page.save_revision().publish()
    return page


class Command(BaseCommand):
    help = "Create /drills/ pages and the starter Parsons puzzles."

    def handle(self, *args, **options):
        site = Site.objects.filter(is_default_site=True).first()
        if site is None:
            msg = "no default Wagtail site; run load_content or create one first"
            raise CommandError(msg)
        home = site.root_page.specific
        hub = _child(
            home,
            DrillsHubPage,
            "drills",
            title="Drills",
            intro="Short, focused question sets grouped by topic. Pick a type, then a topic.",
        )
        parsons = _child(
            hub,
            DrillTypePage,
            "parsons",
            title="Parsons Puzzles",
            kind=DrillTypePage.Kind.PARSONS,
            intro="Arrange shuffled lines of code, with the right indentation, into a working program.",
        )
        topics = {
            key: _child(parsons, DrillTopicPage, key, title=title)
            for key, title in TOPICS.items()
        }
        for position, item in enumerate(PUZZLES):
            problem, _ = ParsonsProblem.objects.get_or_create(
                slug=item["slug"] or slugify(item["title"]),
                defaults={"title": item["title"], "position": position},
            )
            problem.title = item["title"]
            problem.topic = topics[item["topic"]]
            problem.concept = item["concept"]
            problem.difficulty = item["difficulty"]
            problem.description = item["description"]
            problem.expected_output = item["expected_output"]
            problem.lines = [
                (
                    "line",
                    {
                        "text": text,
                        "indent": indent,
                        "is_distractor": distractor,
                        "feedback": feedback,
                    },
                )
                for text, indent, distractor, feedback in item["lines"]
            ]
            problem.save()
        self._seed_quizzes(hub)
        self.stdout.write(
            self.style.SUCCESS(
                f"{len(PUZZLES)} puzzles in {len(topics)} topics; "
                f"{len(QUIZZES)} quiz sets",
            ),
        )

    def _seed_quizzes(self, hub):
        quiz_type = _child(
            hub,
            DrillTypePage,
            "quiz",
            title="Quiz",
            kind=DrillTypePage.Kind.QUIZ,
            intro="Short questions with instant answers and explanations.",
        )
        topics = {
            key: _child(quiz_type, DrillTopicPage, key, title=title)
            for key, title in QUIZ_TOPICS.items()
        }
        for item in QUIZZES:
            quiz, _ = Quiz.objects.get_or_create(
                slug=item["slug"],
                defaults={"title": item["title"]},
            )
            quiz.title = item["title"]
            quiz.drill_topic = topics[item["topic"]]
            quiz.save()
            quiz.questions.all().delete()  # the seed owns these questions
            for order, (kind, text, code, why, answer) in enumerate(item["questions"]):
                is_tf = kind == "tf"
                question = Question.objects.create(
                    quiz=quiz,
                    sort_order=order,
                    question_type=QuestionType.TRUE_FALSE
                    if is_tf
                    else QuestionType.MCQ,
                    text=text,
                    code_snippet=code,
                    explanation=why,
                    correct_bool=answer if is_tf else None,
                )
                if not is_tf:
                    for position, (choice, correct) in enumerate(answer):
                        Choice.objects.create(
                            question=question,
                            sort_order=position,
                            text=choice,
                            is_correct=correct,
                        )
