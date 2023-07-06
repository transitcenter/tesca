from flask_wtf import FlaskForm

from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import (
    Form,
    StringField,
    TextAreaField,
    SubmitField,
    IntegerField,
    SelectField,
    SelectMultipleField,
    DateTimeField,
    MultipleFileField,
    FieldList,
    FormField,
    HiddenField,
)

from wtforms.validators import DataRequired, Length, NumberRange


class OpportunityMeasureForm(Form):
    prettyname = StringField("Opportunity Name", validators=[DataRequired()])
    method = SelectField(
        "Computation Method",
        choices=[("cumulative", "Cumulative"), ("travel_time", "Travel Time to nth Closest")],
        default="c",
    )
    parameters = StringField("Parameters (comma separated)", validators=[DataRequired()], default="30,45")
    opportunity = HiddenField()


# class OpportunityConfigForm(Form):
#     opportunities = FieldList(FormField(OpportunityMeasureForm), min_entries=1)


class OpportunitiesUploadForm(FlaskForm):
    file = FileField(
        "Opportunities File",
        validators=[FileRequired("Gotta have a file"), FileAllowed(["csv"], "Must be a CSV")],
    )
    submit = SubmitField("Start")


class ConfigForm(FlaskForm):
    analyst = StringField("Analyst Name", validators=[DataRequired()], default="Your Name Here")
    project = StringField("Scenario Name", validators=[DataRequired()], default="Test Project")
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

    scenario0_name = StringField("Scenario Name", validators=[DataRequired()], default="Scenario A")
    scenario0_start = DateTimeField(
        "Start Date & Time (YYYY-MM-DD HH:MM)", format="%Y-%m-%d %H:%M", validators=[DataRequired()]
    )
    scenario0_duration = IntegerField(
        "Duration (minutes)", validators=[DataRequired(), NumberRange(min=0)], default=120
    )
    scenario0_modes = SelectMultipleField(
        "Transit Modes",
        choices=[
            ("TRANSIT", "All Modes"),
            ("BUS", "Bus"),
            ("SUBWAY", "Subway"),
            ("TRAM", "Tram/Streetcar"),
            ("RAIL", "Rail"),
            ("FERRY", "Ferry"),
            ("CABLE_CAR", "Cable Car"),
            ("GONDOLA", "Gondola"),
            ("FUNICULAR", "Funicular"),
        ],
        default=["TRANSIT"],
    )
    scenario0_gtfs = MultipleFileField("GTFS Files", validators=[DataRequired()])

    scenario1_name = StringField("Scenario Name", validators=[DataRequired()], default="Scenario B")
    scenario1_start = DateTimeField(
        "Start Date & Time (YYYY-MM-DD HH:MM)", format="%Y-%m-%d %H:%M", validators=[DataRequired()]
    )
    scenario1_duration = IntegerField(
        "Duration (minutes)", validators=[DataRequired(), NumberRange(min=0)], default=120
    )
    scenario1_modes = SelectMultipleField(
        "Transit Modes",
        choices=[
            ("TRANSIT", "All Modes"),
            ("BUS", "Bus"),
            ("SUBWAY", "Subway"),
            ("TRAM", "Tram/Streetcar"),
            ("RAIL", "Rail"),
            ("FERRY", "Ferry"),
            ("CABLE_CAR", "Cable Car"),
            ("GONDOLA", "Gondola"),
            ("FUNICULAR", "Funicular"),
        ],
        default=["TRANSIT"],
    )
    scenario1_gtfs = MultipleFileField("GTFS Files", validators=[DataRequired()])

    submit = SubmitField("Set Up Analysis and Validate")
