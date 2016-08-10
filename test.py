import surveyhelper as sh

survey = sh.QsfParser("data/CNBC_TV_and_Media_Study_-_USA.qsf")
codebook = survey.create_codebook()
codebook.pretty_print()
for qid, qtype in codebook.questions.items():
    print(qid, qtype)
#import ipdb; ipdb.set_trace()
# for label in ['Q1', 'Q2', 'Q3']:
#     c.questions[label].exclude_choices_from_analysis(['Not applicable'])

# for label in ['Q2', 'Q3']:
#     c.questions[label].change_scale('ordinal')

# c.questions['Q1'].reverse_choices()
# c.questions['Q1'].change_midpoint(2)

# # Remove initial numbering from question text
# for label, q in c.questions.items():
#     q.text = re.sub(r'[0-9]\. ','', q.text)


#r = sh.ResponseSet("sample_input_files/Sample_Senior_Survey.csv", c)
#f = sh.FrequencyReport(r, 'sample_input_files/config.yml')
#f.create_report("output/d3/d3_frequency_report.html")
