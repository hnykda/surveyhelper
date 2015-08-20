import pandas as pd
import numpy as np

class ResponseSet:

    # TODO - As currently written this code skips the second row of data,
    # because that's what we want to do for Qualtrics csv results, but this is
    # potentially a big gotcha, so document well or change.
    def __init__(self, response_file, codebook, 
                 skiprows = [1], 
                 encoding="utf8",
                 grouping_var=None,
                 group_dict=None):
        df = pd.read_csv(response_file , skiprows=skiprows, encoding=encoding)
        # go through each variable in the codebook and make sure the corresponding 
        # column is integer coded
        matched_questions = []
        for q in codebook.get_questions():
            matched = True
            for v in q.get_variable_names():
                if v not in df:
                    print("Warning: Expected variable {} not found in data file {}".format(v, response_file))
                    matched = False
                elif df[v].dtype not in [np.int64, np.float64]:
                    print("Converting variable {} to integer from {}".format(v, df[v].dtype))
                    df[v] = df[v].convert_objects(convert_numeric=True)
            if matched: matched_questions.append(q)
        self.data = df
        self.matched_questions = matched_questions
        self.codebook = codebook
        self.grouping_var = grouping_var
        self.group_dict = group_dict

    def get_data(self):
        if (not self.grouping_var and self.group_dict):
            raise(Exception(
                  "Grouping variable must also be specified when a grouping dict is passed in."
                 ))
        if (self.grouping_var and not self.group_dict):
            raise(Exception(
                  "Grouping dict must also be specified when a grouping variable is passed in."
                 ))

        if not self.grouping_var or (self.group_dict and self.grouping_var):
            group_var = 'z'
            while group_var in self.data.columns:
                group_var += 'z'
            if not self.grouping_var:
                self.data[group_var] = 0
            else:
                # Create a special variable to sort the data by so that groups
                # end up in correct order
                sort_var = group_var + "z"
                while sort_var in self.data.columns:
                    sort_var += 'z'
                value_order = list(self.group_dict.keys())
                asc = list(range(0,len(value_order)))
                self.data[sort_var] = self.data[self.grouping_var].replace(
                                      value_order, asc)
                self.data.sort(sort_var, inplace=True)
                # Then replace with labels
                self.data[group_var] = self.data[self.grouping_var].replace(
                                       self.group_dict)

        else:
            group_var = self.grouping_var
        groups = self.data.groupby(group_var, sort=False)
        return(groups)
        
