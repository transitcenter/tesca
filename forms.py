from flask_wtf import FlaskForm

from flask_wtf.file import FileField, FileAllowed, FileRequired
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
    FieldList,
    FormField,
    HiddenField,
)

from wtforms.validators import DataRequired, Length, NumberRange


class OpportunityMeasureForm(FlaskForm):
    prettyname = StringField("Opportunity Name", validators=[DataRequired()])
    method = SelectField(
        "Computation Method", choices=[("c", "Cumulative"), ("t", "Travel Time to nth Closest")], default="c"
    )
    parameters = StringField("Parameters (comma separated)", validators=[DataRequired(), NumberRange(min=1)])
    opportunity = HiddenField()


class OpportunityConfigForm(FlaskForm):
    opportunities = FieldList(FormField(OpportunityMeasureForm), min_entries=1)


class OpportunitiesUploadForm(FlaskForm):
    file = FileField(
        "Opportunities File",
        validators=[FileRequired("Gotta have a file"), FileAllowed(["csv"], "Must be a CSV")],
    )
    submit = SubmitField("Start")


class ConfigForm(FlaskForm):
    analyst = StringField("Analyst Name", validators=[DataRequired()])
    project = StringField("Scenario Name", validators=[DataRequired()])
    description = TextAreaField("Description", default="")
    # fetch_demographics = BooleanField("Fetch Demographics", [], default=True)
    fetch_demographics = SelectField("Fetch Demographics", choices=[("yes", "Yes"), ("no", "No")], default="yes")
    infinity = IntegerField("Infinity Value (minutes)", validators=[DataRequired(), NumberRange(min=0)], default=180)
    max_time_walking = IntegerField(
        "Max Walking Time (minutes)", validators=[DataRequired(), NumberRange(min=0)], default=30
    )

    # block_groups = FileField("Block Groups", validators=[DataRequired()])
    # demographics = FileField("Demographics File")
    # opportunities = FileField("Opportunities File")
    osm = FileField("OpenStreetMap Data (PBF)", validators=[FileRequired(), FileAllowed(["pbf"])])
    impact_area = FileField("Impact Area (CSV)", validators=[FileRequired(), FileAllowed(["csv"])])

    opportunities = FieldList(FormField(OpportunityMeasureForm), min_entries=1)

    scenario0_name = StringField("Scenario Name", validators=[DataRequired()])
    scenario0_start = DateTimeField(
        "Start Date & Time (YYYY-MM-DD HH:MM)", format="%Y-%m-%d %H:%M", validators=[DataRequired()]
    )
    scenario0_duration = IntegerField(
        "Duration (minutes)", validators=[DataRequired(), NumberRange(min=0)], default=120
    )
    scenario0_modes = SelectMultipleField(
        "Transit Modes",
        choices=[("TRANSIT", "All Modes"), ("BUS", "Bus"), ("SUBWAY", "Subway"), ("FUNICULAR", "Funicular")],
        default=["TRANSIT"],
    )
    scenario0_gtfs = MultipleFileField("GTFS Files", validators=[FileRequired()])

    scenario1_name = StringField("Scenario Name", validators=[DataRequired()])
    scenario1_start = DateTimeField(
        "Start Date & Time (YYYY-MM-DD HH:MM)", format="%Y-%m-%d %H:%M", validators=[DataRequired()]
    )
    scenario1_duration = IntegerField(
        "Duration (minutes)", validators=[DataRequired(), NumberRange(min=0)], default=120
    )
    scenario1_modes = SelectMultipleField(
        "Transit Modes",
        choices=[("TRANSIT", "All Modes"), ("BUS", "Bus"), ("SUBWAY", "Subway"), ("FUNICULAR", "Funicular")],
        default=["TRANSIT"],
    )
    scenario1_gtfs = MultipleFileField("GTFS Files", validators=[FileRequired()])

    submit = SubmitField("Set Up Analysis and Validate")
