"""
FrequencyReport
--------
Provides utilities for producing a survey frequency report.
"""

from jinja2 import Environment, FileSystemLoader
import yaml, math
from itertools import compress
from unidecode import unidecode
from surveyhelper.question import SelectQuestion, SelectOneMatrixQuestion

class FrequencyReport:

    def __init__(self, response_set, config_file):
        with open(config_file, 'r') as ymlfile:
            cfg = yaml.load(ymlfile)

        self.template_dir = cfg['output']['template_dir']
        self.freq_template = cfg['output']['template_file']
        self.report_file = cfg['output']['report_file']
        self.report_title = cfg['report_data']['title']
        self.response_set = response_set

    def create_report(self,
                      sort_by_mean=False,
                      mark_sig_diffs=False):
        env = Environment(loader=FileSystemLoader(self.template_dir),
                  extensions=['jinja2.ext.with_'])
        template = env.get_template(self.freq_template)
        outfile = open(self.report_file, 'w+')
        
        matched_questions = self.response_set.matched_questions
        data_groups = self.response_set.get_data()

        if len(data_groups) > 1:
            questions = self.grouped_questions_data(matched_questions, 
                                                    data_groups, 
                                                    sort_by_mean,
                                                    mark_sig_diffs)
        else:
            questions = self.ungrouped_questions_data(matched_questions, 
                                                      self.response_set.data,
                                                      sort_by_mean)
        t = template.render(count=len(self.response_set.data),
                            survey_title=self.report_title,
                            questions=questions)
        outfile.write(unidecode(t))


    def ungrouped_questions_data(self, matched_questions, data, sort_by_mean):
        questions = []
        for q in matched_questions:
            scale = q.get_scale()
            if scale and hasattr(scale, 'midpoint'):
                midpoint = scale.midpoint
            else:
                midpoint = None

            # If this is a matrix question with more than 7 choices, split it
            # into multiple questions
            if (isinstance(q, SelectOneMatrixQuestion) and len(q.get_scale().choices) > 7):
                barheight = math.floor(min(800 / len(q.get_scale().choices), 30))
                for s in q.questions:
                    table = s.freq_table_to_json(data)
                    group_names = ['']
                    text = "{} &mdash; {}".format(q.text, s.text)
                    questions.append((
                        text,
                        [table],
                        [table],
                        group_names,
                        s.graph_type(1),
                        midpoint,
                        barheight
                    ))                  
            else:
                j = q.freq_table_to_json(data)
                if j != '':
                    questions.append((
                                    q.text,
                                    [j],
                                    [j],
                                    [''],
                                    q.graph_type(1),
                                    midpoint,
                                    40
                    ))
        return(questions)

    def grouped_questions_data(self, matched_questions, data_groups, 
                               sort_by_mean, mark_sig_diffs):
        questions = []
        for q in matched_questions:
            scale = q.get_scale()
            if scale and hasattr(scale, 'midpoint'):
                midpoint = scale.midpoint
            else:
                midpoint = None

            # If we have a lot of comparison groups or questions in the 
            # matrix, break the graph into multiple graphs
            if isinstance(q, SelectOneMatrixQuestion) and ((len(data_groups) * 
                len(q.questions)) > 36):
                for sub_q in q.questions:
                    table = sub_q.cut_by_json(self.response_set, 
                                              sort_by_mean=sort_by_mean,
                                              mark_sig_diffs=mark_sig_diffs)
                    if table != '':
                        text = "{} &mdash; {}".format(q.text, sub_q.text)
                        questions.append((
                            text,
                            [table],
                            [table],
                            [''],
                            q.graph_type(len(data_groups)),
                            midpoint,
                            30
                        ))
            # If this is a matrix question with more than 7 answer choices, split it
            # into multiple questions
            elif (isinstance(q, SelectOneMatrixQuestion) and len(q.get_scale().choices) > 7):
                barheight = math.floor(min(800 / len(q.get_scale().choices), 30))
                for s in q.questions:
                    table = s.cut_by_json(self.response_set, 
                                          sort_by_mean=sort_by_mean,
                                          mark_sig_diffs=mark_sig_diffs)
                    if table != '':
                        group_names = [n for n, df in data_groups]
                        text = "{} &mdash; {}".format(q.text, s.text)
                        questions.append((
                            text,
                            [table],
                            [table],
                            group_names,
                            s.graph_type(len(data_groups)),
                            midpoint,
                            barheight
                        ))
            elif isinstance(q, SelectQuestion) and len(q.get_scale().choices) > 7:
                group_names = []
                json = []
                tables = []
                for name, df in data_groups:
                    j = q.freq_table_to_json(df)
                    if j != '':
                        group_names.append(name)
                        json.append(j)
                        tables.append(j)
                if len(tables) > 0:
                    questions.append((
                                    q.text,
                                    tables,
                                    json,
                                    group_names,
                                    q.graph_type(1),
                                    midpoint,
                                    30
                    ))
            else:
                freq_tables = []
                freq_table_json = []
                group_names = []
                # Matrix question (potentially with groups) that doesn't need
                # to be split apart
                if isinstance(q, SelectOneMatrixQuestion):
                    j = q.cut_by_json(self.response_set, 
                                      sort_by_mean=sort_by_mean,
                                      mark_sig_diffs=mark_sig_diffs)
                    if j != '':
                        freq_tables.append(j)
                        freq_table_json.append(j)
                        group_names.append('')
                    barheight = math.floor(min(800 / ((len(data_groups) * len(q.questions))), 40))
                # Select question with some cut variable
                elif isinstance(q, SelectQuestion):
                    table = q.cut_by_json(self.response_set, 
                                          sort_by_mean=sort_by_mean,
                                          mark_sig_diffs=mark_sig_diffs)
                    if table != '':
                        freq_tables.append(table)
                        freq_table_json.append(table)
                        group_names.append('')
                    barheight = math.floor(min(800 / len(data_groups), 40))

                if len(freq_tables) > 0:
                    questions.append((
                                    q.text,
                                    freq_tables,
                                    freq_table_json,
                                    group_names,
                                    q.graph_type(len(data_groups)),
                                    midpoint,
                                    barheight
                                    ))
        return(questions)


