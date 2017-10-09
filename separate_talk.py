#! /usr/bin/env python3


def get_sibling_directory_path(sibling_directory_name):
    '''
    returns path for a specified folder that is in the same parent directory as
        the current working directory
    '''

    import os

    current_path = os.getcwd()
    last_separator_position = current_path.rfind(os.sep)
    parent_directory_path = current_path[0:last_separator_position]
    sibling_directory_path = os.path.join(parent_directory_path,
                                          sibling_directory_name)
    return(sibling_directory_path)


def print_full(x):
    '''
    Taken from:
    https://stackoverflow.com/questions/19124601/is-there-a-way-to-pretty-print-the-entire-pandas-series-dataframe/19126566
    '''

    import pandas as pd

    pd.set_option('display.max_rows', len(x))
    print(x)
    pd.reset_option('display.max_rows')


def print_intermittent_status_message_in_loop(iteration, every_xth_iteration,
                                              total_iterations):
    '''
    Prints message updating loop's progress for user
    '''

    if iteration % every_xth_iteration == 0:
        print('Processing file {0} of {1}, which is {2:.0f}%'
              .format(iteration + 1, total_iterations,
                      100 * (iteration + 1) / total_iterations))


def read_table(table_filepath, column_of_lists):
    '''
    reads table from 'csv' file
    each item in column 'column_of_lists' is read as a list; as currently
        written, the function can read only 1 column as a list
    '''

    import pandas as pd
    from ast import literal_eval

    # '^' used as separator because it does not appear in any text descriptions
    table = pd.read_csv(table_filepath, sep='^',
                        converters={column_of_lists[0]: literal_eval,
                                    column_of_lists[1]: literal_eval,
                                    column_of_lists[2]: literal_eval})

    return(table)


def read_text_file(text_filename, as_string=False):
    '''
    reads each line in a text file as a list item and returns list by default
    if 'as_string' is 'True', reads entire text file as a single string
    '''

    text_list = []

    try:
        with open(text_filename) as text:
            if as_string:
                # reads text file as single string
                text_list = text.read().replace('\n', '')
            else:
                # reads each line of text file as item in a list
                for line in text:
                    text_list.append(line.rstrip('\n'))
            text.close()
        return(text_list)

    except:
        return('There was an error while trying to read the file')


def write_list_to_text_file(a_list, text_file_name, overwrite_or_append='a'):
    '''
    writes a list of strings to a text file
    appends by default; change to overwriting by setting to 'w' instead of 'a'
    '''
    try:
        textfile = open(text_file_name, overwrite_or_append, encoding='utf-8')
        for element in a_list:
            textfile.write(element)
            textfile.write('\n')
    finally:
        textfile.close()


def expand_table(table):
    '''
    In the original table/dataframe, several columns contain lists, all of which
        have an equal number of elements.  This function expands the table
        vertically (i.e., by number of rows) so that each list element is in its
        own row.
    In this case, the table as 8 columns and column indices 3, 4, and 7 contain
        lists as elements.
    '''

    import pandas as pd

    row = []

    for i in range(len(table)):

        for j in range(0, len(table.iloc[i, 3])):

            row.append([table.iloc[i, 0],
                        table.iloc[i, 1],
                        table.iloc[i, 2],
                        table.iloc[i, 3][j],
                        table.iloc[i, 4][j],
                        table.iloc[i, 5],
                        table.iloc[i, 6],
                        table.iloc[i, 7][j]])

    expanded_table = pd.DataFrame(row, columns=table.columns)

    return(expanded_table)


def find_substring_idx(a_string, substring):
    '''
    returns starting and ending indices for a substring in 'a_string'
    if substring is empty (i.e., ''), returns lists of digits from zero to the
        length of 'a_string'
    '''

    import re

    start_idx = [s.start() for s in re.finditer(substring, a_string)]
    #end_idx = [e + len(substring) for e in start_idx]
    # don't need 'end_idx' for this project
    #return(start_idx, end_idx)

    return(start_idx)


