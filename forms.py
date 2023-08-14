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
    details = TextAreaField("Opportunity Description", default="A test")
    unit = StringField(
        "Unit of Measure (e.g. jobs)",
        validators=[DataRequired()],
    )
    parameters = StringField("Parameters (comma separated)", validators=[DataRequired()], default="30,45")
    opportunity = HiddenField()


class OpportunitiesUploadForm(FlaskForm):
    file = FileField(
        "Opportunities File",
        validators=[FileRequired("Gotta have a file"), FileAllowed(["csv"], "Must be a CSV")],
    )
    submit = SubmitField("Start")


class ConfigForm(FlaskForm):
    analyst = StringField("Analyst Name", validators=[DataRequired()], default="Your Name Here")
    project = StringField("Project Title", validators=[DataRequired()], default="Project Name Here")
    description = TextAreaField("Project Description", default="")
    organization = StringField("Organization", validators=[DataRequired()], default="Your Organization Here")
    # infinity = IntegerField("Infinity Value (minutes)", validators=[DataRequired(), NumberRange(min=0)], default=180)
    # max_time_walking = IntegerField(
    #     "Maximum Walking Time (minutes)", validators=[DataRequired(), NumberRange(min=0)], default=30
    # )

    osm = FileField("OpenStreetMap Data (PBF)", validators=[FileRequired(), FileAllowed(["pbf"])])
    impact_area = FileField("Impact Area (CSV)", validators=[FileRequired(), FileAllowed(["csv"])])

    opportunities = FieldList(FormField(OpportunityMeasureForm), min_entries=1)

    scenario0_name = StringField("Scenario Name", validators=[DataRequired()], default="Scenario A")
    scenario0_description = TextAreaField("Scenario Description")
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
    scenario1_description = TextAreaField("Scenario Description")
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
