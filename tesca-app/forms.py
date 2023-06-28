from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    TextAreaField,
    SubmitField,
    IntegerField,
    BooleanField,
    SelectField,
    SelectMultipleField,
    DateTimeField,
    MultipleFileField,
    FileField
)
from wtforms.validators import DataRequired, Length, NumberRange


class ConfigForm(FlaskForm):
    name = StringField("Analyst Name", validators=[DataRequired()])
    scenario = StringField("Scenario Name", validators=[DataRequired()])
    description = TextAreaField("Description")
    # fetch_demographics = BooleanField("Fetch Demographics", [], default=True)
    fetch_demographics = SelectField("Fetch Demographics", choices=[("yes", "Yes"), ("no", "No")], default="yes")
    infinity = IntegerField("Infinity Value (minutes)", validators=[DataRequired(), NumberRange(min=0)], default=180)
    max_time_walking = IntegerField(
        "Max Walking Time (minutes)", validators=[DataRequired(), NumberRange(min=0)], default=30
    )

    block_groups = FileField("Block Groups", validators=[DataRequired()])
    demographics = FileField("Demographics File")
    opportunities = FileField("Opportunities File")
    osm = FileField("OpenStreetMap PBF")

    scenario1_name = StringField("Scenario Name", validators=[DataRequired()])
    scenario1_start = DateTimeField("Start Date & Time (YYYY-MM-DD HH:MM)", validators=[DataRequired()])
    scenario1_duration = IntegerField(
        "Duration (minutes)", validators=[DataRequired(), NumberRange(min=0)], default=120
    )
    scenario1_modes = SelectMultipleField(
        "Travel Modes",
        choices=[("TRANSIT", "All Modes"), ("BUS", "Bus"), ("SUBWAY", "Subway"), ("FUNICULAR", "Funicular")],
        default=["TRANSIT"],
    )
    scenario1_gtfs = MultipleFileField("GTFS Files")

    scenario2_name = StringField("Scenario Name", validators=[DataRequired()])
    scenario2_start = DateTimeField("Start Date & Time (YYYY-MM-DD HH:MM)", validators=[DataRequired()])
    scenario2_duration = IntegerField(
        "Duration (minutes)", validators=[DataRequired(), NumberRange(min=0)], default=120
    )
    scenario2_modes = SelectMultipleField(
        "Travel Modes",
        choices=[("TRANSIT", "All Modes"), ("BUS", "Bus"), ("SUBWAY", "Subway"), ("FUNICULAR", "Funicular")],
        default=["TRANSIT"],
    )
    scenario2_gtfs = MultipleFileField("GTFS Files")

    submit = SubmitField("Submit")