def quotes_n_by_panel(expanded_table):
    '''
    The 'no_quotes_n' and 'odd_quotes_n' variables in the original table gave
        an overall sum of the number of panels with no double-quotes or an odd
        number of quotes, respectively, since each row in the original table
        represented a single comic.  In the expanded table, each row represents
        a single panel within a comic.  This function adjusts these two quotes
        variables so that each row's value represents only that row/panel,
        instead of the entire comic.
    '''

    message_interval = 1000
    loop_len = len(expanded_table)
    quotes_ns = []

    for i in range(loop_len):

        print_intermittent_status_message_in_loop(i, message_interval, loop_len)

        a_string = expanded_table.ix[i, 'text_spell_corrected']
        quotes_idx = find_substring_idx(a_string, '"')
        quotes_n = len(quotes_idx)
        quotes_ns.append(quotes_n)

        if quotes_n == 0:               # if there are no double quotes
            expanded_table.ix[i, 'no_quotes_n'] = 1
        else:
            expanded_table.ix[i, 'no_quotes_n'] = 0

        if (quotes_n % 2) != 0:       # if there is an odd number of double quotes
            expanded_table.ix[i, 'odd_quotes_n'] = 1
        else:
            expanded_table.ix[i, 'odd_quotes_n'] = 0

    expanded_table['quotes_n'] = quotes_ns
    expanded_table.rename(columns={'no_quotes_n': 'no_quotes',
                                   'odd_quotes_n': 'odd_quotes'}, inplace=True)
    expanded_table = expanded_table.iloc[:, [0, 1, 2, 3, 4, 8, 5, 6, 7]]

    return(expanded_table)


def separate_talk(strings, quotes_idx):
    '''
    Divides each string in 'strings' into lists of 'talk' and 'nontalk'
    'Talk' substrings are quotes, that is, substrings that are enclosed in
        double-quotes; 'non-talk' is anything else in the string
    Inputs:  'strings' is a Pandas Series of strings;
             'quotes_idx' is a Pandas Series with the same length as 'strings';
                each element is composed of one or more lists, with one list for
                each occurrence of a 'talk' substring in the corresponding
                string; each list includes the positions of the starting and
                ending double quotes for the 'talk' substring; if there is no
                'talk' substring in the string, the element contains one empty
                list
    Outputs: lists of 'talk' and 'nontalk', each the same length as 'strings',
        containing quoted and non-quoted (respectively) substrings of each
        string in 'strings'; if there are multiple substrings in an element of
        'talk' (or 'nontalk'), each substring is a separate element in a list
    '''

    nontalk = []
    talk = []
    message_interval = 1000
    loop_len = len(strings)

    # for each panel
    for i in range(loop_len):

        print_intermittent_status_message_in_loop(i, message_interval, loop_len)
        panel_nontalk = []
        panel_talk = []

        # if there's no information on the positions of double quotes
        if not quotes_idx[i]:
            panel_nontalk.append([])
            panel_talk.append([])

        else:

            # for each occurrence of a 'talk' substring within a panel
            for j in range(len(quotes_idx[i])):

                string = strings[i]
                start_quote_pos = quotes_idx[i][j][1]
                end_quote_pos = quotes_idx[i][j][2]

                # if this is the first 'talk' substring
                if j == 0:
                    panel_nontalk.append(string[0:start_quote_pos].strip())

                # else (if this is not the first 'talk' substring)
                else:
                    prior_end_quote_pos = quotes_idx[i][j-1][2]
                    panel_nontalk.append(string[prior_end_quote_pos:start_quote_pos].strip())

                # append the 'talk' substring
                panel_talk.append(string[start_quote_pos+1:end_quote_pos].strip())

            # after all 'talk' substrings have been added, if there's still a
            # substring remaining at the end
            if end_quote_pos < len(string) - 1:
                # append it as a 'nontalk' substring
                panel_nontalk.append(string[end_quote_pos+1:len(string)].strip())

        nontalk.append(panel_nontalk)
        talk.append(panel_talk)

    return(nontalk, talk)


def main():
    '''
    Expands table of comic descriptions so that each row represents a panel in
        a comic instead of the entire comic (i.e., a comic with 4 panels is
        represented by 4 rows instead of 1 row)
    Also adds columns to table that divides the descriptions into speech (or
        thought) and non-speech (columns labeled 'text_talk and 'text_nontalk');
        speech was identified by enclosure by double quotes
    '''

    import os

    table_folder = '06_character_talk'
    table_file = 'table.csv'
    source_path = get_sibling_directory_path(table_folder)
    table_filepath = os.path.join(source_path, table_file)

    text_col_names = ['text_by_panels',
                      'text_spell_corrected',
                      'comics_speakers']
    table = read_table(table_filepath, text_col_names)
    table.to_csv('table.csv', sep='^', index=False)
    expanded_table = expand_table(table)
    expanded_table = quotes_n_by_panel(expanded_table)
    expanded_table.to_csv('expanded_table.csv', sep='^', index=False)

    nontalk, talk = separate_talk(expanded_table.loc[:, 'text_spell_corrected'],
                                  expanded_table.loc[:, 'comics_speakers'])

    expanded_table['text_nontalk'] = nontalk
    expanded_table['text_talk'] = talk

    expanded_table.to_csv('expanded_table.csv', sep='^', index=False)


if __name__ == '__main__':
    main()
