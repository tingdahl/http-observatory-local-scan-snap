#!/usr/bin/env python3

import httpobs.scanner.local

import argparse
import json

from operator import itemgetter
from urllib.parse import urlparse

NO_MIN_GRADE = ''
NO_MIN_SCORE = 0
GRADES = ['F', 'D-', 'D', 'D+', 'C-', 'C', 'C+', 'B-', 'B', 'B+', 'A-', 'A', 'A+']

#
# All keys used more than once
FORMAT_JSON_KEY = 'json'
FORMAT_REPORT_KEY = 'report'
RESULT_SCAN_KEY = 'scan'
RESULT_ERROR_KEY = 'error'


def main():

    parser = argparse.ArgumentParser()

    # Add the various arguments
    parser.add_argument('--http-port',
                        default=80,
                        help='port to use for the HTTP scan (instead of 80)',
                        type=int)
    parser.add_argument('--https-port',
                        default=443,
                        help='port to use for the HTTPS scan (instead of 443)',
                        type=int)
    parser.add_argument('--path',
                        default=argparse.SUPPRESS,
                        help='path to scan, instead of /',
                        type=str)
    parser.add_argument('--no-verify',
                        action='store_true',
                        help='disable certificate verification in the HSTS/HPKP tests')
    parser.add_argument('--cookies',
                        default=argparse.SUPPRESS,
                        help='cookies to send in scan (json formatted)',
                        type=json.loads)
    parser.add_argument('--headers',
                        default=argparse.SUPPRESS,
                        help='headers to send in scan (json formatted)',
                        type=json.loads)
    parser.add_argument('--min-grade',
                        default=NO_MIN_GRADE,
                        help='testing: this grade or better, or exit(1)',
                        choices=GRADES,
                        type=str)
    parser.add_argument('--min-score',
                        default=NO_MIN_SCORE,
                        help='testing: this score or better (>=0), or exit(1)',
                        type=int)
    parser.add_argument('--format',
                        default=FORMAT_JSON_KEY,
                        help='output format (json or report), default of json',
                        type=str)
    parser.add_argument('hostname',
                        help='host to scan (hostname only, no protocol or port)',
                        type=str)

    args = vars(parser.parse_args())

    # Remove the -- from the name, change - to underscore
    args = {k.split('--')[-1].replace('-', '_'): v for k, v in args.items()}
    output_format = args.pop('format').lower()

    # Get minimum grade and score
    min_grade = args.pop('min_grade')
    min_score = args.pop('min_score')

    # print out help if no arguments are specified, or bad arguments
    if len(args) == 0 or output_format not in ('json', 'report') or min_score < NO_MIN_SCORE:
        parser.print_help()
        parser.exit(-1)

    # port can't be appended to hostname because we need both HTTP and HTTPS ports.
    # protocol can't be prefixed either, as we scan both of those ports.
    #
    # use urlparse to ensure that neither of these are present in the hostname.
    if urlparse(args['hostname']).scheme or urlparse('http://' + args['hostname']).port:
        parser.print_help()
        parser.exit(-1)

    # Because it makes sense this way
    if args['http_port'] == 80:
        del (args['http_port'])

    if args['https_port'] == 443:
        del (args['https_port'])

    if args.pop('no_verify'):
        args['verify'] = False

    # Get the scan results
    r = httpobs.scanner.local.scan(**args)

    if RESULT_SCAN_KEY not in r.keys():
        if output_format == FORMAT_JSON_KEY:
            print(json.dumps(r, indent=4, sort_keys=True))
        elif output_format == FORMAT_REPORT_KEY and RESULT_ERROR_KEY in r.keys():
            print(f'Error: {r[RESULT_ERROR_KEY]}')
        else:
            print('Unknown error')

        exit(1)

    # Setup thresholding variables
    score_thresholding_text = ''
    grade_thresholding_text = ''
    thresholding_results = {}
    thresholding_passed = True

    grade = r[RESULT_SCAN_KEY]['grade']
    score = r[RESULT_SCAN_KEY]['score']

    # Compare score to threshold
    if min_score > NO_MIN_SCORE:
        thresholding_results['min-score'] = min_score

        score_thresholding_passed = score >= min_score

        if score_thresholding_passed:
            score_thresholding_text = f'Score thresholding passed as score ({score}) is higher or equal to min-score ({min_score})'
        else:
            score_thresholding_text = f'Score thresholding failed as score ({score}) is lower than the minimum score ({min_score})'
            thresholding_passed = False

        thresholding_results['score-test-text'] = score_thresholding_text
        thresholding_results['score-test-passed'] = score_thresholding_passed

    # Compare grade to threshold
    if min_grade != NO_MIN_GRADE:
        thresholding_results['min-grade'] = min_grade
        grade_index = GRADES.index(grade)
        min_grade_index = GRADES.index(min_grade)
        grade_thresholding_passed = grade_index >= min_grade_index

        if grade_thresholding_passed:
            grade_thresholding_text = \
                f'Grade thresholding passed as grade ({grade}) is higher or equal to min-grade ({min_grade})'
        else:
            grade_thresholding_text = \
                f'Grade thresholding failed as grade ({grade}) is lower than the minimum grade ({min_grade})'
            thresholding_passed = False

        thresholding_results['grade-test-text'] = grade_thresholding_text
        thresholding_results['grade-test-passed'] = grade_thresholding_passed
    #
    # Integrate the results
    if len(thresholding_results):
        thresholding_results['passed'] = thresholding_passed
        r['thresholding-results'] = thresholding_results

    # print out the results to the command line
    if output_format == 'json':
        print(json.dumps(r, indent=4, sort_keys=True))
    elif output_format == 'report':
        print('Score: {0} [{1}]'.format(score, grade))

        if len(score_thresholding_text):
            print(f'Score threshold: {score_thresholding_text}')

        if len(grade_thresholding_text):
            print(f'Grade threshold: {grade_thresholding_text}')

        print('Modifiers:')

        # Get all the scores by test name
        scores = [[k.replace('-', ' ').title(), v['score_modifier'], v['score_description']]
                  for k, v in r['tests'].items()]
        scores = sorted(scores, key=itemgetter(0))  # [('test1', -5, 'foo'), ('test2', -10, 'bar')]

        for score in scores:
            if score[1] > 0:
                score[1] = '+' + str(score[1])  # display 5 as +5
            print('  {test:<30} [{modifier:>3}]  {reason}'.format(test=score[0],
                                                                  modifier=score[1],
                                                                  reason=score[2]))

    if thresholding_passed is False:
        exit(1)


if __name__ == "__main__":
    main()
