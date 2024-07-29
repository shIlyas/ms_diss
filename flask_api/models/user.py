
from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(70), nullable = True)
    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"
    
class AssistantScenario(db.Model):
    __tablename__ = 'assistant_scenarios'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    scenario_text = db.Column(db.Text, nullable=False)
    additional_instructions = db.Column(db.Text, nullable=False)
    enable = db.Column(db.Boolean, default=True, nullable=False)

    def __init__(self, scenario_text, additional_instructions, enable=True):
        self.scenario_text = scenario_text
        self.additional_instructions = additional_instructions
        self.enable = enable

    def __repr__(self):
        return f"<AssistantScenario {self.id}>"

    def enable_scenario(self):
        self.enable = True
        db.session.commit()

    def disable_scenario(self):
        self.enable = False
        db.session.commit()

class RubricQuestion(db.Model):
    __tablename__ = 'rubric_questions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question = db.Column(db.Text, nullable=False)
    scenario_id = db.Column(db.Integer, db.ForeignKey('assistant_scenarios.id'), nullable=False)

    scenario = db.relationship('AssistantScenario', backref=db.backref('rubric_questions', lazy=True))

    def __init__(self, question, scenario_id):
        self.question = question
        self.scenario_id = scenario_id

    def __repr__(self):
        return f"<RubricQuestion {self.id}: {self.question}>"
