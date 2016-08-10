import surveyhelper as sh

survey = sh.QsfParser("data/CNBC_TV_and_Media_Study_-_USA.qsf")
codebook = survey.create_codebook()
#codebook.pretty_print()
#for qid, qtype in codebook.questions.items():
#    print(qid, qtype)
#import ipdb; ipdb.set_trace()


def get_label_info(q, prelabel, question_text, print_it=False, wrong_arg=None):
    choices = q.scale.get_choices()
    if wrong_arg is None:
        if hasattr(q.scale, 'get_values'):
            codes = q.scale.get_values()
        else:
            codes = range(1, len(choices) + 1)

        lst = []
        for choice, code in zip(choices, codes):
            label = prelabel + '_' + str(code)
            lst.append((label, choice, question_text, wrong_arg))
    else:
        codes = range(1, len(choices)+1)
        lst = []
        for choice, code in zip(choices, codes):
            label = prelabel + '_' + str(code)
            lst.append((label, question_text, wrong_arg, choice))

    if print_it:
        for label, option_, choice, x in lst:
            print(label, option_, choice, x)
    return lst

def _pprint(q):
    from surveyhelper.question import SelectMultipleMatrixQuestion, SelectMultipleQuestion, SelectOneMatrixQuestion, SelectOneQuestion
    res = []
    label = q.label
    print("\n\n### {} ###".format(label))
    print(q.text)
    print()
    if isinstance(q, SelectMultipleMatrixQuestion):
        for ix, subquestion in enumerate(q.questions):
            question_text = subquestion.text
            _res = get_label_info(subquestion, subquestion.label,
                                      question_text, wrong_arg=q.text)
            res += _res
            print()
    elif isinstance(q, SelectOneMatrixQuestion):
        for ix, subquestion in enumerate(q.questions):
            question_text = subquestion.text
            _res = get_label_info(subquestion, label + "_{}".format(ix + 1),
                                  question_text, wrong_arg=q.text)
            res += _res
            print()
    elif isinstance(q, SelectOneQuestion):
        question_text = q.text
        res = get_label_info(q, label, question_text)
    elif isinstance(q, SelectMultipleQuestion):
        question_text = q.text
        res = get_label_info(q, label, question_text)
    else:
        raise ValueError('Error!')

    return res

def pprint(cb):
    res = []
    for qid, qob in cb.items():
        res += _pprint(qob)
    #print(res)
    print(len(res))
    import pandas as pd
    df = pd.DataFrame(res, columns=['code', 'option', 'question', 'suffix'])
    df['category'] = None
    import ipdb; ipdb.set_trace()
    df.to_csv('tvstudy_labels_by_daniel.csv')

pprint(codebook.questions)